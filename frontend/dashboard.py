"""
Cybercrime Prediction Dashboard
Team: madhu007M | Smart India Hackathon 2024
Developer: [Frontend Team Member Name]
"""

import streamlit as st

# TODO: Implement dashboard here
# - Risk heatmap
# - Alert system
# - Analytics

import streamlit as st
import requests

# ... (existing code) ...

st.sidebar.header("👮 Law Enforcement Controls")

# THE BUTTON
if st.sidebar.button("⚠️ SIMULATE LIVE HACK ATTACK"):
    # This data simulates a "Ringleader" trying to steal ₹80,000
    payload = {
        "mule_id": "MULE_RINGLEADER_01",
        "amount": 80000,
        "lat": 28.6315,
        "long": 77.2167
    }
    
    try:
        # Call your Backend API
        response = requests.post("http://127.0.0.1:5000/api/process_transaction", json=payload)
        result = response.json()
        
        if response.status_code == 200:
            if result['status'] == "INTERCEPTED":
                st.error(f"🚨 ALERT SENT! {result['message']}")
                st.write(f"SMS Status: {result.get('sms_status')}")
            else:
                st.success("Transaction Safe.")
        else:
            st.error("Failed to connect to backend.")
            
    except Exception as e:
        st.error(f"Error: {e}")