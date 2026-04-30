"""
I4C Cybercrime Analytics Portal - Alert System
Role-based real-time alert dashboard for authorized users
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Alerts - I4C Portal",
    page_icon="🚨",
    layout="wide"
)

# Mock alert data for demo
alert_types = ["ATM Withdrawal Risk", "Mule Account Detected", "Suspicious Transaction", "Pattern Match", "High-Value Fraud"]
priorities = ["Critical", "High", "Medium", "Low"]
locations = ["Bangalore", "Delhi", "Mumbai", "Chennai", "Hyderabad", "Pune", "Kolkata"]

def random_alert(i):
    return {
        "id": f"ALERT-{2024000+i}",
        "type": random.choice(alert_types),
        "location": random.choice(locations),
        "priority": random.choice(priorities),
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime("%Y-%m-%d %H:%M"),
        "status": random.choice(["Active", "Acknowledged", "Escalated"]),
        "details": f"Automated detection triggered for {random.choice(locations)} ATM. Immediate action required."
    }

alerts = [random_alert(i) for i in range(1, 16)]

st.markdown("""
<style>
    .alert-header {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
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
<div class="alert-header">
    <h1>🚨 Alert System</h1>
    <h3>Real-Time Cybercrime Risk & Incident Notifications</h3>
    <p>Prioritize, acknowledge, and escalate alerts for rapid response</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>🔔 Active Alerts</h3></div>', unsafe_allow_html=True)

for alert in alerts:
    color = "#dc3545" if alert["priority"] == "Critical" else "#fd7e14" if alert["priority"] == "High" else "#ffc107" if alert["priority"] == "Medium" else "#17a2b8"
    with st.expander(f"🚨 [{alert['priority']}] {alert['type']} - {alert['location']} ({alert['timestamp']})", expanded=alert["priority"] in ["Critical", "High"]):
        st.markdown(f"""
        <div style="padding: 1rem; background: #181825; border-radius: 10px;">
            <span style="background-color: {color}; color: white; padding: 6px 18px; border-radius: 14px; font-size: 1rem; font-weight: 700;">{alert['priority']}</span>
            <span style="margin-left: 1rem; color: #fff;">{alert['type']}</span>
            <span style="margin-left: 1rem; color: #fff;">📍 {alert['location']}</span>
            <span style="margin-left: 1rem; color: #fff;">🕒 {alert['timestamp']}</span>
            <br><br>
            <span style="color: #fff;">{alert['details']}</span>
            <br><br>
            <span style="color: #7f8c8d;">Status: <b>{alert['status']}</b></span>
        </div>
        """, unsafe_allow_html=True)
        st.button("Acknowledge", key=f"ack_{alert['id']}", use_container_width=True)
        st.button("Escalate", key=f"esc_{alert['id']}", use_container_width=True)
        st.button("Download Report", key=f"dl_{alert['id']}", use_container_width=True)

st.markdown("""
<div style="text-align: center; padding: 2rem; background: white; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #7f8c8d; margin: 0;">
        🚨 <strong>Alert System</strong> | Enables rapid response and coordination for cybercrime incidents.
    </p>
</div>
""", unsafe_allow_html=True)

# Add this block for proactive alert simulation
if st.button("Simulate New Alert"):
    st.session_state["alerts"].append({
        "type": "Suspicious Transaction",
        "location": "Demo City",
        "priority": "Critical",
        "timestamp": "Now",
        "status": "Active"
    })
    st.success("🚨 New alert triggered for suspicious transaction! Police and bank notified.")

st.markdown("### Active Alerts")
for alert in st.session_state["alerts"]:
    st.info(f"{alert['type']} at {alert['location']} ({alert['priority']}) - {alert['status']}")