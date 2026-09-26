import logging

logger = logging.getLogger("PosturaX.StateMachine")


class PostureStateMachine:
    def __init__(self, fps: float = 2.0, recovery_threshold_sec: float = 5.0):
        self.fps = fps
        self.slouch_counter = 0
        self.good_posture_counter = 0
        
        # 5 seconds grace period = 10 frames at 2 Hz
        self.recovery_frames_required = int(recovery_threshold_sec * fps)
        
        self.overlay_triggered = False
        self.first_warning_sent = False
        self.second_warning_sent = False

    def process_frame(self, posture_status: str) -> dict:
        action = "NONE"

        if posture_status == "FORWARD_SLOUCHING":
            # Slouching again: reset good posture streak
            self.good_posture_counter = 0
            self.slouch_counter += 1

        else:  # GOOD_POSTURE
            self.good_posture_counter += 1

            # SCENARIO 1: Sits straight for MORE THAN 5 seconds -> Full Reset
            if self.good_posture_counter >= self.recovery_frames_required:
                if self.slouch_counter > 0:
                    logger.info("Sustained good posture for > 5s. Slouch timer fully reset!")
                
                self.slouch_counter = 0
                self.first_warning_sent = False
                self.second_warning_sent = False
                
                if self.overlay_triggered:
                    self.overlay_triggered = False
                    action = "DISMISS_OVERLAY"

            # SCENARIO 2: Sits straight for LESS THAN 5 seconds -> Timer PAUSED / Retained
            else:
                logger.debug(f"Good posture detected ({self.good_posture_counter/self.fps}s). Timer held.")

        slouch_seconds = self.slouch_counter / self.fps

        # -------------------------------------------------------------------
        # TIMED ACTION TRIGGERS
        # -------------------------------------------------------------------
        if action == "NONE":
            # 30 Seconds Slouch (60 frames)
            if self.slouch_counter >= int(30 * self.fps) and not self.first_warning_sent:
                self.first_warning_sent = True
                action = "TRIGGER_FIRST_WARNING"

            # 60 Seconds Slouch (120 frames)
            elif self.slouch_counter >= int(60 * self.fps) and not self.second_warning_sent:
                self.second_warning_sent = True
                action = "TRIGGER_SECOND_WARNING"

            # 90 Seconds Slouch (180 frames)
            elif self.slouch_counter >= int(90 * self.fps) and not self.overlay_triggered:
                self.overlay_triggered = True
                action = "TRIGGER_SCREEN_BLUR"

        return {
            "action": action,
            "slouch_time": slouch_seconds,
            "good_posture_streak": self.good_posture_counter / self.fps
        }
