import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/questions", tags=["questions"])

QUESTIONS_FILE = Path(__file__).resolve().parents[1] / "questions.json"

with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
    QUESTIONS = json.load(file)


@router.get("")
def get_questions() -> list[str]:
    return [question["question"] for question in QUESTIONS]
