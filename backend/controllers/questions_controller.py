import json
import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from gemini_client import analyze_answer
from media_pipeline import extract_audio_from_video, save_uploaded_video, speech_to_text_with_elevenlabs
from text_to_speech_pipeline import text_to_speech_with_elevenlabs

router = APIRouter(prefix="/questions", tags=["questions"])
logger = logging.getLogger(__name__)

QUESTIONS_FILE = Path(__file__).resolve().parents[1] / "questions.json"

with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
    QUESTIONS = json.load(file)


@router.get("")
def get_questions() -> list[str]:
    return [question["question"] for question in QUESTIONS]


@router.get("/speak")
def speak_question(question: str = Query(..., min_length=1), voice_id: str | None = Query(default=None)):
    try:
        if voice_id is None:
            audio_path = text_to_speech_with_elevenlabs(question)
        else:
            audio_path = text_to_speech_with_elevenlabs(question, voice_id=voice_id)
        return FileResponse(audio_path, media_type="audio/mpeg", filename=audio_path.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        logger.exception("Question speech synthesis failed")
        raise HTTPException(status_code=500, detail=f"Question speech synthesis failed: {error}") from error


@router.post("/analyze-interview")
def analyze_interview(video: UploadFile = File(...), question: str = Form(...), role: str = Form("General job interview")):
    stage = "starting"

    try:
        logger.info("Starting interview upload pipeline for %s", video.filename)
        stage = "saving-upload"
        job_id, video_path = save_uploaded_video(video)
        logger.info("Saved interview upload job_id=%s path=%s", job_id, video_path)

        stage = "extracting-audio"
        audio_path = extract_audio_from_video(video_path, job_id)
        logger.info("Extracted audio for job_id=%s path=%s", job_id, audio_path)

        stage = "transcribing-audio"
        transcript = speech_to_text_with_elevenlabs(audio_path)
        logger.info("Transcribed audio for job_id=%s", job_id)

        stage = "analyzing-answer"
        result = analyze_answer(
            question=question,
            transcript=transcript,
            role=role,
        )
        logger.info("Completed interview analysis job_id=%s", job_id)
        return result
    except RuntimeError as error:
        logger.exception("Interview upload pipeline failed at stage=%s", stage)
        raise HTTPException(status_code=500, detail=f"Interview upload pipeline failed at stage '{stage}': {error}") from error
    except Exception as error:
        logger.exception("Unexpected interview upload failure at stage=%s", stage)
        raise HTTPException(status_code=500, detail=f"Unexpected interview upload failure at stage '{stage}': {error}") from error
