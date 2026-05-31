import os
import subprocess
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import UploadFile
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY in backend/.env")

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
AUDIO_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def save_uploaded_video(video: UploadFile) -> tuple[str, Path]:
    """
    Saves the uploaded video file into backend/uploads.
    Returns the job_id and saved video path.
    """
    job_id = str(uuid.uuid4())
    video_extension = Path(video.filename or "").suffix or ".mp4"
    video_path = UPLOAD_DIR / f"{job_id}{video_extension}"

    with video_path.open("wb") as buffer:
        buffer.write(video.file.read())

    return job_id, video_path


def extract_audio_from_video(video_path: Path, job_id: str) -> Path:
    """
    Uses FFmpeg to extract MP3 audio from the saved video.
    Returns the path to the extracted audio file.
    """
    audio_path = AUDIO_DIR / f"{job_id}.mp3"

    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "mp3",
            str(audio_path),
        ]
    )

    return audio_path


def speech_to_text_with_elevenlabs(audio_path: Path) -> str:
    """
    Sends the extracted MP3 audio to ElevenLabs Speech-to-Text.
    Returns the transcript text.
    """
    with audio_path.open("rb") as audio_file:
        transcription = elevenlabs_client.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",
        )

    return transcription.text


def video_to_transcript(video: UploadFile) -> dict:
    """
    Full mini-pipeline:
    uploaded video -> saved video -> extracted audio -> transcript
    """
    job_id, video_path = save_uploaded_video(video)
    audio_path = extract_audio_from_video(video_path, job_id)
    transcript = speech_to_text_with_elevenlabs(audio_path)

    return {
        "job_id": job_id,
        "video_file": video_path.name,
        "audio_file": audio_path.name,
        "video_path": str(video_path),
        "audio_path": str(audio_path),
        "transcript": transcript,
    }