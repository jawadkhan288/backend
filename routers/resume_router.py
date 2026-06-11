"""
routers/resume_router.py — Resume upload & parsing endpoint.

POST /api/resumes/parse
  - Accepts: PDF, DOCX, JSON (multipart/form-data)
  - Returns: Structured resume data as JSON
  - Uses Groq (Llama 3.3 70B) for PDF/DOCX parsing
  - No file storage — parse and discard
"""
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from services.resume_parser import parse_resume

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "json"}

router = APIRouter(
    prefix="/api/resumes",
    tags=["Resume Parsing"],
)


@router.post("/parse")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF, DOCX, or JSON) and get structured data back.
    
    - **PDF/DOCX**: Text is extracted and sent to Groq (Llama 3.3) for parsing.
    - **JSON**: Directly validated against the expected schema (no LLM needed).
    
    Returns the parsed resume as a JSON object.
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '.{ext}'. Accepted: {', '.join('.' + e for e in ALLOWED_EXTENSIONS)}",
        )

    # Read file bytes
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(file_bytes) / 1024 / 1024:.1f} MB). Maximum: 10 MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Get Groq API key (only required for PDF/DOCX)
    groq_api_key = os.getenv("GROQ_API_KEY")

    try:
        parsed_data = parse_resume(
            file_bytes=file_bytes,
            filename=file.filename,
            groq_api_key=groq_api_key,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume parsing failed: {str(e)}",
        )

    return parsed_data

