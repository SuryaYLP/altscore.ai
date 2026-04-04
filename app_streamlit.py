import streamlit as st
import pandas as pd
import numpy as np
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AltScore AI", layout="wide")

# ------------------------
# STYLE
# ------------------------
st.markdown("""
<style>
h1, h2, h3 {color:#1f4e79;}
.block {padding:15px; border-radius:10px; background:#f5f9ff;}
</style>
""", unsafe_allow_html=True)

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine")

st.markdown("---")

# ------------------------
# START BUTTON
# ------------------------
if "start" not in st.session_state:
    st.session_state.start = False

if st.button("🚀 Click to Assess Creditworthiness"):
    st.session_state.start = True

if not st.session_state.start:
    st.stop()

# ------------------------
# PROFILE
# ------------------------
profile = st.selectbox("Select Profile", ["Gig Worker", "Salaried", "Informal"])

primary_income = 0
secondary_income = 0

# ------------------------
# GIG WORKER INPUTS
# ------------------------
if profile == "Gig Worker":

    st.markdown("## 👷 Gig Worker Details")

    sub_profile = st.selectbox(
        "Category",
        ["Delivery Agent", "Driver Partner", "Service Professional"]
    )

    primary_income = st.number_input("Primary platform income (₹)", 0, 200000, 20000)
    secondary_income = st.number_input("Income from other platforms (₹)", 0, 200000, 10000)

    cv = st.slider("Earnings volatility (CV)", 0.0, 1.0, 0.3)
    tenure = st.slider("Platform tenure (months)", 0, 60, 12)

    st.markdown("### 🌐 Cross Platform Signals")
    platform_count = st.slider("Number of platforms", 1, 5, 2)
    active_months = st.slider("Active months", 0, 60, 12)

    total_income = primary_income + secondary_income

else:
    total_income = st.number_input("Monthly income (₹)", 0, 200000, 30000)
    cv = 0.3
    platform_count = 1

# ------------------------
# EXPENSES
# ------------------------
st.markdown("---")
st.markdown("## 💰 Expenses")

fixed_obligations = st.number_input("Fixed obligations (₹)", 0, 200000, 10000)
other_expenses = st.number_input("Other expenses (₹)", 0, 200000, 15000)

total_expenses = fixed_obligations + other_expenses
savings_amount = total_income - total_expenses
savings_ratio = savings_amount / total_income if total_income > 0 else 0

# ------------------------
# CSV UPLOAD
# ------------------------
st.markdown("---")
st.markdown("## 📂 Bank Statement (Optional)")

uploaded_file = st.file_uploader("Upload CSV")

avg_gap = 10

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    cols = [c.lower() for c in df.columns]

    amount_col = df.columns[cols.index("amount")] if "amount" in cols else df.columns[-1]
    date_col = df.columns[cols.index("date")] if "date" in cols else df.columns[0]

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values(date_col)

    credits = df[df[amount_col] > 0][amount_col]

    if len(credits) > 1:
        gaps = df[df[amount_col] > 0][date_col].diff().dt.days.dropna()
        avg_gap = gaps.mean()

# ------------------------
# BEHAVIOR SIGNALS
# ------------------------
st.markdown("---")
st.markdown("## 📊 Behavioral Signals")
st.caption("Extracted from CSV File")

transactions = st.slider("Transactions", 0, 300, 100,
                         help="Number of financial activities. Higher = more active")

bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6,
                     help="Measures how consistently bills are paid")

p2p = st.slider("UPI Transfers", 0, 100, 20,
                help="Peer transfers frequency")

location = st.slider("Location Stability", 0.0, 1.0, 0.7,
                     help="How stable user location is over time")

st.caption("Savings Ratio = Avg Monthly Savings / Avg Monthly Income")

# ------------------------
# RESULT BUTTON
# ------------------------
if st.button("🔍 Check Credit Score"):

    foir = fixed_obligations / total_income if total_income > 0 else 0

    stability = max(0, 1 - cv)
    frequency = min(transactions / 200, 1)
    cf = max(0, 1 - (total_expenses / total_income)) if total_income > 0 else 0.5

    diversification = min(platform_count / 3, 1)

    # ---------------- SCORE ----------------
    score = 300
    score += int(200 * stability)
    score += int(150 * frequency)
    score += int(150 * cf)
    score += int(150 * savings_ratio)
    score += int(100 * diversification)

    if foir < 0.4:
        score += 100
    elif foir < 0.6:
        score += 40
    else:
        score -= 100

    score = max(300, min(score, 900))

    # ---------------- RISK ----------------
    if score > 750:
        risk = "Low"
        color = "green"
    elif score > 600:
        risk = "Medium"
        color = "orange"
    else:
        risk = "High"
        color = "red"

    # ---------------- RESULTS UI ----------------
    st.markdown("---")
    st.markdown("## 📊 Credit Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Credit Score", score)
    c2.metric("Risk Level", risk)
    c3.metric("FOIR", round(foir, 2))

    st.progress(score / 900)

    # ---------------- INCOME BREAKDOWN ----------------
    st.markdown("### 💰 Financial Summary")

    f1, f2, f3 = st.columns(3)
    f1.metric("Avg Monthly Income", int(total_income))
    f2.metric("Avg Monthly Expenses", int(total_expenses))
    f3.metric("Avg Monthly Savings", int(savings_amount))

    # ---------------- UNDERWRITING ----------------
    st.markdown("### 🧠 Underwriting Signals")

    u1, u2, u3 = st.columns(3)
    u1.metric("Stability Score", round(stability,2))
    u2.metric("Income Frequency", round(frequency,2))
    u3.metric("Cash Flow Score", round(cf,2))

    # ---------------- RISK SIGNALS ----------------
    st.markdown("### 🚨 Risk Signals")

    if cv > 0.5:
        st.error("High income volatility")

    if foir > 0.6:
        st.error("High debt burden")

    if total_expenses > total_income:
        st.error("Negative cash flow")

    # ---------------- AI ANALYSIS ----------------
    st.markdown("### 🤖 Detailed AI Analysis")

    st.write(f"""
    This borrower shows a stability score of {round(stability,2)} and income volatility (CV) of {round(cv,2)}.
    Income consistency is {'strong' if frequency > 0.6 else 'weak'}, with average gaps of {int(avg_gap)} days.
    FOIR is {round(foir,2)}, indicating {'low' if foir < 0.4 else 'high'} financial stress.
    Overall risk is classified as {risk}.
    """)

    # ---------------- PDF ----------------
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AltScore Report", styles['Title']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Score: {score}", styles['Normal']))
    content.append(Paragraph(f"Risk: {risk}", styles['Normal']))
    content.append(Paragraph(f"FOIR: {round(foir,2)}", styles['Normal']))

    doc.build(content)

    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download Report", f, file_name="AltScore_Report.pdf")
