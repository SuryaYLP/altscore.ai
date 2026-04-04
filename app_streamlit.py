import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "results" not in st.session_state:
    st.session_state.results = None
    
st.set_page_config(page_title="AltScore AI", layout="wide")
# ------------------------
# UI STYLE
# ------------------------
st.markdown("""
<style>
.section {
    background-color: #f5f9fc;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)
# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine")

st.markdown("---")

st.markdown('</div>', unsafe_allow_html=True)
# ------------------------
# SESSION START BUTTON
# ------------------------
score = None
foir = None
stability = None
frequency = None
cf = None

if "start" not in st.session_state:
    st.session_state.start = False

if st.button("🚀 Click to Assess Creditworthiness"):
    st.session_state.start = True

if not st.session_state.start:
    st.stop()
st.markdown('</div>', unsafe_allow_html=True)
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

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------
# EXPENSES
# ------------------------
st.markdown("---")
st.markdown("## 💰 Expenses")

fixed_obligations = st.number_input("Fixed obligations per month (EMI, rent)", 0, 200000, 10000)
other_expenses = st.number_input("Other expenses per month", 0, 200000, 15000)

total_expenses = fixed_obligations + other_expenses
total_savings = total_income - total_expenses

st.markdown('</div>', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
# ------------------------
# RESULT BUTTON
# ------------------------
# ------------------------
# MONTHLY SUMMARY
# ------------------------
total_savings = total_income - total_expenses
# ------------------------
# FIX: Define savings ratio
# ------------------------
total_savings = total_income - total_expenses
calc_savings_ratio = (total_savings / total_income) if total_income > 0 else 0

# If user changed slider use that, else fallback
try:
    final_savings_ratio = savings if savings > 0 else calc_savings_ratio
except:
    final_savings_ratio = calc_savings_ratio
savings = final_savings_ratio
calc_savings_ratio = (total_savings / total_income) if total_income > 0 else 0

# If user has moved slider, use that, else fallback
final_savings_ratio = savings if savings > 0 else calc_savings_ratio

# ------------------------
if st.button("🔍 Check AltScore Credit Score"):
    # ------------------------
    # CALCULATIONS
    # ------------------------
    total_savings = total_income - total_expenses
    savings_ratio = (total_savings / total_income) if total_income > 0 else 0

    foir = fixed_obligations / total_income if total_income > 0 else 0
    stability = max(0, 1 - cv)
    frequency = min(transactions / 200, 1)
    cf = max(0, 1 - (total_expenses / total_income)) if total_income > 0 else 0.5

    score = 300
    score += int(200 * stability)
    score += int(150 * frequency)
    score += int(150 * cf)
    score += int(150 * savings_ratio)
    score += int(150 * bill_pay)

    if foir < 0.4:
        score += 100
    elif foir < 0.6:
        score += 40
    else:
        score -= 100

    score = max(300, min(score, 900))

    # Loan logic
    if score > 750:
        loan = "₹2L - ₹5L"
        rate = "10% - 14%"
    elif score > 600:
        loan = "₹50K - ₹2L"
        rate = "14% - 20%"
    else:
        loan = "₹0 - ₹50K"
        rate = "20%+"

    # ------------------------
    # STORE EVERYTHING
    # ------------------------
    st.session_state.results = {
        "score": score,
        "foir": foir,
        "stability": stability,
        "frequency": frequency,
        "cf": cf,
        "loan": loan,
        "rate": rate,
        "savings_ratio": savings_ratio,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_savings": total_savings
    }
if st.session_state.results is not None:

    r = st.session_state.results

    st.markdown("---")
    st.markdown("## 📊 Credit Assessment Results")

    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Credit Score", r["score"])
    c2.metric("FOIR", round(r["foir"], 2))
    c3.metric("Savings Ratio", round(r["savings_ratio"], 2))
    c4.metric("Eligible Loan", r["loan"])

    st.progress(r["score"] / 900)

    # Monthly Summary
    st.markdown("### 📊 Monthly Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Income", int(r["total_income"]))
    m2.metric("Expenses", int(r["total_expenses"]))
    m3.metric("Savings", int(r["total_savings"]))

    # Underwriting Signals
    st.markdown("### 🧠 Underwriting Signals")
    u1, u2, u3 = st.columns(3)
    u1.metric("Stability", round(r["stability"], 2))
    u2.metric("Frequency", round(r["frequency"], 2))
    u3.metric("Cash Flow", round(r["cf"], 2))

    # ------------------------
    # RISK LABEL
    # ------------------------
    if r["score"] > 750:
        risk = "Low"
        st.success("Low Risk")
    elif r["score"] > 600:
        risk = "Medium"
        st.warning("Medium Risk")
    else:
        risk = "High"
        st.error("High Risk")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ------------------------
    # INTERACTIVE GRAPHS
    # ------------------------
    import plotly.express as px
    import pandas as pd

    st.markdown("### 📈 Financial Insights")

    finance_df = pd.DataFrame({
        "Category": ["Income", "Expenses", "Savings"],
        "Amount": [r["total_income"], r["total_expenses"], r["total_savings"]]
    })

    fig1 = px.bar(finance_df, x="Category", y="Amount", color="Category", text="Amount")
    st.plotly_chart(fig1, use_container_width=True)

    score_df = pd.DataFrame({
        "Metric": ["Stability", "Frequency", "Cash Flow", "Savings"],
        "Value": [r["stability"], r["frequency"], r["cf"], r["savings_ratio"]]
    })

    fig2 = px.line_polar(score_df, r="Value", theta="Metric", line_close=True)
    st.plotly_chart(fig2, use_container_width=True)
    if st.session_state.results is not None:

        r = st.session_state.results

        import plotly.graph_objects as go

        st.markdown("### 📊 Credit Score Gauge")
            
        fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=r["score"],
                title={'text': "Credit Score"},
                gauge={
                    'axis': {'range': [300, 900]},
                    'bar': {'color': "#1f4e79"},
                    'steps': [
                        {'range': [300, 650], 'color': "red"},
                        {'range': [650, 700], 'color': "orange"},
                        {'range': [700, 750], 'color': "yellow"},
                        {'range': [750, 800], 'color': "lightgreen"},
                        {'range': [800, 900], 'color': "green"},
                    ],
                }
            ))
            
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    # ------------------------
    # GPT AI ANALYSIS
    # ------------------------
    st.markdown("### 🤖 AI Credit Analysis (GPT)")
    
    with st.spinner("AI is analyzing borrower profile..."):
    
            try:
                prompt = f"""
                You are a senior credit risk analyst.
    
                Analyze this borrower:
    
                Income: {r["total_income"]}
                Expenses: {r["total_expenses"]}
                Savings Ratio: {round(r["savings_ratio"],2)}
                FOIR: {round(r["foir"],2)}
                Stability Score: {round(r["stability"],2)}
                Frequency Score: {round(r["frequency"],2)}
                Cash Flow Score: {round(r["cf"],2)}
    
                Provide:
                - Risk summary
                - Key strengths
                - Key risks
                - Final recommendation
                """
    
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
    
                st.markdown(response.choices[0].message.content)
    
            except Exception as e:            
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ------------------------
    # CONFIDENCE SCORE
    # ------------------------
    confidence = (
        0.25 * r["stability"] +
        0.20 * r["frequency"] +
        0.20 * r["cf"] +
        0.20 * (1 - r["foir"]) +
        0.15 * r["savings_ratio"]
        )

    confidence = max(0, min(confidence, 1))

    st.markdown("### 🎯 Model Confidence")

    if confidence > 0.75:
        st.success(f"High Confidence: {round(confidence,2)}")
    elif confidence > 0.5:
        st.warning(f"Moderate Confidence: {round(confidence,2)}")
    else:
        st.error(f"Low Confidence: {round(confidence,2)}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------
    # RULE-BASED AI ANALYSIS (SECOND AI — KEEPING)
    # ------------------------
    st.markdown("### 🤖 AI Credit Analysis (Rule-Based)")
        analysis = []
        
        analysis.append(f"Stability Score: {round(r['stability'],2)}")
        analysis.append(f"Income Frequency: {round(r['frequency'],2)}")
        analysis.append(f"Cash Flow Score: {round(r['cf'],2)}")
        analysis.append(f"FOIR: {round(r['foir'],2)}")
        analysis.append(f"Savings Ratio: {round(r['savings_ratio'],2)}")
        
        if r["stability"] < 0.5:
            analysis.append("Income shows high volatility → repayment risk")
        
        if r["frequency"] < 0.5:
            analysis.append("Income is irregular → inconsistent cash flow")
        
        if r["cf"] < 0.4:
            analysis.append("Cash flow is weak → low financial buffer")
        
        if r["foir"] > 0.6:
            analysis.append("High financial obligations → stress risk")
        
        if r["savings_ratio"] < 0.2:
            analysis.append("Low savings → vulnerable to shocks")
        
        for line in analysis:
            st.write("• " + line)

    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------
    # PDF DOWNLOAD
    # ------------------------
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors

        data = [
            ["Metric", "Value"],
            ["Score", r["score"]],
            ["FOIR", round(r["foir"],2)],
            ["Savings Ratio", round(r["savings_ratio"],2)],
            ["Income", r["total_income"]],
            ["Expenses", r["total_expenses"]],
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.blue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        content.append(table)
    
        with open("report.pdf", "rb") as f:
            st.download_button("📄 Download Report", f, file_name="AltScore_Report.pdf")
