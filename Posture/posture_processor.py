import logging

logger = logging.getLogger("PosturaX.PostureProcessor")


class PostureProcessor:
    def __init__(self, slouch_threshold: float = 20.0):
        self.slouch_threshold = slouch_threshold

    def process_telemetry(self, packet: dict) -> dict:
        pitch = float(packet.get("pitch", 0.0))

        if pitch >= self.slouch_threshold:
            status = "FORWARD_SLOUCHING"
        else:
            status = "GOOD_POSTURE"

        return {
            "device_id": packet.get("device_id", "UNKNOWN"),
            "pitch": pitch,
            "status": status
        }
