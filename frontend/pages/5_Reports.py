"""
I4C Cybercrime Analytics Portal - Reports & Analytics
Role-based analytics dashboard for authorized users
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Reports & Analytics - I4C Portal",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .reports-header {
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
<div class="reports-header">
    <h1>📊 Reports & Analytics</h1>
    <h3>Cybercrime Trends, Success Metrics, and Exportable Reports</h3>
    <p>Empowering I4C, Police, and Banks with actionable intelligence</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>📈 Crime Trends (Last 12 Months)</h3></div>', unsafe_allow_html=True)

# Mock time-series data
months = pd.date_range(end=datetime.now(), periods=12, freq='M').strftime('%b %Y').tolist()
complaints = [random.randint(40, 120) for _ in months]
resolved = [c - random.randint(5, 30) for c in complaints]

df_trend = pd.DataFrame({
    "Month": months,
    "Complaints": complaints,
    "Resolved": resolved
})

fig_trend = px.line(
    df_trend, x="Month", y=["Complaints", "Resolved"],
    markers=True,
    color_discrete_map={"Complaints": "#667eea", "Resolved": "#4ade80"},
    labels={"value": "Count", "variable": "Type"}
)
fig_trend.update_layout(
    height=350,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor='#181825',
    paper_bgcolor='#181825',
    font=dict(color='#fff', size=16),
    xaxis=dict(title_font=dict(color='#fff', size=16), tickfont=dict(color='#fff', size=14)),
    yaxis=dict(title_font=dict(color='#fff', size=16), tickfont=dict(color='#fff', size=14))
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('<div class="section-header"><h3>🎯 Success Rate & Recovery</h3></div>', unsafe_allow_html=True)

# Mock metrics
success_rate = round(sum(resolved) / sum(complaints) * 100, 1)
amount_recovered = round(random.uniform(2.5, 15.0), 2)

col1, col2 = st.columns(2)
with col1:
    st.metric("Success Rate", f"{success_rate}%", delta="+2.3%")
with col2:
    st.metric("Amount Recovered (₹ Lakhs)", f"{amount_recovered}", delta="+₹45,000")

st.markdown('<div class="section-header"><h3>🔎 Downloadable Reports</h3></div>', unsafe_allow_html=True)

# Downloadable CSV
csv = df_trend.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Crime Trends CSV",
    data=csv,
    file_name="crime_trends_report.csv",
    mime="text/csv",
    use_container_width=True
)

st.markdown("""
<div style="text-align: center; padding: 2rem; background: white; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #7f8c8d; margin: 0;">
        📊 <strong>Reports & Analytics</strong> | Export data for meetings, evidence, and strategic planning.
    </p>
</div>
""", unsafe_allow_html=True)