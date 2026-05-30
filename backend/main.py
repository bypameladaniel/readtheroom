from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.gemini_client import analyze_answer
from media_pipeline import video_to_transcript

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