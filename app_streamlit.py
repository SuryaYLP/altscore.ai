import streamlit as st
import pandas as pd
import numpy as np
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AltScore AI", layout="wide")

# ------------------------
# UI STYLE
# ------------------------
st.markdown("""
<style>
body {background-color: white;}
h1, h2, h3 {color: #1f4e79;}
</style>
""", unsafe_allow_html=True)

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine")

st.markdown("---")

# ------------------------
# SESSION START BUTTON
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

# ------------------------
# GIG SEGMENTATION
# ------------------------
primary_income = 0

if profile == "Gig Worker":

    st.markdown("## 👷 Gig Worker Details")

    sub_profile = st.selectbox(
        "Select Category",
        ["Delivery Agent", "Driver Partner", "Service Professional"]
    )

    # ---------------- DELIVERY ----------------
    if sub_profile == "Delivery Agent":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 20000)
        cv = st.slider("Earnings volatility (CV)", 0.0, 1.0, 0.3)
        tenure = st.slider("Platform tenure (months)", 0, 60, 12)
        completion = st.slider("Order completion rate", 0.0, 1.0, 0.9)
        seasonality = st.slider("Income seasonality", 0.0, 1.0, 0.3)
        rating_trend = st.slider("Rating trend", -1.0, 1.0, 0.2)
        active_days = st.slider("Active days/month", 0, 30, 20)

    # ---------------- DRIVER ----------------
    elif sub_profile == "Driver Partner":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 25000)
        weekly_trend = st.slider("Weekly earnings trend", -1.0, 1.0, 0.1)
        cancel_rate = st.slider("Cancellation rate", 0.0, 1.0, 0.1)
        tenure = st.slider("Platform tenure (months)", 0, 60, 18)
        rating = st.slider("Driver rating", 1.0, 5.0, 4.5)
        acceptance = st.slider("Acceptance rate", 0.0, 1.0, 0.8)
        ownership = st.selectbox("Vehicle ownership", ["Owned", "EMI", "Rented"])
        surge = st.slider("Surge participation", 0.0, 1.0, 0.5)
        cv = 0.3

    # ---------------- SERVICE ----------------
    elif sub_profile == "Service Professional":
        primary_income = st.number_input("Monthly revenue (₹)", 0, 200000, 40000)
        completion = st.slider("Job completion rate", 0.0, 1.0, 0.9)
        repeat = st.slider("Repeat customer rate", 0.0, 1.0, 0.5)
        growth = st.slider("Revenue growth", -0.5, 1.0, 0.1)
        rating_volume = st.slider("Rating × volume", 0.0, 1.0, 0.7)
        upskilling = st.slider("Certification level", 0.0, 1.0, 0.6)
        breadth = st.slider("Category breadth", 0.0, 1.0, 0.5)
        cv = 0.2

    # ---------------- CROSS PLATFORM ----------------
    st.markdown("### 🌐 Cross Platform Signals")

    secondary_income = st.number_input("Income from other platforms (₹)", 0, 200000, 10000)
    platform_count = st.slider("Number of platforms", 1, 5, 2)
    active_months = st.slider("Consecutive active months", 0, 60, 12)
    yoy_growth = st.slider("YoY growth", -50, 100, 10)
    reconciliation = st.slider("Income reconciliation score", 0.0, 1.0, 0.8)

    total_income = primary_income + secondary_income

else:
    total_income = st.number_input("Monthly income (₹)", 0, 200000, 30000)
    cv = 0.3

# ------------------------
# EXPENSES
# ------------------------
st.markdown("---")
st.markdown("## 💰 Expenses")

fixed_obligations = st.number_input("Fixed obligations (EMI, rent)", 0, 200000, 10000)
other_expenses = st.number_input("Other expenses", 0, 200000, 15000)

total_expenses = fixed_obligations + other_expenses

# ------------------------
# BEHAVIORAL
# ------------------------
st.markdown("---")
st.markdown("## 📊 Behavioral Signals")

transactions = st.slider("Transactions", 0, 300, 100)
savings = st.slider("Savings ratio", 0.0, 1.0, 0.2)
bill_pay = st.slider("Bill payment consistency", 0.0, 1.0, 0.6)
p2p = st.slider("UPI transfers", 0, 100, 20)
location = st.slider("Location stability", 0.0, 1.0, 0.7)

# ------------------------
# RESULT BUTTON
# ------------------------
if st.button("🔍 Check Credit Score"):

    # ------------------------
    # FEATURE ENGINEERING
    # ------------------------
    foir = fixed_obligations / total_income if total_income > 0 else 0

    stability = max(0, 1 - cv)
    frequency = min(transactions / 200, 1)
    cf = max(0, 1 - (total_expenses / total_income)) if total_income > 0 else 0.5

    diversification = min(platform_count / 3, 1) if profile == "Gig Worker" else 0.5

    # ------------------------
    # SCORE
    # ------------------------
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
    # RISK
    # ------------------------
    if score > 750:
        risk = "Low"
        st.success("Low Risk")
    elif score > 600:
        risk = "Medium"
        st.warning("Medium Risk")
    else:
        risk = "High"
        st.error("High Risk")

    # ------------------------
    # RESULTS
    # ------------------------
    st.markdown("---")
    st.markdown("## 📊 Check Credit Score")

    st.metric("Score", score)
    st.metric("FOIR", round(foir, 2))

    # ------------------------
    # UNDERWRITING SIGNALS
    # ------------------------
    st.markdown("### 🧠 Underwriting Signals")
    st.write("Stability Score:", round(stability,2))
    st.write("Income Frequency:", round(frequency,2))
    st.write("Cash Flow Score:", round(cf,2))

    # ------------------------
    # AI ANALYSIS
    # ------------------------
    st.markdown("### 🤖 Detailed AI Analysis")

    st.write(f"""
    This borrower shows a stability score of {round(stability,2)} and income volatility (CV) of {round(cv,2)}.
    Income consistency is {'strong' if frequency > 0.6 else 'weak'}.
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
    content.append(Paragraph(f"Risk: {risk}", styles['Normal']))
    content.append(Paragraph(f"FOIR: {round(foir,2)}", styles['Normal']))

    doc.build(content)

    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download Report", f, file_name="AltScore_Report.pdf")

