import re
import subprocess
from pathlib import Path


FILLER_WORDS = [
    "um",
    "uh",
    "erm",
    "like",
    "you know",
    "i mean",
    "basically",
    "actually",
    "kind of",
    "sort of",
    "literally",
    "maybe",
]

HEDGING_PHRASES = [
    "i think",
    "i guess",
    "maybe",
    "kind of",
    "sort of",
    "i feel like",
    "probably",
    "hopefully",
]

BUZZWORDS = [
    "synergy",
    "passionate",
    "hard worker",
    "team player",
    "go-getter",
    "detail-oriented",
    "fast learner",
]


def get_audio_duration_seconds(audio_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return float(result.stdout.strip())


def count_words(transcript: str) -> int:
    words = re.findall(r"\b[\w']+\b", transcript.lower())
    return len(words)


def count_phrases(transcript: str, phrases: list[str]) -> dict:
    text = transcript.lower()
    counts = {}

    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        matches = re.findall(pattern, text)

        if matches:
            counts[phrase] = len(matches)

    return {
        "total": sum(counts.values()),
        "breakdown": counts,
    }


def detect_long_pauses(audio_path: Path, min_silence_duration: float = 2.0) -> dict:
    command = [
        "ffmpeg",
        "-i",
        str(audio_path),
        "-af",
        f"silencedetect=noise=-35dB:d={min_silence_duration}",
        "-f",
        "null",
        "-",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    stderr = result.stderr

    starts = re.findall(r"silence_start: ([0-9.]+)", stderr)
    ends = re.findall(r"silence_end: ([0-9.]+)", stderr)

    pauses = []

    for start, end in zip(starts, ends):
        start_float = float(start)
        end_float = float(end)

        pauses.append(
            {
                "start": round(start_float, 2),
                "end": round(end_float, 2),
                "duration": round(end_float - start_float, 2),
            }
        )

    return {
        "count": len(pauses),
        "pauses": pauses,
    }


def get_pace_label(words_per_minute: int) -> str:
    if words_per_minute < 110:
        return "Too slow"
    if words_per_minute <= 160:
        return "Good pace"
    return "Too fast"


def get_filler_label(filler_count: int) -> str:
    if filler_count <= 3:
        return "Low"
    if filler_count <= 10:
        return "Moderate"
    return "Too many"


def detect_star_signals(transcript: str) -> dict:
    text = transcript.lower()

    situation_words = [
        "when",
        "during",
        "at my previous",
        "in my role",
        "there was a time",
    ]

    task_words = [
        "needed to",
        "responsible for",
        "my goal",
        "the challenge",
        "had to",
    ]

    action_words = [
        "i did",
        "i created",
        "i built",
        "i led",
        "i organized",
        "i solved",
        "i reorganized",
    ]

    result_words = [
        "as a result",
        "resulted",
        "we achieved",
        "improved",
        "increased",
        "decreased",
        "successfully",
        "received",
    ]

    return {
        "situation": "strong" if any(x in text for x in situation_words) else "missing",
        "task": "strong" if any(x in text for x in task_words) else "missing",
        "action": "strong" if any(x in text for x in action_words) else "missing",
        "result": "strong" if any(x in text for x in result_words) else "missing",
    }


def score_confidence(
    words_per_minute: int,
    filler_count: int,
    hedge_count: int,
    long_pause_count: int,
) -> int:
    score = 100

    if words_per_minute < 110:
        score -= 12
    elif words_per_minute > 170:
        score -= 12

    score -= min(filler_count * 2, 30)
    score -= min(hedge_count * 3, 20)
    score -= min(long_pause_count * 5, 25)

    return max(0, min(100, score))


def score_clarity(transcript: str, filler_count: int, star_signals: dict) -> int:
    score = 100
    word_count = count_words(transcript)

    sentences = re.split(r"[.!?]+", transcript)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    if sentences:
        avg_sentence_length = word_count / len(sentences)

        if avg_sentence_length > 28:
            score -= 20
        elif avg_sentence_length > 20:
            score -= 10

    score -= min(filler_count, 20)

    missing_star_parts = list(star_signals.values()).count("missing")
    score -= missing_star_parts * 8

    return max(0, min(100, score))


def score_conciseness(
    transcript: str,
    duration_seconds: float,
    words_per_minute: int,
) -> int:
    score = 100
    word_count = count_words(transcript)

    if duration_seconds > 150:
        score -= 30
    elif duration_seconds > 90:
        score -= 15

    if word_count > 280:
        score -= 25
    elif word_count > 180:
        score -= 10

    repeated_phrases = [
        "i think",
        "i feel like",
        "you know",
        "basically",
        "kind of",
        "sort of",
    ]

    repetition_count = sum(
        transcript.lower().count(phrase) for phrase in repeated_phrases
    )

    score -= min(repetition_count * 4, 20)

    if words_per_minute > 180:
        score -= 10

    return max(0, min(100, score))


def detect_upspeak_heuristic(transcript: str) -> dict:
    question_marks = transcript.count("?")

    return {
        "possible_upspeak_count": question_marks,
        "label": "Possible upspeak detected"
        if question_marks >= 2
        else "No major upspeak signal",
    }


def analyze_audio_metrics(audio_path: Path, transcript: str) -> dict:
    duration_seconds = get_audio_duration_seconds(audio_path)
    word_count = count_words(transcript)

    duration_minutes = duration_seconds / 60 if duration_seconds > 0 else 1
    words_per_minute = round(word_count / duration_minutes)

    filler_data = count_phrases(transcript, FILLER_WORDS)
    hedge_data = count_phrases(transcript, HEDGING_PHRASES)
    buzzword_data = count_phrases(transcript, BUZZWORDS)
    pause_data = detect_long_pauses(audio_path)
    star_signals = detect_star_signals(transcript)
    upspeak_data = detect_upspeak_heuristic(transcript)

    filler_count = filler_data["total"]
    hedge_count = hedge_data["total"]
    long_pause_count = pause_data["count"]

    confidence_score = score_confidence(
        words_per_minute=words_per_minute,
        filler_count=filler_count,
        hedge_count=hedge_count,
        long_pause_count=long_pause_count,
    )

    clarity_score = score_clarity(
        transcript=transcript,
        filler_count=filler_count,
        star_signals=star_signals,
    )

    conciseness_score = score_conciseness(
        transcript=transcript,
        duration_seconds=duration_seconds,
        words_per_minute=words_per_minute,
    )

    return {
        "confidence_score": confidence_score,
        "clarity_score": clarity_score,
        "conciseness_score": conciseness_score,
        "words_per_minute": words_per_minute,
        "pace_label": get_pace_label(words_per_minute),
        "filler_words": filler_count,
        "filler_label": get_filler_label(filler_count),
        "filler_breakdown": filler_data["breakdown"],
        "hedging_count": hedge_count,
        "hedging_breakdown": hedge_data["breakdown"],
        "long_pauses": long_pause_count,
        "pause_label": f"{long_pause_count} pauses of 2+ seconds",
        "pause_map": pause_data["pauses"],
        "buzzwords": buzzword_data["total"],
        "buzzword_breakdown": buzzword_data["breakdown"],
        "star_method_detected": star_signals,
        "upspeak_signal": upspeak_data,
        "duration_seconds": round(duration_seconds, 2),
        "word_count": word_count,
    }