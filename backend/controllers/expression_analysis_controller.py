from fastapi import APIRouter, File, Form, UploadFile
from expressions_analysis.data_aggregation import aggregate
from expressions_analysis.expression_analyzer import extract_and_analyze
from media_pipeline import save_uploaded_video
from gemini_client import generate_expression_feedback

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/expressions")
def analyze_expressions(video: UploadFile = File(...), role: str = Form("General job interview")):
    saved_video = save_uploaded_video(video)
    video_path = saved_video[1]
    expression_analysis = extract_and_analyze(video_path, sample_every_n_frames=10, verbose=False)
    agg = aggregate(expression_analysis)
    return generate_expression_feedback(
        agg=agg,
        role=role
    )
