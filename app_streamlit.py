import streamlit as st
import pandas as pd
import numpy as np
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AltScore AI", layout="wide")

# ------------------------
# UI THEME
# ------------------------
st.markdown("""
<style>
body { background-color: white; }
h1, h2, h3 { color: #1f4e79; }
</style>
""", unsafe_allow_html=True)

# ------------------------
# HEADER
# ------------------------
st.title("💳 AltScore AI")
st.caption("Behavioral Credit Underwriting Engine")

st.markdown("---")

# ------------------------
# PROFILE
# ------------------------
profile = st.selectbox("Select Profile", ["Gig Worker", "Salaried", "Informal"])

sub_profile = None

if profile == "Gig Worker":
    sub_profile = st.selectbox(
        "Select Category",
        ["Delivery Agent", "Driver Partner", "Urban Company Professional"]
    )

st.markdown("---")

# ------------------------
# INPUTS
# ------------------------
st.markdown("### 📊 Behavioral Inputs")

transactions = st.slider("Transactions", 0, 300, 100, help="Higher = more financial activity")
savings = st.slider("Savings Ratio", 0.0, 1.0, 0.2, help="Higher = safer")
bill_pay = st.slider("Bill Payment Consistency", 0.0, 1.0, 0.6, help="Higher = reliable")

st.markdown("---")

# ------------------------
# FINANCIAL INPUTS
# ------------------------
st.markdown("### 💰 Financial Inputs")

cash_in = st.number_input("Monthly Income", 0, 200000, 30000)
cash_out = st.number_input("Monthly Expenses", 0, 200000, 25000)
obligations = st.number_input("Fixed Obligations (EMIs, Rent)", 0, 200000, 10000)

st.caption("FOIR = Fixed obligations / income")

# ------------------------
# CROSS PLATFORM
# ------------------------
st.markdown("---")
st.markdown("### 🌐 Cross Platform Signals")

multi_income = st.number_input("Total Digital Income", 0, 500000, 40000)
platform_count = st.slider("Number of Platforms", 1, 5, 2)
active_months = st.slider("Consecutive Active Months", 0, 60, 12)
growth = st.slider("YoY Growth (%)", -50, 100, 10)

# ------------------------
# CSV
# ------------------------
st.markdown("---")
st.markdown("### 📂 Bank Statement (Optional)")

uploaded_file = st.file_uploader("Upload CSV")

cv = 0.3
avg_gap = 10
max_gap = 20

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Flexible column detection
    cols = [c.lower() for c in df.columns]

    if "amount" in cols:
        amount_col = df.columns[cols.index("amount")]
    else:
        amount_col = df.columns[-1]

    if "date" in cols:
        date_col = df.columns[cols.index("date")]
    else:
        date_col = df.columns[0]

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values(date_col)

    credits = df[df[amount_col] > 0][amount_col]

    if len(credits) > 0:
        cv = credits.std() / credits.mean() if credits.mean() > 0 else 1

    if len(credits) > 1:
        gaps = df[df[amount_col] > 0][date_col].diff().dt.days.dropna()
        avg_gap = gaps.mean()
        max_gap = gaps.max()

# ------------------------
# BUTTON TRIGGER
# ------------------------
if st.button("🔍 Check Credit Score"):

    # ------------------------
    # FEATURE ENGINEERING
    # ------------------------
    foir = obligations / cash_in if cash_in > 0 else 0

    stability = max(0, 1 - cv)
    frequency = max(0, 1 - (avg_gap / 30))
    cf = max(0, 1 - (cash_out / cash_in)) if cash_in > 0 else 0.5

    # Cross platform boost
    diversification = min(platform_count / 3, 1)

    # ------------------------
    # SCORING
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

    if cv > 0.5:
        score -= 100

    if max_gap > 20:
        score -= 80

    score = max(300, min(score, 900))

    # ------------------------
    # RISK COLOR
    # ------------------------
    if score > 750:
        risk = "Low"
        color = "green"
    elif score > 600:
        risk = "Medium"
        color = "orange"
    else:
        risk = "High"
        color = "red"

    # ------------------------
    # RESULTS UI
    # ------------------------
    st.markdown("---")
    st.markdown("## 📊 Check Credit Score")

    c1, c2, c3 = st.columns(3)

    c1.metric("Score", score)
    c2.metric("Risk", risk)
    c3.metric("FOIR", round(foir, 2))

    st.progress(score / 900)

    # ------------------------
    # PDF GENERATION
    # ------------------------
    def generate_pdf():
        doc = SimpleDocTemplate("report.pdf")
        styles = getSampleStyleSheet()
        content = []

        content.append(Paragraph("AltScore Credit Report", styles['Title']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(f"Score: {score}", styles['Normal']))
        content.append(Paragraph(f"Risk: {risk}", styles['Normal']))
        content.append(Paragraph(f"FOIR: {round(foir,2)}", styles['Normal']))

        doc.build(content)

    generate_pdf()

    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download Report", f, file_name="AltScore_Report.pdf")

    # ------------------------
    # AI SUMMARY
    # ------------------------
    st.markdown("### 🤖 Analysis")

    st.write(f"""
    This user shows stability score of {round(stability,2)} with volatility {round(cv,2)}.
    Income consistency is {round(frequency,2)}.
    FOIR indicates {'low' if foir < 0.4 else 'high'} financial stress.
    """)
