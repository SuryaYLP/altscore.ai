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

.signal-card {
    background: #f8fbff;
    border: 1px solid #d9e8f5;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.analysis-box {
    background: #f4f9f4;
    border-left: 6px solid #2e7d32;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
    color: #1f1f1f;
}

.risk-box {
    background: #fff8e1;
    border-left: 6px solid #f9a825;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
    color: #1f1f1f;
}

.metric-box {
    background: #f8fbff;
    border: 1px solid #d9e8f5;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
}
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
avg_monthly_income = total_income
avg_monthly_total_expenses = total_expenses
avg_monthly_savings = avg_monthly_income - avg_monthly_total_expenses

# ------------------------
# BEHAVIORAL
# ------------------------
st.markdown("---")
st.markdown("## 📊 Behavioral Signals")
st.caption("Extracted from CSV File")

transactions = st.slider("Transactions", 0, 300, 100)
st.caption("Total number of monthly financial transactions observed in the account.")

savings = (avg_monthly_savings / avg_monthly_income) if avg_monthly_income > 0 else 0
st.write(f"Savings Ratio: {round(savings, 2)}")
st.caption("Savings Ratio = Avg Monthly Savings / Avg Monthly Income")

bill_pay = st.slider("Bill payment consistency", 0.0, 1.0, 0.6)
st.caption("Shows how regularly the borrower pays recurring bills on time.")

p2p = st.slider("UPI transfers", 0, 100, 20)
st.caption("Represents the volume of peer-to-peer UPI transfers in a month.")

location = st.slider("Location stability", 0.0, 1.0, 0.7)
st.caption("Indicates how stable the borrower’s work or residence location is over time.")

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
    avg_gap_days = round(30 / transactions, 1) if transactions > 0 else 30

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

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Score", score)
    col2.metric("FOIR", round(foir, 2))
    col3.metric("Avg Monthly Total Income", f"₹{avg_monthly_income}")
    col4.metric("Avg Monthly Total Expenses", f"₹{avg_monthly_total_expenses}")
    col5.metric("Avg Monthly Savings", f"₹{avg_monthly_savings}")

    # ------------------------
    # UNDERWRITING SIGNALS
    # ------------------------
    st.markdown("### 🧠 Underwriting Signals")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="signal-card">
            <h4>Stability Score</h4>
            <p style="font-size:24px; font-weight:600; color:#1f4e79;">{round(stability,2)}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="signal-card">
            <h4>Income Frequency</h4>
            <p style="font-size:24px; font-weight:600; color:#1f4e79;">{round(frequency,2)}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="signal-card">
            <h4>Cash Flow Score</h4>
            <p style="font-size:24px; font-weight:600; color:#1f4e79;">{round(cf,2)}</p>
        </div>
        """, unsafe_allow_html=True)

    # ------------------------
    # RISK SIGNALS
    # ------------------------
    st.markdown("### ⚠️ Risk Signals")
    st.markdown(f"""
    <div class="risk-box">
        <p><strong>Risk Level:</strong> {risk}</p>
        <p><strong>FOIR:</strong> {round(foir,2)}</p>
        <p><strong>Income Volatility (CV):</strong> {round(cv,2)}</p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------
    # AI ANALYSIS
    # ------------------------
    st.markdown("### 🤖 Detailed AI Analysis")

    st.markdown(f"""
    <div class="analysis-box">
        <p>This borrower shows a <strong>stability score of {round(stability,2)}</strong> and income volatility (CV) of <strong>{round(cv,2)}</strong>.</p>
        <p>Income consistency is <strong>{'strong' if frequency > 0.6 else 'weak'}</strong>, with average gaps of <strong>{avg_gap_days} days</strong>.</p>
        <p>FOIR is <strong>{round(foir,2)}</strong>, indicating <strong>{'low' if foir < 0.4 else 'high'}</strong> financial stress.</p>
        <p>Overall risk is classified as <strong>{risk}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

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
