import json
from dataclasses import dataclass, asdict

class _FloatEncoder(json.JSONEncoder):
    """Converts numpy float32/float64 to plain Python float."""
    def default(self, obj):
        if hasattr(obj, "item"):  # catches np.float32, np.float64, np.int64, etc.
            return obj.item()
        return super().default(obj)
 
@dataclass
class FrameResult:
    timestamp_sec: float
    frame_index: int
    dominant_emotion: str
    emotions: dict          # all 7 emotion scores (0–100)
    face_detected: bool