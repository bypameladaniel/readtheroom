from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from gemini_client import analyze_answer
from media_pipeline import video_to_transcript
from audio_analysis import analyze_audio_metrics

app = FastAPI(title="ReadTheRoom API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "ReadTheRoom backend is running"}


@app.post("/analyze-interview")
def analyze_interview(video: UploadFile = File(...), question: str = Form(...), role: str = Form("General job interview")):
    transcript_data = video_to_transcript(video)
    return analyze_answer(
        question=question,
        transcript=transcript_data["transcript"],
        role=role,
    )


@app.post("/audio-metrics")
def get_audio_metrics(video: UploadFile = File(...)):
    """Extract audio metrics from a video without LLM analysis"""
    try:
        transcript_data = video_to_transcript(video)
        audio_path = Path(transcript_data["audio_path"])
        transcript = transcript_data["transcript"]
        
        metrics = analyze_audio_metrics(
            audio_path=audio_path,
            transcript=transcript,
        )
        
        return {
            "status": "success",
            "job_id": transcript_data["job_id"],
            "transcript": transcript,
            "metrics": metrics,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }