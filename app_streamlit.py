import streamlit as st

st.set_page_config(page_title="AltScore AI", layout="centered")

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("AI-powered alternative credit scoring | Built via vibe coding")

st.subheader("Assess creditworthiness using behavioral signals")

# ------------------------
# START FLOW (USER JOURNEY)
# ------------------------
start = st.button("🚀 Assess Creditworthiness")

if not start:
    st.info("Click the button to begin credit assessment")
    st.stop()

# ------------------------
# USER PROFILE
# ------------------------
profile = st.selectbox(
    "Select User Profile",
    ["Gig Worker", "Salaried", "Student / Informal"]
)

st.divider()

st.markdown("### 📊 Behavioral Inputs")

# ------------------------
# INPUTS
# ------------------------
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

# ------------------------
# RISK CLASSIFICATION
# ------------------------
if score > 750:
    risk = "Low"
elif score > 600:
    risk = "Medium"
else:
    risk = "High"

# ------------------------
# RESULTS
# ------------------------
st.divider()

st.subheader("📊 Results")

st.metric("Credit Score", score)
st.metric("Risk Level", risk)

# Progress bar (visual polish)
st.progress(score / 900)

# ------------------------
# LOAN ELIGIBILITY
# ------------------------
if score > 750:
    loan = "₹2,00,000 - ₹5,00,000"
    rate = "10% - 14%"
elif score > 600:
    loan = "₹50,000 - ₹2,00,000"
    rate = "14% - 20%"
else:
    loan = "₹0 - ₹50,000"
    rate = "20%+"

st.markdown("### 💰 Loan Eligibility")
st.write("Eligible Amount:", loan)
st.write("Estimated Interest Rate:", rate)

# ------------------------
# SCORE BREAKDOWN
# ------------------------
st.markdown("### 📊 Score Breakdown")

st.write("Transactions Contribution:", min(transactions * 1.5, 150))
st.write("Cash Flow Health:", "Good" if cash_out < cash_in else "Poor")
st.write("Savings Impact:", int(savings * 150))
st.write("Bill Discipline:", int(bill_pay * 150))

# ------------------------
# AI INSIGHTS
# ------------------------
st.markdown("### 🧠 AI Insights")

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

# ------------------------
# PERSONALIZED INSIGHT
# ------------------------
st.markdown("### 🎯 Personalized Insight")

if profile == "Gig Worker":
    st.write("Your income variability is considered — consistent behavior improves your score.")
elif profile == "Salaried":
    st.write("Stable income enhances your creditworthiness.")
else:
    st.write("Building financial discipline can improve your future credit access.")

# ------------------------
# DOWNLOAD REPORT
# ------------------------
report = f"""
AltScore AI Report

Profile: {profile}
Score: {score}
Risk: {risk}

Loan Eligibility: {loan}
Interest Rate: {rate}
"""

st.download_button("📄 Download Report", report)

# ------------------------
# TRUST LAYER
# ------------------------
st.divider()

st.markdown("### 🔒 Data Privacy")
st.caption(
    "This prototype uses simulated data. In production, all user data would be encrypted and processed securely."
)

# ------------------------
# MODEL NOTE
# ------------------------
st.markdown("### 🔍 Model Note")
st.write(
    "This system evaluates behavioral signals instead of traditional credit history to assess creditworthiness."
)
