import cv2
import json
import time
from deepface import DeepFace
from dataclasses import dataclass, asdict
from typing import Optional
from expressions_analysis.helper import _FloatEncoder, FrameResult

EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
 
# Emotions that signal nervousness/discomfort in an interview context
NEGATIVE_EMOTIONS = {"angry", "disgust", "fear", "sad"}
POSITIVE_EMOTIONS = {"happy", "surprise"}
 
@dataclass
class ThirdSummary:
    label: str                    # "opening", "middle", "closing"
    start_sec: float
    end_sec: float
    dominant_emotion: str
    emotion_pct: dict             # % breakdown for this segment
    negative_pct: float           # combined negative emotion %
    smile_pct: float              # happy %
 
 
@dataclass
class AggregatedResult:
    total_frames_detected: int
    duration_sec: float
 
    # Overall emotion breakdown (% of frames)
    emotion_pct: dict
 
    # Positive / negative / neutral splits (% of frames)
    positive_pct: float
    negative_pct: float
    neutral_pct: float
 
    # Smile and composure
    smile_pct: float              # % frames where happy is dominant
    expression_variability: float # number of distinct emotions
 
    # Video split into thirds
    thirds: list[ThirdSummary]
 
    # Flagged segments: timestamps where negative emotion was sustained
    flagged_segments: list[dict]  # [{start, end, dominant_emotion}]
 
 
def aggregate(results: list[FrameResult]) -> AggregatedResult:
    """
    Takes raw per-frame results and produces a structured summary
    suitable for passing to Gemini as interview feedback context.
    """
    detected = [r for r in results if r.face_detected]
 
    if not detected:
        raise ValueError("No frames with a detected face — cannot aggregate.")
 
    total      = len(detected)
    duration   = detected[-1].timestamp_sec - detected[0].timestamp_sec
 
    # ── Overall emotion % breakdown ───────────────────────────────────────────
    from collections import Counter
    counts     = Counter(r.dominant_emotion for r in detected)
    emotion_pct = {e: round(100 * counts.get(e, 0) / total, 1) for e in EMOTIONS}
 
    positive_pct = round(sum(emotion_pct[e] for e in POSITIVE_EMOTIONS), 1)
    negative_pct = round(sum(emotion_pct[e] for e in NEGATIVE_EMOTIONS), 1)
    neutral_pct  = round(emotion_pct.get("neutral", 0), 1)
    smile_pct    = round(emotion_pct.get("happy", 0), 1)
 
    # Expression variability: how many distinct emotions appeared > 5% of the time
    active_emotions        = sum(1 for v in emotion_pct.values() if v > 5)
    expression_variability = round(active_emotions / len(EMOTIONS), 2)
 
    # ── Thirds ────────────────────────────────────────────────
    # Separate the video into 3 equal time segments and analyze emotion breakdown in each
    # Helps Gemini understand which parts of the answer had more nervousness, confidence, etc.
    third_size = total // 3
    segments   = [
        ("opening",  detected[:third_size]),
        ("middle",   detected[third_size: 2 * third_size]),
        ("closing",  detected[2 * third_size:]),
    ]
 
    thirds = []
    for label, frames in segments:
        if not frames:
            continue
        seg_counts  = Counter(r.dominant_emotion for r in frames)
        seg_total   = len(frames)
        seg_pct     = {e: round(100 * seg_counts.get(e, 0) / seg_total, 1) for e in EMOTIONS}
        thirds.append(ThirdSummary(
            label            = label,
            start_sec        = frames[0].timestamp_sec,
            end_sec          = frames[-1].timestamp_sec,
            dominant_emotion = seg_counts.most_common(1)[0][0],
            emotion_pct      = seg_pct,
            negative_pct     = round(sum(seg_pct[e] for e in NEGATIVE_EMOTIONS), 1),
            smile_pct        = round(seg_pct.get("happy", 0), 1),
        ))
 
    # ── Flagged segments: runs of negative emotion > 5 consecutive frames ─────
    # Identify any segments of the video where the candidate showed sustained negative emotions
    flagged_segments = []
    run_start        = None
    run_emotion      = None
    run_count        = 0
    MIN_RUN          = 5   # minimum consecutive frames to flag
 
    for r in detected:
        if r.dominant_emotion in NEGATIVE_EMOTIONS:
            if r.dominant_emotion == run_emotion:
                run_count += 1
            else:
                # New negative emotion — reset run
                run_start  = r.timestamp_sec
                run_emotion = r.dominant_emotion
                run_count   = 1
        else:
            if run_count >= MIN_RUN:
                flagged_segments.append({
                    "start_sec":        round(run_start, 1),
                    "end_sec":          round(r.timestamp_sec, 1),
                    "dominant_emotion": run_emotion,
                })
            run_start   = None
            run_emotion = None
            run_count   = 0
 
    # Case where video ends during a negative emotion run
    if run_count >= MIN_RUN:
        flagged_segments.append({
            "start_sec":        round(run_start, 1),
            "end_sec":          round(detected[-1].timestamp_sec, 1),
            "dominant_emotion": run_emotion,
        })
 
    return AggregatedResult(
        total_frames_detected  = total,
        duration_sec           = round(duration, 1),
        emotion_pct            = emotion_pct,
        positive_pct           = positive_pct,
        negative_pct           = negative_pct,
        neutral_pct            = neutral_pct,
        smile_pct              = smile_pct,
        expression_variability = expression_variability,
        thirds                 = thirds,
        flagged_segments       = flagged_segments,
    )
 
 
def print_aggregation(agg: AggregatedResult) -> None:
    """Print the aggregated result as formatted JSON."""
    print(json.dumps(asdict(agg), indent=2, cls=_FloatEncoder))