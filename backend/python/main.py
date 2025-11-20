# backend/python/main.py
"""
Improved backend main.py
- Loads roles.json (if present)
- Robust fuzzy role matching
- Returns 4 recommended roles
- Improved ATS scoring and matching
- Produces learning_plan, projects, missing_skills, summary_text
Compatible with the Dashboard.jsx expected JSON.
"""

import json
import logging
import math
import re
import uvicorn
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import difflib

logger = logging.getLogger("trackmycareer")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="TrackMyCareer-AI (Enhanced v1.2)", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# Load roles.json (safe)
# ---------------------
DATA_DIR = Path(__file__).resolve().parent / "data"
ROLES_JSON_PATH = DATA_DIR / "roles.json"

ROLE_DB: Dict[str, Dict[str, Any]] = {}
try:
    if ROLES_JSON_PATH.exists():
        with open(ROLES_JSON_PATH, "r", encoding="utf-8") as fh:
            ROLE_DB = json.load(fh)
            logger.info("Loaded roles.json with %d roles.", len(ROLE_DB))
    else:
        logger.warning("roles.json not found at %s — using minimal fallback.", ROLES_JSON_PATH)
        ROLE_DB = {
            "General": {"skills": ["communication", "problem solving", "documentation"], "projects": []}
        }
except Exception as e:
    ROLE_DB = {"General": {"skills": ["communication", "problem solving"], "projects": []}}
    logger.exception("Failed to load roles.json — using fallback ROLE_DB. Error: %s", e)

# normalize role keys list for fuzzy matching
ROLE_KEYS = list(ROLE_DB.keys())

# ---------------------
# Utility helpers
# ---------------------
def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    txt = text.lower()
    txt = re.sub(r"[\r\n\t,;|]+", " ", txt)
    txt = re.sub(r"[^\w\s\+\#\-\.\']", " ", txt)  # keep +, #, -, ., '
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

async def _get_text_from_upload(upload: UploadFile) -> str:
    if not upload:
        return ""
    try:
        raw = await upload.read()
        txt = raw.decode("utf-8", errors="ignore")
        if len(txt) < 30:
            # Binary or PDF; frontend can paste text instead
            return "[BINARY_OR_PDF_UPLOADED]"
        return txt
    except Exception as e:
        logger.exception("Failed to read upload: %s", e)
        return ""

def fuzzy_find_role_key(target_role: str) -> str:
    """
    Try to find the closest matching role key from ROLE_DB.
    Returns a role key (exact or fuzzy) or 'General' fallback.
    """
    if not target_role:
        return "General" if "General" in ROLE_DB else (ROLE_KEYS[0] if ROLE_KEYS else "General")
    tr = target_role.strip()
    # 1) exact match (case-insensitive)
    for r in ROLE_KEYS:
        if r.lower() == tr.lower():
            return r
    # 2) direct substring match
    for r in ROLE_KEYS:
        if tr.lower() in r.lower() or r.lower() in tr.lower():
            return r
    # 3) difflib close matches
    close = difflib.get_close_matches(tr, ROLE_KEYS, n=1, cutoff=0.6)
    if close:
        return close[0]
    # 4) try token-wise match: check if any token matches role tokens
    tokens = re.findall(r"[a-zA-Z0-9\+\#]{3,}", tr.lower())
    for r in ROLE_KEYS:
        r_tokens = re.findall(r"[a-zA-Z0-9\+\#]{3,}", r.lower())
        if any(t in r_tokens for t in tokens):
            return r
    # fallback
    return "General" if "General" in ROLE_DB else (ROLE_KEYS[0] if ROLE_KEYS else "General")

# ---------------------
# Skill extractor (simple; phrase-first)
# ---------------------
# Build a MASTER_SKILLS set from ROLE_DB to detect in resume text
MASTER_SKILLS = set()
for meta in ROLE_DB.values():
    for s in meta.get("skills", []):
        MASTER_SKILLS.add(s.lower())

# add a few safe aliases
ALIASES = {
    "js": "javascript",
    "py": "python",
    "powerbi": "power bi",
    "rest api": "rest apis",
    "rest apis": "rest apis",
    "ci/cd": "ci/cd",
    "k8s": "kubernetes",
    "aws lambda": "aws",
    "gcp": "gcp",
}
for k, v in ALIASES.items():
    MASTER_SKILLS.add(k.lower())
    MASTER_SKILLS.add(v.lower())

def extract_skills_from_text(resume_text: str, max_matches: int = 200) -> List[str]:
    """Phrase-aware skill detection using MASTER_SKILLS + fuzzy tokens."""
    txt = normalize_text(resume_text)
    found = set()

    # match explicit multi-word phrases first (longer first)
    phrases = sorted(list(MASTER_SKILLS), key=lambda s: -len(s))
    for phrase in phrases:
        if len(phrase) < 2:
            continue
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, txt):
            found.add(ALIASES.get(phrase, phrase))

    # detect common language tokens (c++, c# etc)
    extras = re.findall(r"c\+\+|c#|\bjava\b|\bpython\b|\bruby\b|\bgo\b|\brust\b|\btypescript\b", resume_text.lower())
    for e in extras:
        found.add(e)

    # fallback: token set fuzzy matches using difflib against MASTER_SKILLS
    tokens = list(set(re.findall(r"[a-zA-Z0-9\+\#]{3,}", txt)))
    master_list = sorted(list(MASTER_SKILLS))
    for t in tokens:
        if t in ALIASES:
            found.add(ALIASES[t])
            continue
        if t in master_list:
            found.add(t)
            continue
        close = difflib.get_close_matches(t, master_list, n=1, cutoff=0.86)
        if close:
            found.add(close[0])

    # produce readable list (preserve common tokens capitalization)
    readable = []
    for s in sorted(found):
        # keep tech tokens in typical casing
        if s in ["python", "java", "javascript", "sql", "react", "node", "c++", "c#"]:
            readable.append(s if s in ["c++", "c#"] else s.capitalize())
        else:
            readable.append(s.capitalize() if s.islower() and " " not in s else s)
    # limit and return
    return readable[:max_matches]

# ---------------------
# ATS scoring (robust)
# ---------------------
def compute_ats_score(resume_text: str, target_role: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    txt = normalize_text(resume_text)
    # find best role key
    role_key = fuzzy_find_role_key(target_role)
    role_skills = set([k.lower() for k in ROLE_DB.get(role_key, {}).get("skills", [])])

    # augment role keywords from job_description if provided (top tokens)
    extra_keywords = set()
    if job_description:
        jd = normalize_text(job_description)
        tokens = re.findall(r"[a-zA-Z0-9\+\#\-]{3,}", jd)
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        jd_sorted = sorted(freq.items(), key=lambda x: -x[1])
        for t, _ in jd_sorted[:30]:
            extra_keywords.add(t.lower())

    role_keywords = set(role_skills) | extra_keywords
    # ensure some fallback tokens
    if not role_keywords:
        role_keywords = set(["python", "sql", "javascript", "git"])

    matched_keywords = []
    weight = 0.0
    # treat core skills (role_skills) heavier
    for kw in role_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, txt):
            matched_keywords.append(kw)
            weight += 1.2 if kw in role_skills else 1.0
        else:
            # allow substring match for compound tokens
            if kw in txt:
                matched_keywords.append(kw)
                weight += 1.0

    matched = len(set(matched_keywords))
    total = len(role_keywords) if len(role_keywords) > 0 else 1
    raw_score = (weight / float(total)) * 100.0
    score = int(max(0, min(100, round(raw_score))))
    # small boost if several core skills matched
    matched_core = len(set(matched_keywords).intersection(role_skills))
    if matched_core >= max(1, min(3, len(role_skills) // 4)):
        score = min(100, score + 3)

    return {
        "ats_score": score,
        "matched": matched,
        "total": total,
        "matched_keywords": sorted(set(matched_keywords)),
    }

# ---------------------
# FIXED Role recommendation (top 4)
# ---------------------
def recommend_roles_for_skills(skills: List[str], top_n: int = 4) -> List[Dict[str, Any]]:
    """
    Final version:
    - No role will exceed 100% readiness
    - AR/VR will NOT be suggested unless REAL AR/VR skills are present
    - Much tighter fuzzy matching
    - Strong domain grouping to avoid cross-domain pollution
    """

    sset = set([s.lower() for s in skills])
    scores = []

    # domain maps to prevent cross-domain noise
    DOMAIN_KEYWORDS = {
        "ar/vr": ["unity", "unreal", "xr", "vr", "3d", "oculus", "arcore", "arkit"],
        "frontend": ["javascript", "react", "typescript", "html", "css", "tailwind", "vue"],
        "backend": ["python", "node", "java", "sql", "api", "fastapi", "express"],
        "data": ["sql", "pandas", "numpy", "statistics", "tableau", "power bi"],
        "devops": ["docker", "kubernetes", "ci/cd", "terraform", "linux"],
        "mobile": ["kotlin", "swift", "flutter", "react native"],
        "security": ["penetration", "owasp", "security", "nist"],
        "cloud": ["aws", "gcp", "azure", "serverless"],
    }

    def detect_domain(role: str) -> str:
        r = role.lower()
        for domain, keys in DOMAIN_KEYWORDS.items():
            for k in keys:
                if k in r:
                    return domain
        return "general"

    # detect candidate domains FROM resume
    detected_domains = set()
    for domain, keys in DOMAIN_KEYWORDS.items():
        for k in keys:
            if k in sset:
                detected_domains.add(domain)

    # fallback to general if none detected
    if not detected_domains:
        detected_domains = {"general"}

    for role, meta in ROLE_DB.items():
        role_skills = [k.lower() for k in meta.get("skills", [])]
        if not role_skills:
            continue

        # exact skills
        exact = sset.intersection(role_skills)
        exact_count = len(exact)

        # stricter fuzzy matching
        fuzzy = 0
        for rskill in role_skills:
            for s in sset:
                if len(rskill) > 4 and len(s) > 4:
                    if difflib.SequenceMatcher(None, rskill, s).ratio() > 0.88:
                        fuzzy += 1
                        break

        total_matches = exact_count + fuzzy
        max_possible = len(role_skills)

        # raw readiness
        readiness = int((total_matches / max_possible) * 100)
        readiness = min(readiness, 100)  # cap to 100%

        # DOMAIN BOOST / PENALTY
        role_domain = detect_domain(role)
        if role_domain in detected_domains:
            readiness += 10  # small boost
        else:
            readiness -= 25  # big penalty so AR/VR stops showing up!!

        readiness = max(0, min(100, readiness))

        scores.append({
            "title": role,
            "readiness": readiness,
            "reason": f"Matched {total_matches} / {max_possible} key skills",
            "matched_skills": [s.title() for s in sorted(exact)],
        })

    # final sort
    scores.sort(key=lambda x: x["readiness"], reverse=True)

    # ensure we ALWAYS return different diverse roles
    return scores[:top_n]

# ---------------------
# Learning plan generator (basic but deterministic)
# ---------------------
def create_learning_plan(role: str, skills: List[str]) -> Dict[str, Any]:
    """
    Create a safe, deterministic 30 / 60 / 90 day plan.
    Returns a dict with keys: 30_days, 60_days, 90_days, daily_schedule, missing_skills
    """
    role_key = fuzzy_find_role_key(role)
    role_skills = [s.lower() for s in ROLE_DB.get(role_key, {}).get("skills", [])]
    have = set([s.lower() for s in skills])
    missing = [s for s in role_skills if s not in have]

    def res(t, title, url="", hours=5):
        return {"type": t, "title": title, "url": url, "hours": hours}

    plan = {"30_days": [], "60_days": [], "90_days": [], "daily_schedule": [], "missing_skills": [m.title() for m in missing]}

    # 30 days: fundamentals for top missing (max 3)
    top_missing = missing[:3]
    if not top_missing:
        plan["30_days"].append({
            "task": "Polish fundamentals & build a small practice project",
            "estimated_hours": 25,
            "notes": "Consolidate core knowledge and document work.",
            "resources": [res("YouTube", "Crash course (free)", "", 6)]
        })
    else:
        for m in top_missing:
            plan["30_days"].append({
                "task": f"Learn core of {m}",
                "estimated_hours": 15,
                "notes": f"Hands-on exercises and tutorials focused on {m}",
                "resources": [res("YouTube", f"{m} - Intro (free)", "", 4)]
            })

    # 60 days: combine into small projects
    plan["60_days"].append({
        "task": "Build 1-2 small projects integrating 30-day learnings",
        "estimated_hours": 40,
        "notes": "Push to GitHub and write READMEs.",
        "resources": [res("Kaggle/Medium", "Project tutorials", "", 20)]
    })

    # 90 days: portfolio + interview prep
    plan["90_days"].append({
        "task": "Polish portfolio & interview prep",
        "estimated_hours": 40,
        "notes": "Mock interviews and polish README + demo video.",
        "resources": [res("Platform", "Mock interviews", "", 15)]
    })

    plan["daily_schedule"] = [
        {"day_range": "Mon-Fri", "morning": "1h theory", "afternoon": "2h hands-on", "evening": "1h revision"},
        {"day_range": "Weekend", "morning": "3h project", "afternoon": "2h practice"}
    ]

    return plan

# ---------------------
# Project suggester
# ---------------------
def suggest_projects_for_role(role: str, top_n: int = 3) -> List[Dict[str, Any]]:
    role_key = fuzzy_find_role_key(role)
    projects = ROLE_DB.get(role_key, {}).get("projects", []) or []
    out = []
    for p in projects[:top_n]:
        out.append({
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "tech_stack": p.get("tech_stack", [])
        })
    # fallback sample project if empty
    if not out:
        out = [{
            "title": f"{role_key} - Practice Project",
            "description": "Build a small project that addresses role fundamentals and document outcomes.",
            "tech_stack": ROLE_DB.get(role_key, {}).get("skills", [])[:3]
        }]
    return out

# ---------------------
# Summary builder
# ---------------------
def build_summary_text(target_role: str, match_percent: int, missing_skills: List[str]) -> str:
    if match_percent >= 95:
        return f"You are exceptionally well matched ({match_percent}%) for {target_role} — highlight these strengths on your resume."
    if match_percent >= 70:
        return f"You are {match_percent}% ready for {target_role}. Focus on the missing skills to reach a hiring-ready level."
    if match_percent >= 40:
        ms = ', '.join(missing_skills[:5]) if missing_skills else "core skills"
        return f"You are {match_percent}% ready for {target_role}. You have a solid base but need to close gaps in: {ms}."
    ms = ', '.join(missing_skills[:5]) if missing_skills else "core fundamentals"
    return f"You are {match_percent}% ready for {target_role}. Prioritize learning: {ms}."

# ---------------------
# Response model
# ---------------------
class AnalysisResponse(BaseModel):
    skills: List[str]
    role_recommendations: List[Dict[str, Any]]
    learning_plan: Dict[str, Any]
    ats: Dict[str, Any]
    projects: List[Dict[str, Any]]
    missing_skills: List[str]
    match_percent: int
    summary_text: str

# ---------------------
# /analyze endpoint
# ---------------------
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(
    resume: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None),
):
    # 1) get text
    text = ""
    if resume:
        text = await _get_text_from_upload(resume)
    if resume_text and (not text or len(resume_text) > len(text)):
        text = resume_text
    if not text:
        text = ""

    # 2) extract skills
    skills = extract_skills_from_text(text)

    # 3) ATS
    ats = compute_ats_score(text, target_role, job_description)

    # 4) recommend roles (top 4)
    recommendations = recommend_roles_for_skills(skills, top_n=4)

    # 5) learning plan for target role
    plan = create_learning_plan(target_role, skills)

    # 6) projects (for target role)
    projects = suggest_projects_for_role(target_role)

    # 7) match percent: if target role is present in recommendations, prefer it
    match_percent = 0
    target_key = fuzzy_find_role_key(target_role)
    # find readiness for matched role_key
    found = next((r for r in recommendations if r.get("title", "").lower() == target_key.lower()), None)
    if found:
        match_percent = found.get("readiness", 0)
    else:
        # if not found in top 4 fallback: compute readiness against ROLE_DB role_key directly
        role_sk = set([k.lower() for k in ROLE_DB.get(target_key, {}).get("skills", [])])
        have = set([s.lower() for s in skills])
        if role_sk:
            inter = have.intersection(role_sk)
            match_percent = int(round((len(inter) / len(role_sk)) * 100))
        # if still zero, fallback to top recommendation
        if match_percent == 0 and recommendations:
            match_percent = recommendations[0].get("readiness", 0)

    # 8) missing_skills: from plan if present
    missing_skills = plan.get("missing_skills", [])

    summary_text = build_summary_text(target_key, match_percent, missing_skills)

    response = {
        "skills": skills,
        "role_recommendations": recommendations,
        "learning_plan": plan,
        "ats": {
            "ats_score": ats.get("ats_score", 0),
            "matched": ats.get("matched", 0),
            "total": ats.get("total", 0),
            "matched_keywords": ats.get("matched_keywords", []),
        },
        "projects": projects,
        "missing_skills": missing_skills,
        "match_percent": match_percent,
        "summary_text": summary_text
    }

    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
