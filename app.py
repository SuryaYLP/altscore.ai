def calculate_score(user):
    score = 300

    # Basic signals
    score += min(user["transactions"] * 1.5, 150)
    score += min(user["recharge"] * 5, 100)
    score += int(user["location"] * 150)

    # Cash flow
    if user["cash_in"] > 0:
        ratio = user["cash_out"] / user["cash_in"]
        if ratio < 0.7:
            score += 120
        elif ratio < 1:
            score += 80
        else:
            score -= 50

    # Behavior
    score += min(user["p2p"] * 1.5, 100)
    score += int(user["bill_pay"] * 150)
    score += int(user["savings"] * 150)

    # Profile adjustment
    if user["profile"] == "Gig Worker":
        score += 20
    elif user["profile"] == "Student / Informal":
        score -= 20

    score = max(300, min(score, 900))

    return score


def risk_level(score):
    if score > 750:
        return "Low"
    elif score > 600:
        return "Medium"
    else:
        return "High"


# Sample user
user = {
    "profile": "Gig Worker",
    "transactions": 120,
    "recharge": 8,
    "location": 0.7,
    "cash_in": 30000,
    "cash_out": 25000,
    "p2p": 20,
    "bill_pay": 0.6,
    "savings": 0.2
}

score = calculate_score(user)
risk = risk_level(score)

print("AltScore:", score)
print("Risk:", risk)
