import os
from dotenv import load_dotenv
from google import genai
import json
from pathlib import Path

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ── Interview analysis ────────────────────────────────────────────────────────

_ANALYSIS_SYSTEM_PROMPT = """
You are an expert interview coach.
Analyze the candidate's answer and return structured interview feedback.
""".strip()

_ANALYSIS_USER_TEMPLATE = """
Interview question:
{question}

Target role:
{role}

Candidate answer transcript:
{transcript}
""".strip()


def analyze_answer(
    question: str,
    transcript: str,
    role: str = "General job interview",
) -> dict:

    prompt = _ANALYSIS_USER_TEMPLATE.format(
        question=question,
        role=role,
        transcript=transcript,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": _ANALYSIS_SYSTEM_PROMPT,
            "temperature": 0.3,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "conciseness_score": {"type": "INTEGER"},
                    "relevance_score": {"type": "INTEGER"},
                    "filler_words": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "star_method": {
                        "type": "OBJECT",
                        "properties": {
                            "situation": {"type": "STRING"},
                            "task": {"type": "STRING"},
                            "action": {"type": "STRING"},
                            "result": {"type": "STRING"}
                        }
                    },
                    "strengths": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "improvements": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                }
            }
        }
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"raw_analysis": response.text}
