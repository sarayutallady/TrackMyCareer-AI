# backend/python/resume_parser.py

import io
import logging
from typing import Optional
from fastapi import UploadFile, HTTPException

# PDF
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

# DOCX
try:
    import docx
except Exception:
    docx = None

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    import re
    if not text:
        return ""
    replacements = {"\u2013": "-", "\u2014": "-", "\u2022": "*"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()

def parse_pdf(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise HTTPException(status_code=500, detail="PDF parsing not available (PyPDF2 not installed).")
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file.")
    text_chunks = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        text_chunks.append(page_text)
    full_text = "\n".join(text_chunks).strip()
    return clean_text(full_text)

def parse_docx(file_bytes: bytes) -> str:
    if docx is None:
        raise HTTPException(status_code=500, detail="DOCX parsing not available (python-docx not installed).")
    try:
        temp = io.BytesIO(file_bytes)
        document = docx.Document(temp)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted DOCX file.")
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return clean_text("\n".join(paragraphs))

def parse_txt(file_bytes: bytes) -> str:
    try:
        return clean_text(file_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        return clean_text(file_bytes.decode("latin-1", errors="ignore"))

def extract_resume_text(resume_text: Optional[str], file: Optional[UploadFile]):
    if resume_text and not file:
        return clean_text(resume_text), "text"
    if file:
        raw = file.file.read()
        file.file.seek(0)
        filename = (file.filename or "").lower()
        content_type = (file.content_type or "").lower()
        if "pdf" in content_type or filename.endswith(".pdf"):
            return parse_pdf(raw), f"file:{file.filename}"
        if "word" in content_type or filename.endswith(".docx"):
            return parse_docx(raw), f"file:{file.filename}"
        if "text" in content_type or filename.endswith(".txt"):
            return parse_txt(raw), f"file:{file.filename}"
        try:
            return parse_txt(raw), f"file:{file.filename}"
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported file format. Upload PDF, DOCX, or TXT.")
    raise HTTPException(status_code=400, detail="Provide resume_text or upload a file.")
