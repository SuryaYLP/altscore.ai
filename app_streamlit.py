import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="AltScore AI", layout="wide")

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("AI-powered alternative credit scoring | Built via vibe coding")

st.markdown("---")

# ------------------------
# SESSION STATE (FIX)
# ------------------------
if "started" not in st.session_state:
    st.session_state.started = False

if st.button("🚀 Assess Creditworthiness"):
    st.session_state.started = True

if not st.session_state.started:
    st.info("Click the button to begin credit assessment")
    st.stop()

# ------------------------
# PROFILE
# ------------------------
profile = st.selectbox(
    "Select User Profile",
    ["Gig Worker", "Salaried", "Student / Informal"]
)

st.markdown("---")

# ------------------------
# LAYOUT (2 COLUMNS)
# ------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Behavioral Inputs")

    transactions = st.slider("Monthly Transactions", 0, 300, 100)
    recharge = st.slider("Recharge Frequency", 0, 20, 5)
    location = st.slider("Location Stability", 0.0, 1.0, 0.5)

    p2p = st.slider("Peer-to-Peer Transfers (UPI)", 0, 100, 20)
    bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6)
    savings = st.slider("Savings Ratio", 0.0, 1.0, 0.2)

with col2:
    st.markdown("### 💰 Financial Inputs")

    cash_in = st.number_input("Monthly Cash Inflow (₹)", 0, 200000, 30000)
    cash_out = st.number_input("Monthly Cash Outflow (₹)", 0, 200000, 25000)

    st.markdown("### 📂 Upload Bank Statement")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.dataframe(df.head(), height=150)

        if "amount" in df.columns:
            cash_in = df[df["amount"] > 0]["amount"].sum()
            cash_out = abs(df[df["amount"] < 0]["amount"].sum())

            st.success(f"Inflow detected: ₹{int(cash_in)}")
            st.success(f"Outflow detected: ₹{int(cash_out)}")

# ------------------------
# SCORING (ML-LIKE)
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

st.markdown("---")

# ------------------------
# RESULTS (3 COLUMNS)
# ------------------------
r1, r2, r3 = st.columns(3)

r1.metric("💳 Credit Score", score)
r2.metric("⚠️ Risk Level", risk)

if score > 750:
    loan = "₹2L - ₹5L"
    rate = "10% - 14%"
elif score > 600:
    loan = "₹50K - ₹2L"
    rate = "14% - 20%"
else:
    loan = "₹0 - ₹50K"
    rate = "20%+"

r3.metric("💰 Loan Range", loan)

st.progress(score / 900)

# ------------------------
# BREAKDOWN + INSIGHTS (2 COL)
# ------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown("### 📊 Score Breakdown")

    st.write("Transactions:", int(150 * t_norm))
    st.write("Savings:", int(150 * s_norm))
    st.write("Bill Discipline:", int(150 * b_norm))
    st.write("Cash Flow Score:", round(cf_score, 2))

with c2:
    st.markdown("### 🧠 AI Analysis")

    analysis = f"""
Profile: {profile}

Cash Flow Ratio: {round(cash_out / cash_in, 2) if cash_in > 0 else "N/A"}

Observations:
"""

    if cash_out > cash_in:
        analysis += "\n- Spending exceeds income"
    else:
        analysis += "\n- Healthy cash flow"

    if savings < 0.2:
        analysis += "\n- Low savings buffer"

    if bill_pay > 0.7:
        analysis += "\n- Strong repayment discipline"

    if location > 0.7:
        analysis += "\n- Stable behavior"

    if p2p > 40:
        analysis += "\n- Active financial network"

    st.code(analysis)

# ------------------------
# PERSONALIZATION
# ------------------------
st.markdown("### 🎯 Personalized Insight")

if profile == "Gig Worker":
    st.info("Income variability considered — consistency improves score")
elif profile == "Salaried":
    st.info("Stable income boosts your credit profile")
else:
    st.info("Improving discipline will unlock credit access")

# ------------------------
# RISK FLAGS
# ------------------------
st.markdown("### 🚨 Risk Signals")

if transactions > 250 and savings < 0.1:
    st.warning("High transactions + low savings")

if cash_in == 0:
    st.error("No income detected")

# ------------------------
# DOWNLOAD
# ------------------------
report = f"""
AltScore Report

Score: {score}
Risk: {risk}
Loan: {loan}
Rate: {rate}
"""

st.download_button("📄 Download Report", report)

# ------------------------
# FOOTER
# ------------------------
st.markdown("---")

st.caption("🔒 Data is simulated. Production systems would use secure pipelines.")

# Reset button
if st.button("🔄 Reset"):
    st.session_state.started = False
