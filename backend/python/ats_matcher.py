# ats_matcher.py
"""
ATS matcher utilities.
Provides:
- compute_ats_score(resume_text, target_role, job_description=None)
- compute_ats(resume_text, target_role)  # backward-compatible wrapper

This version is intentionally simple and deterministic:
- extracts keywords for a role from a small built-in mapping
- counts keyword matches (case-insensitive)
- returns integer percentage and match details

You should replace ROLE_KEYWORDS with your real mapping or load from a JSON.
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Simple role -> keyword list example. Replace/extend this or load from a file.
ROLE_KEYWORDS = {
    "ML Engineer": [
        "python", "pytorch", "tensorflow", "scikit-learn", "transformer",
        "deep learning", "nlp", "computer vision", "model", "inference"
    ],
    "Data Analyst": [
        "python", "sql", "pandas", "excel", "tableau", "power bi", "visualization",
        "statistics", "data cleaning", "etl"
    ],
    "Frontend Developer": [
        "javascript", "react", "html", "css", "typescript", "webpack", "vite",
        "tailwind", "ui", "dom"
    ],
    "Software Engineer": [
        "java", "git", "rest api", "microservices", "docker", "kubernetes",
        "unit test", "ci/cd"
    ],
    # Add other roles you support...
}

# fallback keywords across roles if role not found
FALLBACK_KEYWORDS = ["python", "sql", "javascript", "git", "docker", "rest", "api"]

def _normalize_text(text: str) -> str:
    return (text or "").lower()

def _token_match_count(text: str, keywords: List[str]) -> Dict:
    """
    Count how many distinct keywords appear in text.
    Returns dict: { matched: int, total: int, matched_keywords: [...] }
    """
    txt = _normalize_text(text)
    matched_keywords = []
    for kw in keywords:
        # use word-boundary-ish match for short tokens and substring for long ones
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, txt):
            matched_keywords.append(kw)
        else:
            # fallback: substring match for phrases or tokens that may appear stuck
            if kw.lower() in txt:
                matched_keywords.append(kw)
    total = len(keywords)
    matched = len(set(matched_keywords))
    return {"matched": matched, "total": total, "matched_keywords": sorted(set(matched_keywords))}

def compute_ats_score(resume_text: str, target_role: str, job_description: Optional[str] = None) -> Dict:
    """
    Main ATS function.
    Accepts:
      resume_text: str
      target_role: str
      job_description: Optional[str] - used to augment keywords (if provided)

    Returns:
      {
        "ats_score": int,        # 0-100 percent
        "matched": int,
        "total": int,
        "keywords": [...],
        "error": None or "message"
      }
    """
    try:
        if not resume_text:
            return {"ats_score": 0, "matched": 0, "total": 0, "keywords": [], "error": "Empty resume text"}

        role = (target_role or "").strip()
        keywords = ROLE_KEYWORDS.get(role)

        if not keywords:
            # try approximate match (case-insensitive)
            for r, kws in ROLE_KEYWORDS.items():
                if r.lower() == role.lower():
                    keywords = kws
                    break

        if not keywords:
            # fallback: use a small default set
            keywords = FALLBACK_KEYWORDS.copy()

        # If a job_description is passed, extract additional tokens (simple split)
        if job_description:
            jd = _normalize_text(job_description)
            # take top tokens from JD (very naive: split and keep long tokens)
            extra = []
            for token in re.findall(r"[a-zA-Z0-9\-\_]{3,}", jd):
                if token not in keywords and token not in extra:
                    extra.append(token)
                    if len(extra) >= 8:
                        break
            if extra:
                keywords = keywords + extra

        counts = _token_match_count(resume_text, keywords)
        matched = counts["matched"]
        total = counts["total"]

        # compute percentage: matched/total * 100, but clamp to 100
        ats_score = 0
        if total > 0:
            ats_score = int(round((matched / total) * 100))

        return {
            "ats_score": min(max(ats_score, 0), 100),
            "matched": matched,
            "total": total,
            "keywords": counts["matched_keywords"],
            "error": None,
        }
    except Exception as e:
        logger.exception("compute_ats_score error: %s", e)
        return {"ats_score": 0, "matched": 0, "total": 0, "keywords": [], "error": str(e)}

# Backwards-compatible wrapper used by older code
def compute_ats(resume_text: str, target_role: str) -> Dict:
    """
    Older code used compute_ats(resume_text, target_role).
    Keep that API and forward to compute_ats_score.
    """
    return compute_ats_score(resume_text, target_role, None)


# If someone imported * and expects a function named compute_ats_score, ensure it's exported
__all__ = ["compute_ats_score", "compute_ats"]
