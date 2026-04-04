import streamlit as st
import pandas as pd
import numpy as np
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
        ["Delivery Agent", "Driver Partner", "Service Professional", "Blue Collar / Others"]
    )

    # ---------------- DELIVERY ----------------
    if sub_profile == "Delivery Agent":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 15000)
        cv = st.slider("Earnings volatility / CV (Coefficient of Variation): 0-Stable Earnings, 1-Highly Volatile ", 0.0, 1.0, 0.3)
        tenure = st.slider("Platform tenure (months)", 0, 60, 42)
        completion = st.slider("Order completion rate: 1-All orders fulfilled", 0.0, 1.0, 0.9)
        seasonality = st.slider("Income seasonality: 0-Regular Income, 1-Seasonal Income", 0.0, 1.0, 0.3)
        rating_trend = st.slider("Rating trend: 0-Lowest Rating, 1-Highest Rating", 0.0, 1.0, 0.2)
        active_days = st.slider("Active days per month", 0, 30, 22)

    # ---------------- DRIVER ----------------
    elif sub_profile == "Driver Partner":
        primary_income = st.number_input("Monthly payout (₹)", 0, 200000, 25000)
        cv = st.slider("Income Stability / CV (Coefficient of Variation): 0-Stable Earnings, 1-Highly Volatile ", 0.0, 1.0, 0.3)
        weekly_trend = st.slider("Weekly earnings trend: Rolling 4-week income growth or decline", -1.0, 1.0, 0.5)
        cancel_rate = st.slider("Ride aancellation rate", 0.0, 1.0, 0.1)
        tenure = st.slider("Platform tenure (months)", 0, 60, 18)
        rating = st.slider("Driver rating: 0-Lowest Rating, 5-Highest Rating", 1.0, 5.0, 4.5)
        acceptance = st.slider("Ride acceptance rate: 1-All rides are accepted", 0.0, 1.0, 0.8)
        ownership = st.selectbox("Vehicle ownership", ["Owned", "EMI", "Rented"])
        surge = st.slider("Surge participation", 0.0, 1.0, 0.5)

    # ---------------- SERVICE ----------------
    elif sub_profile == "Service Professional":
        primary_income = st.number_input("Monthly revenue (₹)", 0, 200000, 40000)
        completion = st.slider("Job completion rate", 0.0, 1.0, 0.9)
        repeat = st.slider("Repeat customer rate", 0.0, 1.0, 0.5)
        growth = st.slider("Weekly earnings trend: Rolling 4-week income growth or decline", -0.5, 1.0, 0.1)
        rating_volume = st.slider("Avg. rating in the last 4 weeks", 0.0, 1.0, 0.7)
        upskilling = st.slider("Certification level: 0-No upskilling in the last 1 year", 0.0, 1.0, 0.6)
        breadth = st.slider("Category breadth: 0.1 increment for every category ", 0.0, 1.0, 0.5)
        cv = st.slider("Income Stability / CV (Coefficient of Variation): 0-Stable Earnings, 1-Highly Volatile ", 0.0, 1.0, 0.2)

    # ---------------- BLUE COLLAR / OTHERS ----------------
    elif sub_profile == "Blue Collar / Others":
        primary_income = st.number_input("Monthly revenue (₹)", 0, 200000, 40000)
        growth = st.slider("Weekly earnings trend: Rolling 4-week income growth or decline", -0.5, 1.0, 0.1)
        seasonality = st.slider("Income seasonality: 0-Regular Income, 1-Seasonal Income", 0.0, 1.0, 0.3)
        cv = st.slider("Income Stability / CV (Coefficient of Variation): 0-Stable Earnings, 1-Highly Volatile ", 0.0, 1.0, 0.2)

    # ---------------- CROSS PLATFORM ----------------
    st.markdown("### 🌐 Cross Platform Signals")

    secondary_income = st.number_input("Monthly income from other platforms (₹)", 0, 200000, 10000)
    platform_count = st.slider("Number of platforms", 1, 5, 2)
    active_months = st.slider("Consecutive active months", 0, 60, 12)
    yoy_growth = st.slider("YoY growth across all platforms", -50, 100, 10)
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

fixed_obligations = st.number_input("Fixed obligations per month (EMI, rent)", 0, 200000, 10000)
other_expenses = st.number_input("Other expenses per month", 0, 200000, 15000)

total_expenses = fixed_obligations + other_expenses
total_savings = total_income - total_expenses

# ------------------------
# BEHAVIORAL
# ------------------------
st.markdown("---")
st.markdown("## 📊 Behavioral Signals")
st.caption("If CSV file is uploaded, these values are auto-filled. Otherwise, user can adjust manually.")

transactions = st.slider("Transactions", 0, 300, 100)
st.caption("Number of financial transactions. Higher = more active financial behavior.")
savings = st.slider("Savings ratio", 0.0, 1.0, 0.2)
st.caption("Savings Ratio = Monthly Savings / Monthly Income. Higher ratio indicates better financial discipline.")
bill_pay = st.slider("Bill payment consistency", 0.0, 1.0, 0.6)
st.caption("Measures how consistently bills are paid. Higher = more reliable borrower.")
upi = st.slider("UPI based transactions in a month", 0, 500, 20)
st.caption("UPI activity. Moderate activity is healthy; extremely high may indicate cash churn.")
p2p = st.slider("P2P transfers in a month", 0, 100, 20)
st.caption("Peer-to-peer transfers. Moderate activity is healthy; extremely high may indicate cash churn.")
location = st.slider("Location stability", 0.0, 1.0, 0.7)
st.caption("Indicates how stable the user's location is. Higher stability reduces default risk.")

# ------------------------
# RESULT BUTTON
# ------------------------
# ------------------------
# MONTHLY SUMMARY
# ------------------------
total_savings = total_income - total_expenses
savings = final_savings_ratio
calc_savings_ratio = (total_savings / total_income) if total_income > 0 else 0

# If user has moved slider, use that, else fallback
final_savings_ratio = savings if savings > 0 else calc_savings_ratio

st.markdown("### 📊 Monthly Summary")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Avg Monthly Income", int(total_income))
m2.metric("Avg Monthly Expenses", int(total_expenses))
m3.metric("Avg Monthly Savings", int(total_savings))
m4.metric("Savings Ratio", round(final_savings_ratio, 2))

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
# RESULTS SECTION (ENHANCED UI)
# ------------------------
st.markdown("---")
st.markdown("## 📊 Credit Assessment Results")

# Top Metrics
r1, r2, r3, r4 = st.columns(4)

r1.metric("Credit Score", score)
r2.metric("FOIR", round(foir, 2))
r3.metric("Savings Ratio", round(savings, 2))

# Loan eligibility (added back)
if score > 750:
    loan = "₹2L - ₹5L"
    rate = "10% - 14%"
elif score > 600:
    loan = "₹50K - ₹2L"
    rate = "14% - 20%"
else:
    loan = "₹0 - ₹50K"
    rate = "20%+"

r4.metric("Eligible Loan", loan)

st.progress(score / 900)

# ------------------------
# UNDERWRITING SIGNALS
# ------------------------
st.markdown("### 🧠 Underwriting Signals")

u1, u2, u3 = st.columns(3)

u1.metric("Stability Score", round(stability, 2))
u2.metric("Income Frequency", round(frequency, 2))
u3.metric("Cash Flow Score", round(cf, 2))

# ------------------------
# RISK SIGNALS
# ------------------------
st.markdown("### 🚨 Risk Signals")

if cv > 0.5:
    st.error("High income volatility detected")

if foir > 0.6:
    st.error("High debt burden")

if cf < 0.3:
    st.warning("Weak cash flow position")

if stability > 0.7:
    st.success("Stable income behavior")

# ------------------------
# INTERACTIVE VISUALS
# ------------------------
st.markdown("### 📈 Financial Insights")

import plotly.express as px
import pandas as pd

# Financial Breakdown Chart
finance_df = pd.DataFrame({
    "Category": ["Income", "Expenses", "Savings"],
    "Amount": [total_income, total_expenses, total_income - total_expenses]
})

fig1 = px.bar(
    finance_df,
    x="Category",
    y="Amount",
    color="Category",
    text="Amount",
    title="Income vs Expenses vs Savings"
)

fig1.update_layout(showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# Score Components Radar Chart
score_df = pd.DataFrame({
    "Metric": ["Stability", "Frequency", "Cash Flow", "Savings"],
    "Value": [stability, frequency, cf, savings]
})

fig2 = px.line_polar(
    score_df,
    r="Value",
    theta="Metric",
    line_close=True,
    title="Behavioral Score Profile"
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------------
# GPT AI ANALYSIS (LIVE)
# ------------------------
st.markdown("### 🤖 AI Credit Analysis")

with st.spinner("AI is analyzing borrower profile..."):

    try:
        prompt = f"""
        You are a credit risk analyst.

        Analyze this borrower:

        Income: {total_income}
        Expenses: {total_expenses}
        Savings Ratio: {round(savings,2)}
        FOIR: {round(foir,2)}
        Stability Score: {round(stability,2)}
        Frequency Score: {round(frequency,2)}
        Cash Flow Score: {round(cf,2)}

        Provide:
        1. Risk summary
        2. Key strengths
        3. Key risks
        4. Final recommendation

        Keep it professional, concise, and structured.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_output = response.choices[0].message.content

        st.markdown(ai_output)

    except Exception as e:
        st.warning("AI analysis unavailable, showing fallback")

        st.write(f"""
        Stability: {round(stability,2)}, FOIR: {round(foir,2)}.
        Moderate underwriting risk.
        """)
# ------------------------
# CONFIDENCE SCORE
# ------------------------
confidence = (
    0.25 * stability +
    0.20 * frequency +
    0.20 * cf +
    0.20 * (1 - foir) +
    0.15 * savings
)

confidence = max(0, min(confidence, 1))

st.markdown("### 🎯 Model Confidence")

if confidence > 0.75:
    st.success(f"High Confidence: {round(confidence,2)}")
elif confidence > 0.5:
    st.warning(f"Moderate Confidence: {round(confidence,2)}")
else:
    st.error(f"Low Confidence: {round(confidence,2)}")


# ------------------------
# ADVANCED AI ANALYSIS (for testing only)
# ------------------------
st.markdown("### 🤖 AI Credit Analysis")

analysis = []

# Stability
if stability > 0.7:
    analysis.append(f"Income stability is strong (score: {round(stability,2)}), indicating predictable earnings behavior.")
else:
    analysis.append(f"Income shows volatility (CV: {round(cv,2)}), which may impact repayment consistency.")

# Frequency
if frequency > 0.6:
    analysis.append("Income frequency is consistent, suggesting steady earning patterns.")
else:
    analysis.append("Income inflow is irregular, indicating potential gaps in earnings.")

# Cash Flow
if cf > 0.5:
    analysis.append("Cash flow position is healthy, with sufficient surplus after expenses.")
else:
    analysis.append("Cash flow is constrained, indicating limited financial buffer.")

# FOIR
if foir < 0.4:
    analysis.append(f"FOIR is {round(foir,2)}, reflecting low financial stress and strong repayment capacity.")
else:
    analysis.append(f"FOIR is {round(foir,2)}, indicating elevated financial obligations relative to income.")

# Behavioral Layer
if savings > 0.3:
    analysis.append("Savings behavior is strong, reinforcing financial discipline.")
else:
    analysis.append("Savings buffer is limited, increasing vulnerability to income shocks.")

# Final Recommendation
if score > 750:
    recommendation = "Borrower is highly creditworthy and eligible for premium lending products."
elif score > 600:
    recommendation = "Borrower is moderately creditworthy. Controlled exposure recommended."
else:
    recommendation = "Borrower is high risk. Lending should be cautious or limited."

# Display output like real AI
for line in analysis:
    st.write("• " + line)

st.markdown("---")
st.markdown("### 📌 Recommendation")

if score > 750:
    st.success(recommendation)
elif score > 600:
    st.warning(recommendation)
else:
    st.error(recommendation)
    
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
