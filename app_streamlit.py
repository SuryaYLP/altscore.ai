import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="AltScore AI", layout="wide")

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine | Stability > Income")

st.markdown("---")

# ------------------------
# SESSION STATE
# ------------------------
if "started" not in st.session_state:
    st.session_state.started = False

if st.button("🚀 Assess Creditworthiness"):
    st.session_state.started = True

if not st.session_state.started:
    st.info("Click to begin")
    st.stop()

# ------------------------
# PROFILE
# ------------------------
profile = st.selectbox(
    "User Profile",
    ["Gig Worker", "Salaried", "Informal"]
)

st.markdown("---")

# ------------------------
# INPUTS
# ------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Behavioral Inputs")

    transactions = st.slider("Monthly Transactions", 0, 300, 100)
    savings = st.slider("Savings Ratio", 0.0, 1.0, 0.2)
    bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6)

with col2:
    st.markdown("### 💰 Financial Inputs")

    cash_in = st.number_input("Monthly Income (₹)", 0, 200000, 30000)
    cash_out = st.number_input("Monthly Expenses (₹)", 0, 200000, 25000)
    obligations = st.number_input("Fixed Obligations (₹)", 0, 200000, 10000)

    st.markdown("### 📂 Upload Bank Statement")
    uploaded_file = st.file_uploader("CSV", type=["csv"])

# ------------------------
# FEATURE EXTRACTION FROM CSV
# ------------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "amount" in df.columns and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        credits = df[df["amount"] > 0]["amount"]
        debits = df[df["amount"] < 0]["amount"]

        # Income stats
        income_total = credits.sum()
        income_mean = credits.mean() if len(credits) > 0 else 0
        income_std = credits.std() if len(credits) > 0 else 0

        # Volatility (CV)
        if income_mean > 0:
            cv = income_std / income_mean
        else:
            cv = 1

        # Frequency
        credit_dates = df[df["amount"] > 0]["date"]
        if len(credit_dates) > 1:
            gaps = credit_dates.diff().dt.days.dropna()
            avg_gap = gaps.mean()
            max_gap = gaps.max()
        else:
            avg_gap = 30
            max_gap = 30

        # Cash flow
        inflow = credits.sum()
        outflow = abs(debits.sum())

        # Override inputs
        cash_in = inflow
        cash_out = outflow

        st.success(f"Income detected: ₹{int(cash_in)}")
        st.success(f"Expenses detected: ₹{int(cash_out)}")

    else:
        st.error("CSV must contain 'date' and 'amount' columns")
        cv = 1
        avg_gap = 30
        max_gap = 30
else:
    cv = 0.3
    avg_gap = 10
    max_gap = 20

# ------------------------
# FOIR
# ------------------------
foir = obligations / cash_in if cash_in > 0 else 0

# ------------------------
# FEATURE ENGINEERING
# ------------------------

# Stability score (LOW CV = GOOD)
stability_score = max(0, 1 - cv)

# Frequency score (LOW GAP = GOOD)
frequency_score = max(0, 1 - (avg_gap / 30))

# Cash flow health
if cash_in > 0:
    cf_ratio = cash_out / cash_in
    cf_score = max(0, 1 - cf_ratio)
else:
    cf_score = 0.5

# ------------------------
# SCORING ENGINE
# ------------------------
score = 300

score += int(200 * stability_score)
score += int(150 * frequency_score)
score += int(150 * cf_score)
score += int(150 * savings)
score += int(150 * bill_pay)

# FOIR
if foir < 0.4:
    score += 100
elif foir < 0.6:
    score += 40
else:
    score -= 100

# Volatility penalty
if cv > 0.5:
    score -= 100

# Gap penalty
if max_gap > 20:
    score -= 80

# Clamp
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
# RESULTS
# ------------------------
c1, c2, c3 = st.columns(3)

c1.metric("Credit Score", score)
c2.metric("Risk Level", risk)
c3.metric("FOIR", round(foir, 2))

st.progress(score / 900)

# ------------------------
# UNDERWRITING DASHBOARD
# ------------------------
st.markdown("### 🧠 Underwriting Signals")

d1, d2, d3 = st.columns(3)

d1.metric("Stability Score", round(stability_score, 2))
d2.metric("Income Frequency", round(frequency_score, 2))
d3.metric("Cash Flow Score", round(cf_score, 2))

# ------------------------
# RISK FLAGS
# ------------------------
st.markdown("### 🚨 Risk Signals")

if cv > 0.5:
    st.warning("High income volatility detected")

if max_gap > 20:
    st.warning("Irregular income gaps detected")

if foir > 0.6:
    st.error("High debt burden")

if cash_out > cash_in:
    st.error("Negative cash flow")

# ------------------------
# AI ANALYSIS (SIMULATED)
# ------------------------
st.markdown("### 🤖 AI Analysis")

analysis = f"""
This borrower shows a stability score of {round(stability_score,2)} and income volatility (CV) of {round(cv,2)}.

Income consistency is {'strong' if frequency_score > 0.6 else 'weak'}, with average gaps of {int(avg_gap)} days.

FOIR is {round(foir,2)}, indicating {'low' if foir < 0.4 else 'high'} financial stress.

Overall risk is classified as {risk}.
"""

st.code(analysis)

# ------------------------
# FOOTER
# ------------------------
st.markdown("---")
st.caption("Prototype underwriting engine using behavioral financial signals")

if st.button("🔄 Reset"):
    st.session_state.started = False
