# backend/python/market_insights.py

def market_insights(roles):
    results = []
    for r in roles:
        title = r["title"]

        demand_score = (abs(hash(title)) % 50) + 50  # 50–100
        avg_salary_lpa = ((abs(hash(title[::-1])) % 12) + 4)  # 4–16 LPA

        results.append({
            "role": title,
            "demand_score": demand_score,
            "average_salary_lpa": avg_salary_lpa
        })

    return results
