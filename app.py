import math


def calculate_score(user):
    score = 300

    # Normalize inputs (0–1 scale)
    t_norm = min(user["transactions"] / 200, 1)
    r_norm = min(user["recharge"] / 10, 1)
    l_norm = user["location"]
    s_norm = user["savings"]
    b_norm = user["bill_pay"]
    p_norm = min(user["p2p"] / 50, 1)

    # Cash flow scoring
    if user["cash_in"] > 0:
        cf_ratio = user["cash_out"] / user["cash_in"]
        cf_score = max(0, 1 - cf_ratio)
    else:
        cf_score = 0.5

    # Weighted scoring (ML-like)
    score += int(150 * t_norm)
    score += int(100 * r_norm)
    score += int(150 * l_norm)
    score += int(150 * s_norm)
    score += int(150 * b_norm)
    score += int(100 * p_norm)
    score += int(150 * cf_score)

    # Non-linear penalty
    if user["cash_out"] > user["cash_in"]:
        score -= int(100 * math.log(user["cash_out"] - user["cash_in"] + 1))

    # Profile adjustments
    if user["profile"] == "Gig Worker":
        score += 10
    elif user["profile"] == "Student / Informal":
        score -= 10

    # Clamp score
    score = max(300, min(score, 900))

    return score


def risk_level(score):
    if score > 750:
        return "Low"
    elif score > 600:
        return "Medium"
    else:
        return "High"


# ------------------------
# SAMPLE RUN
# ------------------------
if __name__ == "__main__":

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
    print("Risk Level:", risk)
