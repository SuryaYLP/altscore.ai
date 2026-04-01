import streamlit as st

st.set_page_config(page_title="AltScore AI", layout="centered")

st.title("💳 AltScore AI")
st.subheader("AI-Powered Alternative Credit Scoring")

# ------------------------
# USER TYPE
# ------------------------
profile = st.selectbox(
    "Select User Profile",
    ["Gig Worker", "Salaried", "Student / Informal"]
)

st.divider()

st.markdown("### 📊 Behavioral Inputs")

transactions = st.slider("Monthly Transactions", 0, 300, 100)
recharge = st.slider("Recharge Frequency", 0, 20, 5)
location = st.slider("Location Stability", 0.0, 1.0, 0.5)

cash_in = st.number_input("Monthly Cash Inflow (₹)", 0, 200000, 30000)
cash_out = st.number_input("Monthly Cash Outflow (₹)", 0, 200000, 25000)

p2p = st.slider("Peer-to-Peer Transfers (UPI)", 0, 100, 20)
bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6)
savings = st.slider("Savings Ratio", 0.0, 1.0, 0.2)

# ------------------------
# SCORING LOGIC
# ------------------------
score = 300

# Basic signals
score += min(transactions * 1.5, 150)
score += min(recharge * 5, 100)
score += int(location * 150)

# Cash flow health
if cash_in > 0:
    ratio = cash_out / cash_in
    if ratio < 0.7:
        score += 120
    elif ratio < 1:
        score += 80
    else:
        score -= 50

# P2P behavior
score += min(p2p * 1.5, 100)

# Bill discipline
score += int(bill_pay * 150)

# Savings behavior
score += int(savings * 150)

# Profile adjustments
if profile == "Gig Worker":
    score += 20
elif profile == "Student / Informal":
    score -= 20

score = max(300, min(score, 900))

# Risk
if score > 750:
    risk = "Low"
elif score > 600:
    risk = "Medium"
else:
    risk = "High"

# ------------------------
# OUTPUT
# ------------------------
st.divider()

st.subheader("📊 Results")

st.metric("Credit Score", score)
st.metric("Risk Level", risk)

# Insight engine
st.markdown("###  AI Insights")

insights = []

if cash_out > cash_in:
    insights.append("Spending exceeds income → high financial stress")

if savings < 0.2:
    insights.append("Low savings buffer")

if bill_pay > 0.7:
    insights.append("Strong bill payment discipline")

if location > 0.7:
    insights.append("High location stability")

if p2p > 40:
    insights.append("Strong peer network activity")

for i in insights:
    st.write("- " + i)

if not insights:
    st.write("Behavior appears neutral with no strong signals.")

st.divider()

st.markdown("### 🔍 Model Note")
st.write(
    "This prototype evaluates behavioral signals instead of traditional credit history to assess creditworthiness."
)
