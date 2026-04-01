def calculate_score(transactions, recharge_freq, location_stability):
    score = 300

    score += min(transactions * 2, 200)
    score += min(recharge_freq * 5, 150)
    score += int(location_stability * 200)

    if score > 900:
        score = 900

    return score


def risk_level(score):
    if score > 750:
        return "Low"
    elif score > 600:
        return "Medium"
    else:
        return "High"


user = {
    "transactions": 120,
    "recharge_freq": 8,
    "location_stability": 0.7
}

score = calculate_score(**user)
risk = risk_level(score)

print("AltScore:", score)
print("Risk:", risk)
