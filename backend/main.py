from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/video-to-transcript")
def process_video(video: UploadFile = File(...)):
    return video_to_transcript(video)