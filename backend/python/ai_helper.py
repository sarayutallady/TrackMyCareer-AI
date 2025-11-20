# backend/python/ai_helper.py
"""
Robust AI helper that supports:
 - Real Gemini SDK (if installed and USE_GEMINI=true)
 - Safe deterministic local fallback (mock) when Gemini is missing
This prevents import-time crashes and ensures the backend always responds.
"""

import os
import json
import logging
import re

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("ai_helper")
logging.basicConfig(level=logging.INFO)

# Config
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
API_KEY = os.getenv("GOOGLE_API_KEY", None)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Try to import genai only if user requested USE_GEMINI true.
genai = None
client = None
if USE_GEMINI:
    try:
        # Some installations expose google.genai, some 'google' package with genai submodule.
        # Try flexible import.
        try:
            from google import genai as _genai  # preferred modern import
        except Exception:
            # fallback older package name
            import google
            _genai = getattr(google, "genai", None)
        if _genai is None:
            raise ImportError("google.genai not available")
        genai = _genai
        # instantiate client (most recent SDK)
        try:
            client = genai.Client(api_key=API_KEY)
        except Exception:
            # some SDKs may use configure function
            try:
                genai.configure(api_key=API_KEY)
                client = genai
            except Exception as e:
                logger.exception("Failed to instantiate genai client: %s", e)
                client = None
        logger.info("Gemini SDK import succeeded. USE_GEMINI=%s", USE_GEMINI)
    except Exception as e:
        logger.exception("Gemini SDK import failed; falling back to mock mode: %s", e)
        genai = None
        client = None
        # We do NOT raise: fallback will be used
else:
    logger.info("USE_GEMINI not enabled; running in mock fallback mode.")


# -------------------------------
# Helpers
# -------------------------------
def _extract_first_json(text: str):
    if not text:
        return None
    # Try direct json load
    try:
        return json.loads(text)
    except Exception:
        pass
    # Find first {...} or [...] block
    m = re.search(r"(\{(?:.|\n)*?\}|\[(?:.|\n)*?\])", text)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            try:
                # last resort: use ast.literal_eval
                import ast
                return ast.literal_eval(candidate)
            except Exception:
                return None
    return None


# -------------------------------
# Mock behaviors (deterministic)
# -------------------------------
def _mock_extract_skills_from_text(resume_text: str):
    # Simple deterministic heuristic: search for known keywords
    seeds = [
        "python","sql","java","javascript","react","node","docker","kubernetes","aws",
        "pandas","numpy","tensorflow","pytorch","excel","tableau","power bi",
        "git","rest api","fastapi","flask","html","css","typescript","c++","c#",
        "leadership","communication","project management","agile","scrum"
    ]
    txt = (resume_text or "").lower()
    found = []
    for s in seeds:
        if s in txt and s not in found:
            found.append(s.capitalize() if len(s)>1 else s)
    if not found:
        # return a minimal set so UI isn't empty
        return ["Python","SQL","Communication"]
    return found


def _mock_ats(resume_text: str, target_role: str):
    # simple deterministic ATS: keyword match percentage
    tokens = re.findall(r"[A-Za-z0-9]+", (target_role or "").lower())
    txt = (resume_text or "").lower()
    if not tokens:
        return {"ats_score": 50, "matched_keywords": [], "missing_keywords": []}
    matched = [t for t in tokens if t in txt]
    missing = [t for t in tokens if t not in txt]
    score = int(round((len(matched) / max(1, len(tokens))) * 100))
    return {"ats_score": score, "matched_keywords": matched, "missing_keywords": missing}


def _mock_recommend_roles(skills, top_n=5):
    sk = [s.lower() for s in (skills or [])]
    out = []
    if any("python" in s for s in sk) or any("sql" in s for s in sk):
        out.append({"title":"Data Analyst","reason":"Python/SQL skills","readiness":75})
    if any(x in " ".join(sk) for x in ["react","javascript","html","css"]):
        out.append({"title":"Frontend Developer","reason":"Frontend stack present","readiness":68})
    if any("aws" in s for s in sk) or any("docker" in s for s in sk):
        out.append({"title":"DevOps Engineer","reason":"Cloud & infra skills","readiness":55})
    if not out:
        out = [{"title":"Software Engineer","reason":"General coding fit","readiness":60}]
    return out[:top_n]


def _mock_learning_plan(role, skills):
    return {
        "30_days":[{"task":"Core fundamentals","estimated_hours":20,"resources":[{"type":"free","title":"Youtube course","url":"https://youtube.com"}]}],
        "60_days":[{"task":"Small project","estimated_hours":40,"resources":[{"type":"free","title":"Kaggle","url":"https://kaggle.com"}]}],
        "90_days":[{"task":"Interview prep & portfolio","estimated_hours":30,"resources":[{"type":"paid","title":"Udemy course","url":"https://udemy.com"}]}],
        "daily_schedule":[{"day_range":"Mon-Fri","hours_per_day":2}]
    }


# -------------------------------
# Public API: gpt_process & gpt_json
# -------------------------------
def gpt_process(prompt: str, temperature: float = 0.2) -> str:
    """
    Return plain text. Uses Gemini if available; otherwise returns short mock text.
    """
    # If real SDK available, attempt to call it
    if client is not None:
        try:
            # Newer SDK uses client.models.generate_content(...)
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt],
                generation_config={"temperature": temperature}
            )
            # prefer resp.text
            text = getattr(resp, "text", None)
            if text is None:
                # try outputs
                outputs = getattr(resp, "outputs", None)
                if outputs and isinstance(outputs, (list,tuple)) and len(outputs)>0:
                    # join content fields
                    pieces = []
                    for out in outputs:
                        if isinstance(out, dict):
                            pieces.append(out.get("content","") or out.get("text",""))
                        else:
                            pieces.append(getattr(out,"content", getattr(out,"text","")))
                    text = "\n".join([p for p in pieces if p])
                else:
                    text = str(resp)
            return text or ""
        except Exception as e:
            logger.exception("Gemini call failed in gpt_process, falling back to mock: %s", e)

    # Fallback deterministic behavior
    lower = (prompt or "").lower()
    if "extract" in lower and "skills" in lower:
        return json.dumps(_mock_extract_skills_from_text(prompt))
    if "ats" in lower or "ats_score" in lower:
        # extract role/resume snippet heuristically
        return json.dumps(_mock_ats(prompt, ""))
    if "recommend" in lower or "career" in lower:
        return json.dumps(_mock_recommend_roles([]))
    if "learning" in lower or "plan" in lower:
        return json.dumps(_mock_learning_plan("", []))
    return "OK"


def gpt_json(prompt: str, temperature: float = 0.0):
    """
    Request the model to return JSON. If Gemini available, try parsing output.
    Otherwise use mock deterministic JSON objects.
    """
    # If real SDK available, attempt to call it
    if client is not None:
        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt],
                generation_config={"temperature": temperature}
            )
            # attempt to extract textual output
            text = getattr(resp, "text", None)
            if not text:
                outputs = getattr(resp, "outputs", None)
                if outputs and isinstance(outputs, (list,tuple)) and len(outputs)>0:
                    pieces = []
                    for out in outputs:
                        if isinstance(out, dict):
                            pieces.append(out.get("content","") or out.get("text",""))
                        else:
                            pieces.append(getattr(out,"content", getattr(out,"text","")))
                    text = "\n".join([p for p in pieces if p])
                else:
                    text = str(resp)
            parsed = _extract_first_json(text)
            if parsed is not None:
                return parsed
            # try literal eval fallback
            try:
                import ast
                return ast.literal_eval(text)
            except Exception:
                raise ValueError("Failed to parse model output as JSON.")
        except Exception as e:
            logger.exception("Gemini gpt_json failed; falling back to mock: %s", e)

    # MOCK branch (deterministic parsing of prompt to supply structured objects)
    lower = (prompt or "").lower()

    # Skills request (expects JSON array)
    if "extract" in lower and "skills" in lower:
        # attempt to extract a resume substring after "resume:" if present
        m = re.search(r"resume:\s*(.+)$", prompt, flags=re.IGNORECASE|re.DOTALL)
        resume_text = m.group(1) if m else prompt
        return _mock_extract_skills_from_text(resume_text)

    # ATS request (expects dict with ats_score)
    if "ats" in lower and "resume" in lower:
        # detect role title naive
        m_role = re.search(r"role:\s*(.+)$", prompt, flags=re.IGNORECASE|re.DOTALL)
        role_text = m_role.group(1).strip().splitlines()[0] if m_role else ""
        # find resume snippet
        m_resume = re.search(r"resume:\s*(.+?)role:", prompt, flags=re.IGNORECASE|re.DOTALL)
        resume_txt = m_resume.group(1) if m_resume else prompt
        return _mock_ats(resume_txt, role_text)

    # Role recommender
    if "career recommender" in lower or "recommend the top" in lower or "recommend roles" in lower:
        # parse "skills:" block
        m = re.search(r"skills:\s*(.+)$", prompt, flags=re.IGNORECASE|re.DOTALL)
        skills_block = m.group(1) if m else ""
        skills_list = re.findall(r"[A-Za-z\+\#\-\d]{2,}", skills_block)
        return _mock_recommend_roles(skills_list)

    # Learning plan
    if "30 / 60 / 90" in lower or "learning plan" in lower:
        # try to parse role
        m = re.search(r"role[:\-]\s*(.+)$", prompt, flags=re.IGNORECASE|re.DOTALL)
        role = m.group(1).splitlines()[0].strip() if m else ""
        return _mock_learning_plan(role, [])

    # Default: return empty dict
    return {}
