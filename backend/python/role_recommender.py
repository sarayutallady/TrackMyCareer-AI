# backend/python/role_recommender.py
"""
Role recommender + role match analyzer.

Features:
- recommend_roles(skills, top_n=5): returns a GPT-assisted list of top role suggestions
- analyze_role_match(skills, role, job_description=None): returns detailed JSON with:
    - readiness (0-100)
    - matched_skills, missing_skills (lists)
    - category_match_percent (technical / soft / tools)
    - role_iq (weighted combined score)
    - gap_levels (critical/moderate/minor)
    - project_suggestions (list)
    - learning_plan (30/60/90)
Uses gpt_json when possible; falls back to local matching using ROLE_DATABASE and heuristics.
"""

import logging
from typing import List, Dict, Any
from skill_extractor import extract_skills, COMMON_SKILLS
from ai_helper import gpt_json  # you already use this elsewhere
import difflib
import random

logger = logging.getLogger(__name__)

# A lightweight role database (fallback). You can expand later.
ROLE_DATABASE = [
    {"title": "Software Engineer", "keywords": ["python", "java", "git", "api", "algorithms", "data structures"]},
    {"title": "Frontend Developer", "keywords": ["react", "javascript", "html", "css", "ui design"]},
    {"title": "Backend Developer", "keywords": ["node", "api", "database", "security", "microservices"]},
    {"title": "Data Analyst", "keywords": ["sql", "excel", "power bi", "tableau", "pandas", "statistics"]},
    {"title": "Data Scientist", "keywords": ["python", "machine learning", "pandas", "tensorflow", "statistics"]},
    {"title": "ML Engineer", "keywords": ["mlops", "docker", "pytorch", "tensorflow", "aws"]},
    {"title": "Cloud Engineer", "keywords": ["aws", "azure", "gcp", "terraform", "devops"]},
    {"title": "DevOps Engineer", "keywords": ["jenkins", "kubernetes", "docker", "linux", "ci/cd"]},
    {"title": "Product Manager", "keywords": ["roadmap", "stakeholder", "communication", "agile"]},
    {"title": "Business Analyst", "keywords": ["requirements", "excel", "data analysis", "bp modeling", "stakeholders"]},
    {"title": "UX Designer", "keywords": ["figma", "wireframing", "user research", "ui"]},
    # add more fallback roles if desired
]


# ----- Helpers -----
def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _similar(a: str, b: str) -> float:
    """Simple similarity (0..1) using difflib; cheap semantic approximation."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _best_local_role_matches(skills: List[str], top_n=5) -> List[Dict[str, Any]]:
    """Local role matching fallback."""
    skills_l = [s.lower() for s in skills]
    scored = []
    for role in ROLE_DATABASE:
        required = role.get("keywords", [])
        matched = [k for k in required if k in skills_l]
        match_count = len(matched)
        score = int((match_count / max(1, len(required))) * 100)
        scored.append({
            "title": role["title"],
            "readiness": score,
            "reason": f"Matches {match_count}/{len(required)} key skills",
            "matched_skills": [m.title() for m in matched],
            "missing_skills": [r.title() for r in required if r not in skills_l]
        })
    scored = sorted(scored, key=lambda x: -x["readiness"])
    return scored[:top_n]


def _categorize_skill(skill: str) -> str:
    """Heuristic category guess for a skill string (technical / tool / soft / domain)."""
    s = _normalize(skill)
    # quick keyword-based heuristics
    tech_keywords = ["python", "java", "c++", "javascript", "sql", "r", "pandas", "numpy", "tensorflow", "pytorch", "ml", "machine", "deep", "react", "angular", "node", "django", "flask", "fastapi"]
    tool_keywords = ["docker", "kubernetes", "git", "github", "jira", "tableau", "power bi", "excel", "snowflake", "aws", "gcp", "azure", "redis", "postgresql", "mysql"]
    soft_keywords = ["communication", "leadership", "teamwork", "problem solving", "presentation", "negotiation", "stakeholder", "time management"]
    domain_keywords = ["marketing", "finance", "healthcare", "sales", "ops", "operations", "product", "analytics", "research"]

    for kw in tech_keywords:
        if kw in s:
            return "technical"
    for kw in tool_keywords:
        if kw in s:
            return "tools"
    for kw in soft_keywords:
        if kw in s:
            return "soft"
    for kw in domain_keywords:
        if kw in s:
            return "domain"
    # fallback checks against COMMON_SKILLS
    s_plain = s.replace("-", " ")
    for cs in COMMON_SKILLS:
        if cs in s_plain:
            # treat words like "excel" as tools; many COMMON_SKILLS will be tech/tool
            if cs in ["communication", "leadership", "teamwork", "creativity"]:
                return "soft"
            if cs in ["excel", "power bi", "tableau", "git", "docker"]:
                return "tools"
            # default to technical
            return "technical"
    # last fallback
    return "technical"


def _classify_skills(skills: List[str]) -> Dict[str, List[str]]:
    cats = {"technical": [], "tools": [], "soft": [], "domain": []}
    for s in skills:
        cat = _categorize_skill(s)
        cats.setdefault(cat, []).append(s)
    return cats


# ----- Public API -----
def recommend_roles(skills: List[str], top_n=5) -> List[Dict[str, Any]]:
    """
    Recommend top roles for a given skill list.

    Strategy:
      - Ask GPT for suggestions (better), freeze to JSON using gpt_json
      - If GPT fails, use local simple matching algorithm
    """
    # normalize unique
    skills = sorted(list(set([_normalize(s) for s in skills if s])))
    if not skills:
        return _best_local_role_matches([])

    # GPT prompt (returns JSON)
    prompt = f"""
You are a helpful career recommender.

Candidate skills:
{skills}

Return a JSON array of up to {top_n} objects with keys:
- title (string)
- reason (short string)
- readiness (integer 0-100)

Example:
[
  {{"title":"Data Analyst","reason":"Strong SQL + Excel","readiness":85}},
  {{"title":"Frontend Developer","reason":"React projects","readiness":70}}
]
Respond ONLY with JSON.
    """
    try:
        res = gpt_json(prompt, temperature=0.3)
        if isinstance(res, list) and res:
            cleaned = []
            for it in res[:top_n]:
                title = it.get("title") or ""
                readiness = int(it.get("readiness", 50))
                reason = it.get("reason", "")
                cleaned.append({"title": title, "readiness": readiness, "reason": reason})
            return cleaned
    except Exception as e:
        logger.warning("GPT recommend_roles failed, falling back to local. %s", e)

    # fallback
    return _best_local_role_matches(skills, top_n=top_n)


def analyze_role_match(skills: List[str], role: str = None, job_description: str = None, top_n_projects: int = 6) -> Dict[str, Any]:
    """
    Analyze how candidate skills match a target role (or job_description).
    Returns a dict with:
      - title
      - readiness
      - role_iq
      - matched_skills / missing_skills
      - category_match_percent (technical, soft, tools)
      - gap_levels (critical, moderate, minor)
      - project_suggestions (list of {title,desc,skills})
      - learning_plan: dict with 30_days,60_days,90_days (each a list of week tasks)
    """
    skills_norm = sorted(list(set([_normalize(s) for s in (skills or []) if s])))
    # If job_description given, ask GPT to extract required skills (preferred)
    required_skills = []
    jd_text = job_description or ""
    if jd_text.strip():
        prompt = f"""
Extract the required and preferred skills from this job description.
Return JSON with keys:
{{"required": ["skill1","skill2"], "preferred": ["skillA","skillB"]}}
Job description:
\"\"\"{jd_text}\"\"\"
Return ONLY JSON.
"""
        try:
            res = gpt_json(prompt, temperature=0.0)
            if isinstance(res, dict):
                required_skills = [ _normalize(s) for s in res.get("required", []) if s ]
                preferred = [ _normalize(s) for s in res.get("preferred", []) if s ]
                # combine
                required_skills = list(dict.fromkeys(required_skills + preferred))
        except Exception as e:
            logger.warning("gpt_json failed extracting JD skills: %s", e)

    # If role name provided and no JD, try to find role keywords in local DB
    if not required_skills and role:
        # local DB match
        for r in ROLE_DATABASE:
            if _normalize(role) == _normalize(r["title"]):
                required_skills = [ _normalize(k) for k in r.get("keywords", []) ]
                break

    # If still empty, ask GPT to produce required skills for generic role
    if not required_skills and role:
        prompt = f"""
List the top required skills (both technical and soft) for the role: "{role}".
Return JSON: {{"required": ["skill1","skill2"], "preferred": ["skillA"]}}
Return ONLY JSON.
"""
        try:
            res = gpt_json(prompt, temperature=0.2)
            if isinstance(res, dict):
                required_skills = [ _normalize(s) for s in res.get("required", []) if s ]
                preferred = [ _normalize(s) for s in res.get("preferred", []) if s ]
                required_skills = list(dict.fromkeys(required_skills + preferred))
        except Exception as e:
            logger.warning("gpt_json failed to list role skills: %s", e)

    # Final fallback: take top keywords from ROLE_DATABASE by role name similarity
    if not required_skills:
        # pick the top local role by best fuzzy match
        best = None
        best_ratio = 0
        if role:
            rname = _normalize(role)
            for r in ROLE_DATABASE:
                ratio = _similar(rname, _normalize(r["title"]))
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = r
        if best:
            required_skills = [ _normalize(k) for k in best.get("keywords", []) ]

    # If still empty - as absolute last resort, create empty required_skills
    required_skills = required_skills or []

    # Matched vs missing
    matched = []
    for rs in required_skills:
        # exact or fuzzy match against candidate skills
        # if any candidate skill is highly similar -> count as matched
        found = False
        for cs in skills_norm:
            if cs == rs or _similar(cs, rs) > 0.78:
                found = True
                matched.append(rs)
                break
        # allow substring match
        if not found:
            for cs in skills_norm:
                if rs in cs or cs in rs:
                    found = True
                    matched.append(rs)
                    break

    matched = sorted(list(set(matched)))
    missing = [r for r in required_skills if r not in matched]

    # classify candidate skills into categories
    candidate_cats = _classify_skills([s for s in skills_norm])
    required_cats = _classify_skills([r for r in required_skills])

    def percent_match(cat_name):
        req = set(required_cats.get(cat_name, []))
        if not req:
            return None
        matched_in_cat = len([r for r in req if r in matched or any(_similar(r,cs) > 0.78 for cs in skills_norm)])
        return int((matched_in_cat / len(req)) * 100)

    tech_pct = percent_match("technical") or 0
    soft_pct = percent_match("soft") or 0
    tools_pct = percent_match("tools") or 0

    # Role IQ weighted as defined: Tech 60%, Soft 20%, Tools 20%
    role_iq = int(round(tech_pct * 0.6 + soft_pct * 0.2 + tools_pct * 0.2))

    # Readiness fallback: simple ratio of matched required skills
    readiness = int(round((len(matched) / max(1, len(required_skills))) * 100)) if required_skills else 0

    # Gap levels:
    # - critical: missing required skills (exact)
    # - moderate: skills that appear in preferred or partial match (we detect by fuzzy similarity threshold)
    # - minor: optional skills present in COMMON_SKILLS but not required
    critical = [m for m in missing]  # required but missing
    moderate = []
    minor = []
    # moderate: if any candidate skill is similar to a required skill (0.5 - 0.78)
    for r in missing:
        for cs in skills_norm:
            sim = _similar(r, cs)
            if 0.48 < sim < 0.78:
                moderate.append(r)
                break
    # minor: skills present in candidate that are NOT in required but are in COMMON_SKILLS
    minor = [s for s in skills_norm if s not in required_skills and s in [c.lower() for c in COMMON_SKILLS]]

    # generate project suggestions (GPT preferred)
    project_suggestions = []
    try:
        pj_prompt = f"""
Generate {top_n_projects} role-specific project suggestions for a candidate trying to reach the role "{role or 'target role'}".
Base suggestions primarily on these missing skills (critical): {critical}.
Return JSON array like:
[
  {{"title":"Project A","description":"...","skills":["skill1","skill2"]}},
  ...
]
Return ONLY JSON.
"""
        pj_res = gpt_json(pj_prompt, temperature=0.3)
        if isinstance(pj_res, list) and pj_res:
            for pj in pj_res[:top_n_projects]:
                project_suggestions.append({
                    "title": pj.get("title"),
                    "description": pj.get("description", ""),
                    "skills": pj.get("skills", [])
                })
    except Exception as e:
        logger.warning("gpt_json projects failed: %s", e)

    # fallback local simple project generator if GPT failed or returned empty
    if not project_suggestions:
        # create projects by combining missing / critical skills into practical projects
        base = critical or (missing[:2] if missing else ["build a portfolio project"])
        project_suggestions = []
        for i in range(top_n_projects):
            skills_for_proj = base[:2] if len(base) >= 2 else base
            title = f"{(role or 'Target Role')} - Practical Project #{i+1}"
            desc = f"Build a project that uses {' ,'.join(skills_for_proj)}; show end-to-end pipeline and document outcomes."
            project_suggestions.append({
                "title": title,
                "description": desc,
                "skills": skills_for_proj
            })

    # generate learning plan (GPT preferred)
    learning_plan = {}
    try:
        lp_prompt = f"""
Create 3 role-specific learning roadmaps (30 / 60 / 90 days) for someone trying to become a {role or 'target role'}.
Base the plan on these missing/critical skills: {critical}.
Return JSON:
{{"30_days": ["Week 1: ...","Week 2: ..."], "60_days":[...], "90_days":[...]}}
Return ONLY JSON.
"""
        lp_res = gpt_json(lp_prompt, temperature=0.4)
        if isinstance(lp_res, dict):
            learning_plan = lp_res
    except Exception as e:
        logger.warning("gpt_json learning_plan failed: %s", e)

    # fallback local basic timetable
    if not learning_plan:
        # simple templated plans
        def make_plan(days):
            weeks = days // 7
            plan = []
            for w in range(1, weeks + 1):
                if w == 1:
                    plan.append(f"Week {w}: Fundamentals - study core missing skills: {', '.join(critical[:3]) or 'foundations'}")
                elif w <= max(2, weeks // 2):
                    plan.append(f"Week {w}: Tools & practice - hands-on exercises and tutorials")
                elif w == weeks - 1:
                    plan.append(f"Week {w}: Build project - start the capstone project")
                else:
                    plan.append(f"Week {w}: Polish - resume, portfolio, mock interviews")
            return plan

        learning_plan = {
            "30_days": make_plan(30),
            "60_days": make_plan(60),
            "90_days": make_plan(90)
        }

    out = {
        "title": role or "Custom Role",
        "readiness": readiness,
        "role_iq": role_iq,
        "matched_skills": [m.title() for m in matched],
        "missing_skills": [m.title() for m in missing],
        "category_match_percent": {
            "technical": tech_pct,
            "soft": soft_pct,
            "tools": tools_pct
        },
        "gap_levels": {
            "critical": [s.title() for s in critical],
            "moderate": [s.title() for s in moderate],
            "minor": [s.title() for s in minor],
        },
        "project_suggestions": project_suggestions,
        "learning_plan": learning_plan
    }

    return out


# Quick test
if __name__ == "__main__":
    # naive local test
    sample_skills = ["Python", "Pandas", "SQL", "Tableau", "Communication"]
    print("Recommend roles:", recommend_roles(sample_skills, top_n=5))
    print("Analyze Data Analyst:", analyze_role_match(sample_skills, role="Data Analyst"))
