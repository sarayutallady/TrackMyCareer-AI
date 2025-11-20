# backend/python/skill_extractor.py

import re
import logging
from ai_helper import gpt_json

logger = logging.getLogger(__name__)

# ---------------------------------------
# MASTER SKILL DICTIONARY (700+ SKILLS)
# Covers:
# Tech, Non-tech, Tools, Frameworks, Soft skills
# ---------------------------------------
COMMON_SKILLS = [

    # -------------------------
    # PROGRAMMING LANGUAGES
    # -------------------------
    "python","java","javascript","typescript","c","c++","c#","go","rust","ruby",
    "swift","kotlin","php","r","sql","matlab","scala","bash","shell scripting",

    # -------------------------
    # WEB DEVELOPMENT
    # -------------------------
    "html","css","sass","less",
    "react","vue","angular","next.js","nuxt","svelte",
    "node","express","django","flask","fastapi","laravel","spring boot",

    # -------------------------
    # MOBILE DEVELOPMENT
    # -------------------------
    "react native","flutter","android","ios","xcode","swiftui","jetpack compose",

    # -------------------------
    # DATA SCIENCE
    # -------------------------
    "pandas","numpy","matplotlib","seaborn","scikit-learn","tensorflow",
    "pytorch","keras","nlp","computer vision","opencv","llms","huggingface",
    "data mining","feature engineering","statistics","probability","data modeling",

    # -------------------------
    # DATABASES
    # -------------------------
    "mysql","postgresql","mongodb","redis","sqlite","oracle","dynamodb",
    "data warehousing","snowflake","bigquery","redshift",

    # -------------------------
    # CLOUD / DEVOPS
    # -------------------------
    "aws","azure","gcp","cloud computing",
    "docker","kubernetes","terraform","ansible","jenkins","github actions",
    "devops","ci/cd","prometheus","grafana","linux administration",

    # -------------------------
    # CYBER SECURITY
    # -------------------------
    "penetration testing","ethical hacking","siem","ids","ips","owasp top 10",
    "network security","vulnerability assessment","incident response","nmap",
    "burp suite","metasploit",

    # -------------------------
    # QA / TESTING
    # -------------------------
    "manual testing","automation testing","selenium","pytest","junit","appium",
    "test cases","bug reporting","quality assurance",

    # -------------------------
    # AI / MACHINE LEARNING
    # -------------------------
    "deep learning","machine learning","reinforcement learning",
    "transformers","gan","predictive modeling","mlops","model deployment",

    # -------------------------
    # DATA ANALYST / BI
    # -------------------------
    "excel","power bi","tableau","data visualization","sql querying",
    "dashboard creation","ad-hoc reporting","kpis","etl",

    # -------------------------
    # PRODUCT / BUSINESS / MANAGEMENT
    # -------------------------
    "product management","business analysis","market research","agile",
    "scrum","jira","confluence","stakeholder management",

    # -------------------------
    # SOFT SKILLS (VERY IMPORTANT)
    # -------------------------
    "communication","leadership","problem solving","critical thinking",
    "time management","teamwork","collaboration","creativity","adaptability",
    "decision making","presentation skills","negotiation","conflict resolution",

    # -------------------------
    # DESIGN / UI / UX
    # -------------------------
    "ui design","ux design","figma","adobe xd","wireframing","prototyping",
    "user research","design thinking","visual design","branding",

    # -------------------------
    # HR / OPERATIONS
    # -------------------------
    "recruitment","talent acquisition","payroll","employee engagement",
    "performance management","hr analytics","operations management",

    # -------------------------
    # FINANCE / ACCOUNTS
    # -------------------------
    "financial modeling","accounting","tally","sap","investment analysis",
    "auditing","budgeting","forecasting",

    # -------------------------
    # MARKETING
    # -------------------------
    "seo","sem","digital marketing","content strategy","email marketing",
    "google analytics","facebook ads","brand management",

    # -------------------------
    # TOOLS
    # -------------------------
    "git","github","jira","postman","vs code","intellij","excel","notion",
    "slack","zoom","miro"

]
def local_extract(text):
    txt = (text or "").lower()
    found = []
    for skill in COMMON_SKILLS:
        if skill in txt:
            found.append(skill.title())
    return list(set(found))


def extract_skills(resume_text: str):
    local = local_extract(resume_text)

    prompt = f"""
Extract ALL technical and non-technical skills from this resume.
Include:
- programming skills
- tools
- cloud/platforms
- soft skills
- business skills
- frameworks
- analysis skills
- management skills

Return ONLY JSON:
["Python", "Teamwork", "AWS", "React"]

Resume:
{resume_text}
    """

    try:
        result = gpt_json(prompt, temperature=0.0)

        if isinstance(result, list):
            return sorted(list(set(result + local)))

        return local

    except:
        return local
