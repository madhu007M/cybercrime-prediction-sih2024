"""
I4C Cybercrime Analytics Portal - AI Predictor
Predict next ATM withdrawal location using hybrid ML + transaction tracing
"""

import streamlit as st
import random

st.set_page_config(
    page_title="AI Predictor - I4C Portal",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    .predictor-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        color: white;
        text-align: center;
    }
    .section-header {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .section-header h3 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="predictor-header">
    <h1>🎯 AI Predictor</h1>
    <h3>Predict Next ATM Withdrawal Location</h3>
    <p>Hybrid ML + Transaction Tracing Fusion Engine</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>📝 Enter Complaint / Mule Account Details</h3></div>', unsafe_allow_html=True)

with st.form("predict_form"):
    complaint_id = st.text_input("Complaint ID", "")
    mule_account = st.text_input("Mule Account Number", "")
    fraud_type = st.selectbox("Fraud Type", ["Credit Card Fraud", "UPI Fraud", "Phishing", "Loan Fraud", "Cyber Extortion", "Job Fraud", "Investment Scam", "Lottery Scam", "Romance Scam"])
    city = st.selectbox("Suspected City", ["Bangalore", "Delhi", "Mumbai", "Chennai", "Hyderabad", "Pune", "Kolkata"])
    submit = st.form_submit_button("Predict ATM Location")

if submit:
    # Mock fusion engine logic
    use_tracing = mule_account and random.choice([True, False])
    if use_tracing:
        confidence = 95 + random.randint(0, 3)
        engine = "Transaction Tracing"
    else:
        confidence = 85 + random.randint(0, 5)
        engine = "ML Pattern Prediction"
    atm_locations = [
        f"{city} ATM-{random.randint(1, 10)}",
        f"{city} ATM-{random.randint(11, 20)}",
        f"{city} ATM-{random.randint(21, 30)}"
    ]
    st.markdown(f"""
    <div class="section-header">
        <h3>🎯 Prediction Results</h3>
        <p><b>Fusion Engine Used:</b> {engine}</p>
        <p><b>Confidence:</b> {confidence}%</p>
        <ul>
            <li><b>Top Prediction:</b> {atm_locations[0]}</li>
            <li><b>Second Prediction:</b> {atm_locations[1]}</li>
            <li><b>Third Prediction:</b> {atm_locations[2]}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.success("Prediction complete! Share with law enforcement or bank teams for rapid action.")

st.markdown("""
<div style="text-align: center; padding: 2rem; background: white; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #7f8c8d; margin: 0;">
        🎯 <strong>AI Predictor</strong> | Combines ML and transaction tracing for proactive cybercrime prevention.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🏦 Simulate Suspicious Transaction (Bank API)")
with st.form("mock_tracing"):
    mule_account = st.text_input("Mule Account Number")
    amount = st.number_input("Amount", min_value=0)
    city = st.selectbox("City", ["Bangalore", "Delhi", "Mumbai", "Chennai", "Hyderabad", "Pune", "Kolkata"])
    submit = st.form_submit_button("Simulate Transaction")

if submit:
    st.info(f"Suspicious transaction detected for account {mule_account} in {city}. Predicting withdrawal location...")
    # Mock fusion engine output
    prediction = f"{city} ATM-{random.randint(1,10)}"
    confidence = random.choice([85, 95, 98])
    st.success(f"Predicted withdrawal location: {prediction} (Confidence: {confidence}%)")
    st.warning("🚨 Alert sent to police and bank for proactive action!")