import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="AltScore AI", layout="centered")

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("AI-powered alternative credit scoring | Built via vibe coding")

st.subheader("Assess creditworthiness using behavioral signals")

# ------------------------
# START FLOW
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
# DEFAULT INPUTS
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
# FILE UPLOAD
# ------------------------
st.markdown("### 📂 Upload Bank Statement (Optional)")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("Preview of uploaded data:")
    st.dataframe(df.head())

    if "amount" in df.columns:
        cash_in = df[df["amount"] > 0]["amount"].sum()
        cash_out = abs(df[df["amount"] < 0]["amount"].sum())

        st.success(f"Detected Cash Inflow: ₹{int(cash_in)}")
        st.success(f"Detected Cash Outflow: ₹{int(cash_out)}")

# ------------------------
# ML-LIKE SCORING
# ------------------------
score = 300

t_norm = min(transactions / 200, 1)
r_norm = min(recharge / 10, 1)
l_norm = location
s_norm = savings
b_norm = bill_pay
p_norm = min(p2p / 50, 1)

if cash_in > 0:
    cf_ratio = cash_out / cash_in
    cf_score = max(0, 1 - cf_ratio)
else:
    cf_score = 0.5

score += int(150 * t_norm)
score += int(100 * r_norm)
score += int(150 * l_norm)
score += int(150 * s_norm)
score += int(150 * b_norm)
score += int(100 * p_norm)
score += int(150 * cf_score)

if cash_out > cash_in:
    score -= int(100 * math.log(cash_out - cash_in + 1))

if profile == "Gig Worker":
    score += 10
elif profile == "Student / Informal":
    score -= 10

score = max(300, min(score, 900))

# ------------------------
# RISK
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
# BREAKDOWN
# ------------------------
st.markdown("### 📊 Score Breakdown")

st.write("Transactions Contribution:", int(150 * t_norm))
st.write("Savings Contribution:", int(150 * s_norm))
st.write("Bill Discipline Contribution:", int(150 * b_norm))
st.write("Cash Flow Score:", round(cf_score, 2))

# ------------------------
# AI ANALYSIS
# ------------------------
st.markdown("### AI Analysis")

analysis = f"""
User Profile: {profile}

Financial Behavior Summary:
- Cash flow ratio: {round(cash_out / cash_in, 2) if cash_in > 0 else "N/A"}
- Savings ratio: {round(savings, 2)}
- Bill discipline: {round(bill_pay, 2)}

Key Observations:
"""

if cash_out > cash_in:
    analysis += "\n- Spending exceeds income → financial stress."
else:
    analysis += "\n- Positive cash flow indicates stability."

if savings < 0.2:
    analysis += "\n- Low savings buffer."

if bill_pay > 0.7:
    analysis += "\n- Strong repayment discipline."

if location > 0.7:
    analysis += "\n- Stable location behavior."

if p2p > 40:
    analysis += "\n- Strong peer network activity."

analysis += "\n\nRecommendation: "

if score > 750:
    analysis += "Eligible for premium lending."
elif score > 600:
    analysis += "Moderate risk — controlled lending."
else:
    analysis += "High risk — limited lending."

st.code(analysis)

# ------------------------
# PERSONALIZED INSIGHT
# ------------------------
st.markdown("### 🎯 Personalized Insight")

if profile == "Gig Worker":
    st.write("Income variability is accounted — consistency improves your score.")
elif profile == "Salaried":
    st.write("Stable income boosts your creditworthiness.")
else:
    st.write("Improving discipline can unlock future credit access.")

# ------------------------
# FRAUD SIGNALS
# ------------------------
st.markdown("### 🚨 Risk Signals")

if transactions > 250 and savings < 0.1:
    st.warning("High transactions + low savings → potential risk")

if cash_in == 0:
    st.error("No income detected → high default risk")

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
st.caption("Prototype only. Production systems would use encrypted, secure processing.")

# ------------------------
# MODEL NOTE
# ------------------------
st.markdown("### 🔍 Model Note")
st.write("This system evaluates behavioral signals instead of traditional credit history.")
