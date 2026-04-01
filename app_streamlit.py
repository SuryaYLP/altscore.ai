import streamlit as st

st.set_page_config(page_title="AltScore AI", layout="centered")

st.title("💳 AltScore AI")
st.subheader("Alternative Credit Scoring for the Underserved")

st.markdown("Enter user behavioral data:")

transactions = st.slider("Monthly Transactions", 0, 200, 100)
recharge = st.slider("Recharge Frequency", 0, 20, 5)
location = st.slider("Location Stability", 0.0, 1.0, 0.5)

# Scoring logic
score = 300 + transactions*2 + recharge*5 + int(location*200)
score = min(score, 900)

if score > 750:
    risk = "Low"
elif score > 600:
    risk = "Medium"
else:
    risk = "High"

st.divider()

st.subheader("📊 Results")

st.metric("Credit Score", score)
st.metric("Risk Level", risk)

if risk == "Low":
    st.success("User is highly creditworthy")
elif risk == "Medium":
    st.warning("User has moderate risk")
else:
    st.error("User is high risk")

st.divider()

st.markdown("### 🧠 AI Insight")
st.write(
    "This score is derived from behavioral consistency patterns rather than traditional financial history."
)
