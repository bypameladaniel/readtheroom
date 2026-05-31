import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

if not ELEVENLABS_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY in backend/.env")

if not DEFAULT_VOICE_ID:
    raise RuntimeError("Missing ELEVENLABS_VOICE_ID in backend/.env")

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


def text_to_speech_with_elevenlabs(
    text: str,
    voice_id: str = DEFAULT_VOICE_ID,
    output_path: Path | None = None,
    model_id: str = "eleven_multilingual_v2",
) -> Path:
    """
    Sends text to ElevenLabs and saves the generated speech as an MP3 file.
    Returns the saved audio path.
    """
    if not text.strip():
        raise ValueError("text must not be empty")

    if not voice_id.strip():
        raise ValueError("voice_id must not be empty")

    audio_path = output_path or OUTPUT_DIR / f"{uuid.uuid4()}.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    audio_stream = elevenlabs_client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_44100_128",
        text=text,
        model_id=model_id,
    )

    with audio_path.open("wb") as audio_file:
        for chunk in audio_stream:
            audio_file.write(chunk)

    return audio_path