import streamlit as st
import pandas as pd
import numpy as np
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AltScore AI", layout="wide")

st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine")

st.markdown("---")

if "start" not in st.session_state:
    st.session_state.start = False

if st.button("🚀 Click to Assess Creditworthiness"):
    st.session_state.start = True

if not st.session_state.start:
    st.stop()

profile = st.selectbox("Select Profile", ["Gig Worker", "Salaried", "Informal"])

primary_income = 0
secondary_income = 0

if profile == "Gig Worker":

    st.markdown("## 👷 Gig Worker Details")

    sub_profile = st.selectbox(
        "Select Category",
        ["Delivery Agent", "Driver Partner", "Service Professional"]
    )

    if sub_profile == "Delivery Agent":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 20000)
        cv = st.slider("Earnings volatility (CV)", 0.0, 1.0, 0.3)

    elif sub_profile == "Driver Partner":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 25000)
        cv = 0.3

    elif sub_profile == "Service Professional":
        primary_income = st.number_input("Monthly revenue (₹)", 0, 200000, 40000)
        cv = 0.2

    st.markdown("### 🌐 Cross Platform Signals")

    secondary_income = st.number_input("Income from other platforms (₹)", 0, 200000, 10000)

    total_income = primary_income + secondary_income

else:
    total_income = st.number_input("Monthly income (₹)", 0, 200000, 30000)
    cv = 0.3

st.markdown("---")
st.markdown("## 💰 Expenses")

fixed_obligations = st.number_input("Fixed obligations (EMI, rent)", 0, 200000, 10000)
other_expenses = st.number_input("Other expenses", 0, 200000, 15000)

total_expenses = fixed_obligations + other_expenses

# ------------------------
# NEW CALCULATIONS (YOUR REQUEST)
# ------------------------
avg_income = total_income
avg_expenses = total_expenses
avg_savings = avg_income - avg_expenses
savings_ratio = (avg_savings / avg_income) if avg_income > 0 else 0

st.markdown("### 📊 Monthly Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Avg Monthly Income", int(avg_income))
c2.metric("Avg Monthly Expenses", int(avg_expenses))
c3.metric("Avg Monthly Savings", int(avg_savings))

# ------------------------
# BEHAVIORAL
# ------------------------
st.markdown("---")
st.markdown("## 📊 Behavioral Signals")
st.caption("Extracted from CSV File")

transactions = st.slider("Transactions", 0, 300, 100)
st.caption("Higher transactions = more financial activity")

savings = savings_ratio
st.caption("Savings Ratio = Savings / Income. Higher is safer")

bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6)
st.caption("Higher means more reliable bill payments")

p2p = st.slider("UPI transfers", 0, 100, 20)
st.caption("High transfers indicate active financial behavior")

location = st.slider("Location stability", 0.0, 1.0, 0.7)
st.caption("Higher means stable living pattern")

# ------------------------
# RESULT BUTTON
# ------------------------
if st.button("🔍 Check Credit Score"):

    foir = fixed_obligations / avg_income if avg_income > 0 else 0

    stability = max(0, 1 - cv)
    frequency = min(transactions / 200, 1)
    cf = max(0, 1 - (avg_expenses / avg_income)) if avg_income > 0 else 0.5

    diversification = 0.5

    score = 300
    score += int(200 * stability)
    score += int(150 * frequency)
    score += int(150 * cf)
    score += int(150 * savings)
    score += int(150 * bill_pay)
    score += int(100 * diversification)

    if foir < 0.4:
        score += 100
    elif foir < 0.6:
        score += 40
    else:
        score -= 100

    score = max(300, min(score, 900))

    # ------------------------
    # RESULTS UI (IMPROVED)
    # ------------------------
    st.markdown("---")
    st.markdown("## 📊 Check Credit Score")

    r1, r2, r3 = st.columns(3)
    r1.metric("Credit Score", score)
    r2.metric("FOIR", round(foir, 2))
    r3.metric("Savings Ratio", round(savings_ratio, 2))

    if score > 750:
        st.success("Low Risk")
        risk = "Low"
    elif score > 600:
        st.warning("Medium Risk")
        risk = "Medium"
    else:
        st.error("High Risk")
        risk = "High"

    # ------------------------
    # UNDERWRITING SIGNALS (RESTORED)
    # ------------------------
    st.markdown("### 🧠 Underwriting Signals")

    u1, u2, u3 = st.columns(3)
    u1.metric("Stability Score", round(stability, 2))
    u2.metric("Income Frequency", round(frequency, 2))
    u3.metric("Cash Flow Score", round(cf, 2))

    # ------------------------
    # AI ANALYSIS (RESTORED FORMAT)
    # ------------------------
    st.markdown("### 🤖 Detailed AI Analysis")

    st.write(f"""
    This borrower shows a stability score of {round(stability,2)} and income volatility (CV) of {round(cv,2)}.
    Income consistency is {'strong' if frequency > 0.6 else 'weak'}, with average gaps of 10 days.
    FOIR is {round(foir,2)}, indicating {'low' if foir < 0.4 else 'high'} financial stress.
    Overall risk is classified as {risk}.
    """)

    # ------------------------
    # PDF
    # ------------------------
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AltScore Report", styles['Title']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Score: {score}", styles['Normal']))
    content.append(Paragraph(f"FOIR: {round(foir,2)}", styles['Normal']))
    content.append(Paragraph(f"Savings Ratio: {round(savings_ratio,2)}", styles['Normal']))

    doc.build(content)

    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download Report", f, file_name="AltScore_Report.pdf")
