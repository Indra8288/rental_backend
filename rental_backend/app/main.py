from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.db.init_db import init_db
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(title="Rental House System (Multi-house)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(api_router)
