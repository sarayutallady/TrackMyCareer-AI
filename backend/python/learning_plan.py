# backend/python/learning_plan.py

from ai_helper import gpt_json
import logging

logger = logging.getLogger(__name__)


def create_learning_plan(role, skills):

    prompt = f"""
Create a COMPLETE 30 / 60 / 90 day learning plan for:

Role: {role}  
Skills: {skills}

RETURN JSON EXACTLY LIKE THIS:
{{
  "30_days": [
    {{
      "task": "Learn SQL basics",
      "hours": 20,
      "resources": [
        {{"type":"free","title":"YouTube SQL Course","url":"https://"}},
        {{"type":"paid","title":"Udemy SQL Bootcamp","url":"https://"}}
      ]
    }}
  ],
  "60_days": [...],
  "90_days": [...],
  "daily_schedule": [
    {{"day":"Mon-Fri","study_hours":"2 hours/day"}}
  ]
}}
"""

    try:
        return gpt_json(prompt, temperature=0.2)

    except Exception as e:
        logger.error("Plan failed: %s", e)
        return {
            "30_days":[{"task":"Basics","hours":20}],
            "60_days":[{"task":"Projects","hours":40}],
            "90_days":[{"task":"Interview Prep","hours":30}],
            "daily_schedule":[{"day":"Mon-Fri","study_hours":"2 hours"}]
        }
