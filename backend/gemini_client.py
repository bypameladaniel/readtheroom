import os
from dotenv import load_dotenv
from google import genai
import json
from pathlib import Path
from dataclasses import asdict

from expressions_analysis.data_aggregation import AggregatedResult
from expressions_analysis.helper import _FloatEncoder

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
    
# ── Expression feedback ────────────────────────────────────────────────────────

_FEEDBACK_SYSTEM_PROMPT = """
You are an expert interview coach specializing in non-verbal communication and 
body language. You analyze facial expression data captured during job interviews 
and provide honest, constructive, and actionable feedback.
 
Your feedback should:
- Be warm and encouraging, but direct about areas needing improvement
- Reference specific timestamps when flagging moments of concern
- Give concrete, actionable advice the candidate can practice before their next interview
- Consider the emotional arc across the full interview, not just isolated moments
- Distinguish between nervousness (understandable) and patterns that undermine credibility
""".strip()
 
_FEEDBACK_USER_TEMPLATE = """
Below is facial expression data captured during a {duration_min:.1f}-minute job interview 
for a {role} position. Analyze this data and provide structured coaching feedback.
 
--- EXPRESSION DATA ---
{expression_data}
-----------------------
""".strip()
 
 
def generate_expression_feedback(
    agg: AggregatedResult,
    role: str = "General job interview",
) -> dict:
    """
    Takes an AggregatedResult and calls Gemini to produce structured
    interview coaching feedback.
 
    Args:
        agg:            Output from aggregate().
        role:           Job role being interviewed for (adds context to feedback).
 
    Returns:
        Parsed dict matching the response schema below.
    """
 
    # Serialise aggregation to a clean JSON string for the prompt

    expression_data = json.dumps(agg if isinstance(agg, dict) else asdict(agg), indent=2, cls=_FloatEncoder)
 
    prompt = _FEEDBACK_USER_TEMPLATE.format(
        duration_min    = agg.duration_sec / 60,
        role            = role,
        expression_data = expression_data,
    )
 
    response = client.models.generate_content(
        model    = "gemini-2.5-flash",
        contents = prompt,
        config   = {
            "system_instruction"  : _FEEDBACK_SYSTEM_PROMPT,
            "temperature"         : 0.4,      # slight creativity for natural coaching tone
                                              # lower than creative tasks, higher than pure analysis
            "response_mime_type"  : "application/json",
            "response_schema"     : {
                "type": "OBJECT",
                "properties": {
 
                    # ── Overall impression ─────────────────────────────────
                    "overall_score": {
                        "type": "INTEGER",
                    },
                    "overall_summary": {
                        "type": "STRING",
                    },
 
                    # ── Emotional arc ──────────────────────────────────────
                    "emotional_arc": {
                        "type": "OBJECT",
                        "properties": {
                            "opening":  {"type": "STRING"},  # feedback on first third
                            "middle":   {"type": "STRING"},  # feedback on mid section
                            "closing":  {"type": "STRING"},  # feedback on final third
                            "arc_note": {"type": "STRING"},  # pattern across the full arc
                        }
                    },
 
                    # ── Specific flags ─────────────────────────────────────
                    "moments_of_concern": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "timestamp": {"type": "STRING"},   # e.g. "0:42 – 0:58"
                                "emotion":   {"type": "STRING"},
                                "note":      {"type": "STRING"},   # what it may signal
                                "tip":       {"type": "STRING"},   # how to address it
                            }
                        }
                    },
 
                    # ── Strengths ──────────────────────────────────────────
                    "strengths": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
 
                    # ── Improvements ───────────────────────────────────────
                    "improvements": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
 
                    # ── Actionable drills ──────────────────────────────────
                    "practice_exercises": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
                }
            }
        }
    )
 
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"raw_feedback": response.text}
 


