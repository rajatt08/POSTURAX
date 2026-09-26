import json
import logging
from pathlib import Path
from backend import config

logger = logging.getLogger("PosturaX.Calibrator")


class PostureCalibrator:
    """Manages reading, writing, and computing baseline pitch calibration."""

    def __init__(self, calib_file: Path = config.CALIBRATION_FILE):
        self.calib_file = calib_file
        self.baseline_pitch = 0.0
        self.is_calibrating = False
        self._samples = []
        self.load_calibration()

    def load_calibration(self):
        """Loads baseline pitch from calibration.json file if available."""
        if self.calib_file.exists():
            try:
                with open(self.calib_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.baseline_pitch = float(data.get("baseline_pitch", 0.0))
                    logger.info(f"Loaded calibration baseline pitch: {self.baseline_pitch}°")
            except Exception as e:
                logger.error(f"Error reading calibration file: {e}")
                self.baseline_pitch = 0.0
        else:
            self.baseline_pitch = 0.0

    def save_calibration(self, baseline_pitch: float):
        """Saves new baseline pitch to disk."""
        self.baseline_pitch = round(baseline_pitch, 2)
        try:
            with open(self.calib_file, "w", encoding="utf-8") as f:
                json.dump({"baseline_pitch": self.baseline_pitch}, f, indent=4)
            logger.info(f"Saved new baseline pitch: {self.baseline_pitch}°")
        except Exception as e:
            logger.error(f"Failed to save calibration file: {e}")

    def start_calibration(self):
        """Starts collecting samples to calculate a new baseline pitch."""
        self.is_calibrating = True
        self._samples = []
        logger.info("Started posture calibration process...")

    def add_sample(self, pitch: float) -> dict:
        """Adds a pitch reading to the active calibration sample pool."""
        if not self.is_calibrating:
            return {"status": "NOT_CALIBRATING"}

        self._samples.append(pitch)
        if len(self._samples) >= 30:  # Collect 30 samples (~3s at 10Hz)
            new_baseline = sum(self._samples) / len(self._samples)
            self.save_calibration(new_baseline)
            self.is_calibrating = False
            return {"status": "COMPLETE", "baseline_pitch": self.baseline_pitch}

        return {"status": "IN_PROGRESS", "samples_collected": len(self._samples)}
