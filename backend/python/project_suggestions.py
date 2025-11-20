# backend/python/project_suggestions.py

def generate_projects(skills, role):

    base = []

    # AI / ML
    if "python" in skills or "machine learning" in skills:
        base.append({
            "title":"AI Resume Analyzer",
            "description":"Build an NLP system that analyzes resumes.",
            "tech_stack":["Python","NLP","FastAPI","ML models"],
            "outcome":"A deployable ML project for your portfolio."
        })

    # Web Dev
    if "react" in skills:
        base.append({
            "title":"Modern Dashboard App",
            "description":"Build a complete dashboard with charts & auth.",
            "tech_stack":["React","Node","MongoDB"],
            "outcome":"Full-stack job-ready application."
        })

    # Data Jobs
    if "sql" in skills or "tableau" in skills:
        base.append({
            "title":"Data Insights Report",
            "description":"Analyze business data and build dashboards.",
            "tech_stack":["SQL","Excel","Power BI"],
            "outcome":"Great for data analyst roles."
        })

    # Product roles
    if "product management" in skills:
        base.append({
            "title":"Product Case Study",
            "description":"Redesign/improve an existing product.",
            "tech_stack":["Figma","Jira"],
            "outcome":"Strong PM case study for interviews."
        })

    return base
