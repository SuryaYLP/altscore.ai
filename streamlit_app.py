import streamlit as st

st.title("AltScore AI")

transactions = st.slider("Monthly Transactions", 0, 200, 100)
recharge = st.slider("Recharge Frequency", 0, 20, 5)
location = st.slider("Location Stability", 0.0, 1.0, 0.5)

score = 300 + transactions*2 + recharge*5 + int(location*200)
score = min(score, 900)

if score > 750:
    risk = "Low"
elif score > 600:
    risk = "Medium"
else:
    risk = "High"

st.write("### Credit Score:", score)
st.write("### Risk Level:", risk)
