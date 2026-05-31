from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.questions_controller import router as questions_router

app = FastAPI(title="ReadTheRoom API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions_router)