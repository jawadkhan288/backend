"""
services/resume_parser.py — Resume text extraction and LLM-powered parsing.

Supports: PDF, DOCX, JSON
Uses Groq (Llama 3.3 70B) for intelligent text → structured JSON conversion.
"""
import json
import re
import logging
from typing import Optional

import fitz  # PyMuPDF
from docx import Document
from openai import OpenAI

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Text Extraction (per file type)
# ─────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all text from a DOCX file using python-docx."""
    import io
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def parse_json_resume(file_bytes: bytes) -> dict:
    """Parse a JSON file that already matches our schema."""
    raw = json.loads(file_bytes.decode("utf-8"))

    # Validate required top-level keys
    required_keys = {"personalDetails"}
    if not required_keys.issubset(raw.keys()):
        raise ValueError(
            f"JSON resume must contain keys: {required_keys}. "
            f"Got: {set(raw.keys())}"
        )

    # Normalize / fill defaults
    pd = raw.get("personalDetails", {})
    return {
        "personalDetails": {
            "fullName": pd.get("fullName", "Unknown"),
            "email": pd.get("email", ""),
            "phone": pd.get("phone", ""),
            "location": pd.get("location", ""),
            "linkedin": pd.get("linkedin"),
            "portfolio": pd.get("portfolio"),
        },
        "summary": raw.get("summary"),
        "education": raw.get("education", []),
        "experience": raw.get("experience", []),
        "skills": {
            "technical": raw.get("skills", {}).get("technical", []),
            "soft": raw.get("skills", {}).get("soft", []),
            "languages": raw.get("skills", {}).get("languages", []),
        },
        "certifications": raw.get("certifications"),
    }


# ─────────────────────────────────────────────────────────────
#  LLM-Powered Parsing (Groq — Llama 3.3 70B)
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert resume parser. Given raw text extracted from a resume, 
extract the information into a strictly valid JSON object with this exact structure:

{
  "personalDetails": {
    "fullName": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string or null",
    "portfolio": "string or null"
  },
  "summary": "string or null (professional summary/objective)",
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "year": "string (e.g. '2015-2019')",
      "gpa": "string or null"
    }
  ],
  "experience": [
    {
      "position": "string",
      "company": "string",
      "duration": "string (e.g. '2021 - Present')",
      "description": ["string (achievement/responsibility)", "..."]
    }
  ],
  "skills": {
    "technical": ["string", "..."],
    "soft": ["string", "..."],
    "languages": ["string (e.g. 'English (Native)')", "..."]
  },
  "certifications": ["string", "..."] or null
}

Rules:
- Return ONLY the JSON object, no markdown fences, no extra text.
- If a field cannot be found, use empty string "" for strings, empty array [] for arrays, or null for optional fields.
- For experience descriptions, list each bullet point as a separate string in the array.
- Infer the most likely values from context when information is ambiguous.
- Always include at least one entry in education and experience if any related text exists.
"""


def parse_resume_with_llm(raw_text: str, api_key: str) -> dict:
    """
    Send extracted resume text to Groq (Llama 3.3 70B) and get structured JSON back.
    Uses the OpenAI-compatible Groq API.
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume text to parse:\n\n{raw_text}"},
            ],
            temperature=0.1,
            max_tokens=4096,
        )
    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        raise RuntimeError(f"Groq API call failed: {str(e)}")

    response_text = response.choices[0].message.content.strip()

    # Strip markdown fences if the model wraps them
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
        response_text = re.sub(r"\s*```$", "", response_text)

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\nRaw response:\n{response_text[:500]}")

    return parsed


# ─────────────────────────────────────────────────────────────
#  Main Entry Point
# ─────────────────────────────────────────────────────────────

def parse_resume(file_bytes: bytes, filename: str, groq_api_key: Optional[str] = None) -> dict:
    """
    Parse a resume file and return structured data.
    
    Args:
        file_bytes: Raw file content
        filename: Original filename (used to detect type)
        groq_api_key: Groq API key (required for PDF/DOCX)
    
    Returns:
        Structured resume dict matching the ParsedResume schema
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "json":
        # JSON files are already structured — no LLM needed
        return parse_json_resume(file_bytes)

    elif ext == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Accepted: .pdf, .docx, .json")

    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError(
            "Could not extract meaningful text from the file. "
            "The file may be scanned/image-based or empty."
        )

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is required for PDF/DOCX parsing. "
            "Set it in backend/.env"
        )

    return parse_resume_with_llm(raw_text, groq_api_key)
