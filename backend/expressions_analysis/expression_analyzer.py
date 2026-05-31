import cv2
import json
import time
from deepface import DeepFace
from dataclasses import dataclass, asdict
from typing import Optional
from expressions_analysis.data_aggregation import aggregate, print_aggregation
from expressions_analysis.helper import _FloatEncoder, FrameResult

def extract_and_analyze(
    video_path: str,
    sample_every_n_frames: int = 10,
    verbose: bool = True,
) -> list[FrameResult]:
    """
    Opens an MP4 video, samples every Nth frame, runs DeepFace emotion
    detection on each, and returns a list of FrameResult objects.

    Args:
        video_path:             Path to the .mp4 file.
        sample_every_n_frames:  How often to sample. 10 = every 10th frame
                                (~3 fps for a 30fps video). Lower = more
                                accurate but slower.
        verbose:                Print progress to terminal.

    Returns:
        List of FrameResult, one per sampled frame where a face was detected.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps

    if verbose:
        print(f"\n--- Video info ---")
        print(f"  File          : {video_path}")
        print(f"  FPS           : {fps:.1f}")
        print(f"  Total frames  : {total_frames}")
        print(f"  Duration      : {duration_sec:.1f}s ({duration_sec/60:.1f} min)")
        print(f"  Sampling every: {sample_every_n_frames} frames")
        print(f"  Frames to scan: ~{total_frames // sample_every_n_frames}")
        print(f"------------------\n")

    results: list[FrameResult] = []
    frame_index  = 0
    scanned      = 0
    detected     = 0
    start_time   = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Only process every Nth frame
        if frame_index % sample_every_n_frames == 0:
            timestamp = frame_index / fps
            scanned  += 1

            try:
                analysis = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=True,   # raises exception if no face
                    silent=True,
                )

                # DeepFace returns a list when multiple faces are found;
                # we take the first (most prominent) face.
                face_data = analysis[0] if isinstance(analysis, list) else analysis

                result = FrameResult(
                    timestamp_sec    = round(timestamp, 2),
                    frame_index      = frame_index,
                    dominant_emotion = face_data["dominant_emotion"],
                    emotions         = {k: round(v, 2) for k, v in face_data["emotion"].items()},
                    face_detected    = True,
                )
                results.append(result)
                detected += 1

                if verbose:
                    bar = _progress_bar(frame_index, total_frames)
                    print(f"\r{bar}  {timestamp:.1f}s  {face_data['dominant_emotion']:<10}", end="", flush=True)

            except Exception:
                # No face detected in this frame — record it but skip
                results.append(FrameResult(
                    timestamp_sec    = round(timestamp, 2),
                    frame_index      = frame_index,
                    dominant_emotion = "none",
                    emotions         = {},
                    face_detected    = False,
                ))

        frame_index += 1

    cap.release()
    elapsed = time.time() - start_time

    if verbose:
        print(f"\n\n--- Analysis complete ---")
        print(f"  Frames scanned : {scanned}")
        print(f"  Faces detected : {detected}  ({100*detected/max(scanned,1):.0f}%)")
        print(f"  Time taken     : {elapsed:.1f}s")
        print(f"-------------------------\n")

    return results
 
def print_results(results: list[FrameResult]) -> None:
    """Print all frame results as formatted JSON."""
    print(json.dumps([asdict(r) for r in results], indent=2, cls=_FloatEncoder))

def quick_summary(results: list[FrameResult]) -> None:
    """Print a quick emotion breakdown to the terminal."""
    detected = [r for r in results if r.face_detected]
    if not detected:
        print("No faces detected in any frame.")
        return

    from collections import Counter
    counts   = Counter(r.dominant_emotion for r in detected)
    total    = len(detected)
    duration = detected[-1].timestamp_sec - detected[0].timestamp_sec

    print(f"\n--- Emotion summary ({total} frames, {duration:.0f}s) ---")
    for emotion, count in counts.most_common():
        bar   = "█" * int(30 * count / total)
        pct   = 100 * count / total
        print(f"  {emotion:<10}  {bar:<30}  {pct:5.1f}%")
    print()


# ── Progress bar helper ────────────────────────────────────────────────────────
def _progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / max(total, 1))
    return f"[{'█' * filled}{'░' * (width - filled)}]"
