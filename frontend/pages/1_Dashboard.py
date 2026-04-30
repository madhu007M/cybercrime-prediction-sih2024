"""
I4C Cybercrime Analytics Portal - Main Dashboard
Role-based dashboard with real-time statistics and insights
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import (
    check_authentication, get_user_role, show_status_badge,
    format_currency, format_datetime, calculate_time_ago,
    get_fraud_type_emoji, get_chart_colors
)
from db_manager import db

# Page config
st.set_page_config(
    page_title="Dashboard - I4C Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication
user = check_authentication()
user_role = get_user_role()

# Custom CSS for winning UI
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .dashboard-title {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Data tables */
    .dataframe {
        background: white !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Section headers */
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
    
    /* Quick action buttons */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Alert boxes */
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .alert-high {
        background: linear-gradient(135deg, #ffa502 0%, #ff7f00 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    /* Stats card */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        height: 100%;
    }
    
    .stats-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stats-label {
        color: #7f8c8d;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### 👤 {user['name']}")
    st.markdown(f"**🎭 Role:** {user_role}")
    st.markdown(f"**📍 Jurisdiction:** {user['jurisdiction']}")
    st.markdown("---")
    
    # Quick stats in sidebar with visible numbers
    stats = db.get_user_stats(user_role)
    
    st.markdown("### 📊 Quick Stats")
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-bottom: 0.3rem;">Active Cases</div>
        <div style="color: white; font-size: 2rem; font-weight: 700;">{stats['active_complaints']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-bottom: 0.3rem;">Today's Alerts</div>
        <div style="color: white; font-size: 2rem, font-weight: 700;">{stats['active_alerts']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-bottom: 0.3rem;">Success Rate</div>
        <div style="color: white; font-size: 2rem; font-weight: 700;">{stats['success_rate']}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Last refresh time
    st.caption(f"🕐 Last updated: {datetime.now().strftime('%I:%M %p')}")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ==================== MAIN DASHBOARD ====================

# Dashboard Header
st.markdown(f"""
<div class="dashboard-header">
    <div class="dashboard-title">🏠 Welcome, {user['name']}!</div>
    <div class="dashboard-subtitle">
        {user_role} Dashboard | {datetime.now().strftime('%A, %B %d, %Y')}
    </div>
</div>
""", unsafe_allow_html=True)

# Get dashboard statistics
stats = db.get_user_stats(user_role)

# ==================== KEY METRICS ROW ====================
st.markdown('<div class="section-header"><h3>📈 Key Performance Indicators</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #7f8c8d; text-transform: uppercase; margin-bottom: 0.5rem;">📥 Total Complaints</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{stats['total_complaints']}</div>
        <div style="font-size: 0.85rem; color: #28a745; font-weight: 600;">▲ +8 this month</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #7f8c8d; text-transform: uppercase; margin-bottom: 0.5rem;">⚡ Active Cases</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{stats['active_complaints']}</div>
        <div style="font-size: 0.85rem; color: #dc3545; font-weight: 600;">▼ -5 resolved today</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #7f8c8d; text-transform: uppercase; margin-bottom: 0.5rem;">🎯 Predictions Made</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{stats['total_predictions']}</div>
        <div style="font-size: 0.85rem; color: #28a745; font-weight: 600;">▲ +3 today</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #7f8c8d; text-transform: uppercase; margin-bottom: 0.5rem;">✅ Success Rate</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{stats['success_rate']}%</div>
        <div style="font-size: 0.85rem; color: #28a745; font-weight: 600;">▲ +2.3%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #7f8c8d; text-transform: uppercase; margin-bottom: 0.5rem;">💰 Amount Recovered</div>
        <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{format_currency(stats['amount_recovered'])}</div>
        <div style="font-size: 0.85rem; color: #28a745; font-weight: 600;">▲ +₹45,000 today</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== ALERTS SECTION ====================
active_alerts = db.get_active_alerts()
critical_alerts = [a for a in active_alerts if a['severity'] == 'Critical']
high_alerts = [a for a in active_alerts if a['severity'] == 'High']

if critical_alerts or high_alerts:
    st.markdown('<div class="section-header"><h3>🚨 Priority Alerts</h3></div>', unsafe_allow_html=True)
    
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        if critical_alerts:
            st.markdown("### 🔴 Critical Alerts")
            for alert in critical_alerts[:3]:
                st.markdown(f"""
                <div class="alert-critical">
                    <strong>{alert['alert_type']}</strong><br>
                    📍 {alert['location']}<br>
                    🕐 {calculate_time_ago(alert['created_at'])}
                </div>
                """, unsafe_allow_html=True)
    
    with alert_col2:
        if high_alerts:
            st.markdown("### 🟠 High Priority Alerts")
            for alert in high_alerts[:3]:
                st.markdown(f"""
                <div class="alert-high">
                    <strong>{alert['alert_type']}</strong><br>
                    📍 {alert['location']}<br>
                    🕐 {calculate_time_ago(alert['created_at'])}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")

# ==================== CHARTS SECTION ====================
st.markdown('<div class="section-header"><h3>📊 Analytics & Insights</h3></div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Complaints Trend (Last 30 days)
with chart_col1:
    st.markdown("#### 📈 Complaint Trends (Last 30 Days)")
    
    time_series = db.get_time_series_data(30)
    
    if time_series['dates']:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=time_series['dates'],
            y=time_series['counts'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#764ba2'),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            name='Complaints'
        ))
        
        fig_trend.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified',
            plot_bgcolor='#181825',
            paper_bgcolor='#181825',
            font=dict(color='#fff', size=16),
            xaxis=dict(
                title_font=dict(color='#fff', size=16),
                tickfont=dict(color='#fff', size=14)
            ),
            yaxis=dict(
                title_font=dict(color='#fff', size=16),
                tickfont=dict(color='#fff', size=14)
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No data available for trend analysis")

# Chart 2: Fraud Type Distribution
with chart_col2:
    st.markdown("#### 🎯 Fraud Type Distribution")
    
    fraud_data = db.get_complaints_by_fraud_type()
    
    if fraud_data:
        fig_fraud = go.Figure(data=[
            go.Pie(
                labels=list(fraud_data.keys()),
                values=list(fraud_data.values()),
                hole=0.4,
                marker=dict(colors=get_chart_colors()),
                textinfo='label+percent',
                textposition='auto'
            )
        ])
        
        fig_fraud.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            paper_bgcolor='#181825',
            font=dict(color='#fff', size=16)
        )
        
        st.plotly_chart(fig_fraud, use_container_width=True)
    else:
        st.info("No fraud data available")

st.markdown("---")

# Chart 3: City-wise Complaint Distribution
st.markdown("#### 🗺️ Geographic Distribution")

city_data = db.get_complaints_by_city()

if city_data:
    fig_city = go.Figure(data=[
        go.Bar(
            x=list(city_data.keys()),
            y=list(city_data.values()),
            marker=dict(
                color=list(city_data.values()),
                colorscale='Viridis',
                showscale=True
            ),
            text=list(city_data.values()),
            textposition='auto'
        )
    ])
    
    fig_city.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="City",
        yaxis_title="Complaint Count",
        plot_bgcolor='#181825',
        paper_bgcolor='#181825',
        font=dict(color='#fff', size=16),
        xaxis=dict(
            title_font=dict(color='#fff', size=16),
            tickfont=dict(color='#fff', size=14)
        ),
        yaxis=dict(
            title_font=dict(color='#fff', size=16),
            tickfont=dict(color='#fff', size=14)
        )
    )
    
    st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# ==================== RECENT COMPLAINTS ====================
st.markdown('<div class="section-header"><h3>🎯 Recent AI Predictions</h3></div>', unsafe_allow_html=True)

recent_predictions = db.get_recent_predictions(limit=5)

if recent_predictions:
    for pred in recent_predictions:
        with st.expander(f"🎯 {pred['prediction_id']} - {pred['method']} ({pred['confidence_1']:.1f}% confidence)"):
            col_pred1, col_pred2, col_pred3 = st.columns(3)
            
            with col_pred1:
                st.markdown(f"""
                **🥇 Top Prediction**  
                📍 **Location:** {pred['atm_1']}  
                🏙️ **City:** {pred['city_1']}  
                ✅ **Confidence:** {pred['confidence_1']:.1f}%
                """)
            
            with col_pred2:
                st.markdown(f"""
                **🥈 Second Prediction**  
                📍 **Location:** {pred['atm_2']}  
                🏙️ **City:** {pred['city_2']}  
                ✅ **Confidence:** {pred['confidence_2']:.1f}%
                """)
            
            with col_pred3:
                st.markdown(f"""
                **🥉 Third Prediction**  
                📍 **Location:** {pred['atm_3']}  
                🏙️ **City:** {pred['city_3']}  
                ✅ **Confidence:** {pred['confidence_3']:.1f}%
                """)
            
            st.markdown(f"""
            **🔍 Details:**  
            📋 Complaint: `{pred['complaint_id']}`  
            🏦 Mule Account: `{pred['mule_account']}`  
            🕐 Generated: {calculate_time_ago(pred['prediction_date'])}
            """)
else:
    st.info("No recent predictions available")

st.markdown("---")

# ==================== QUICK ACTIONS ====================
st.markdown('<div class="section-header"><h3>⚡ Quick Actions</h3></div>', unsafe_allow_html=True)

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("View Crime Heatmap", use_container_width=True):
        st.switch_page("pages/2_Heatmap.py")

with action_col2:
    if st.button("Generate Prediction", use_container_width=True):
        st.switch_page("pages/3_Predictor.py")

with action_col3:
    if st.button("View All Alerts", use_container_width=True):
        st.switch_page("pages/4_Alerts.py")

with action_col4:
    if st.button("Generate Report", use_container_width=True):
        st.switch_page("pages/5_Reports.py")

st.markdown("---")

# ==================== FOOTER ====================
st.markdown("""
<div style="text-align: center; padding: 2rem; background: white; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #7f8c8d; margin: 0;">
        🚨 <strong>I4C Cybercrime Analytics Portal</strong> | Ministry of Home Affairs<br>
        Predictive Analytics Framework for Proactive Cybercrime Intervention
    </p>
</div>
""", unsafe_allow_html=True)