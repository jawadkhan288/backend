"""
main.py — FastAPI application entry point for HireMate backend.

Run with:
    uvicorn main:app --reload --port 8000
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.auth_router import router as auth_router
from routers.candidate_router import router as candidate_router
from routers.resume_router import router as resume_router

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title="HireMate API",
    description="Backend API for the HireMate HR Management Dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────
#  CORS — allow the Vite dev server (and production domain)
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
#  Routers
# ─────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(resume_router)


# ─────────────────────────────────────────────────────────────
#  Health Check
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "HireMate API is running 🚀"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
