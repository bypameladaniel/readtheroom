import os
import uuid
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from controllers.questions_controller import router as questions_router

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.include_router(questions_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
FRAME_DIR = BASE_DIR / "frames"

UPLOAD_DIR.mkdir(exist_ok=True)
FRAME_DIR.mkdir(exist_ok=True)


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def extract_audio(video_path: Path, audio_path: Path) -> None:
    run_command([
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "mp3",
        str(audio_path)
    ])


def sample_frames(video_path: Path, output_folder: Path) -> list[Path]:
    output_folder.mkdir(exist_ok=True)

    # One frame every 5 seconds. Good enough for hackathon body-language analysis.
    output_pattern = output_folder / "frame_%03d.jpg"

    run_command([
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", "fps=1/5",
        str(output_pattern)
    ])

    return sorted(output_folder.glob("*.jpg"))[:8]


def transcribe_audio(audio_path: Path) -> str:
    with audio_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return transcription.text


def analyze_answer(question: str, role: str, transcript: str) -> dict:
    prompt = f"""
You are an interview coach.

Interview question:
{question}

Target role:
{role or "General job interview"}

Candidate answer transcript:
{transcript}

Return a JSON object with:
- confidence_score: number from 0 to 100
- clarity_score: number from 0 to 100
- conciseness_score: number from 0 to 100
- relevance_score: number from 0 to 100
- filler_words: list of common filler words noticed
- star_method: object with situation, task, action, result each as "missing", "weak", or "strong"
- strengths: list of 3 strings
- improvements: list of 5 specific coaching tips
- rewritten_answer: a stronger version of the answer
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return {
        "raw_analysis": response.output_text
    }


@app.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    question: str = Form(...),
    role: str = Form("")
):
    job_id = str(uuid.uuid4())

    video_path = UPLOAD_DIR / f"{job_id}_{video.filename}"
    audio_path = UPLOAD_DIR / f"{job_id}.mp3"
    job_frame_dir = FRAME_DIR / job_id

    with video_path.open("wb") as buffer:
        buffer.write(await video.read())

    extract_audio(video_path, audio_path)
    transcript = transcribe_audio(audio_path)
    frames = sample_frames(video_path, job_frame_dir)

    analysis = analyze_answer(question, role, transcript)

    return {
        "job_id": job_id,
        "question": question,
        "role": role,
        "transcript": transcript,
        "frame_count": len(frames),
        "analysis": analysis
    }


@app.get("/")
def health_check():
    return {"status": "ReadTheRoom backend running"}