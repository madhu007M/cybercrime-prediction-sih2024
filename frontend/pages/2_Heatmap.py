"""
I4C Cybercrime Analytics Portal - Crime Heatmap
Visualize geographic distribution of cybercrime complaints
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_manager import db

st.set_page_config(
    page_title="Crime Heatmap - I4C Portal",
    page_icon="🗺️",
    layout="wide"
)

st.markdown("""
<style>
    .heatmap-header {
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
<div class="heatmap-header">
    <h1>🗺️ Crime Heatmap</h1>
    <h3>Geographic Distribution of Cybercrime Complaints</h3>
    <p>Identify hotspots and patterns for proactive intervention</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>📍 Interactive Heatmap</h3></div>', unsafe_allow_html=True)

# Fetch city-wise complaint data
city_data = db.get_complaints_by_city()

if city_data:
    df = pd.DataFrame(list(city_data.items()), columns=["City", "Complaint Count"])
    # For demo, assign lat/lon for major cities (real app: fetch from DB)
    city_coords = {
        "Bangalore": (12.9716, 77.5946),
        "Delhi": (28.7041, 77.1025),
        "Mumbai": (19.0760, 72.8777),
        "Chennai": (13.0827, 80.2707),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
        "Kolkata": (22.5726, 88.3639)
    }
    df["lat"] = df["City"].map(lambda x: city_coords.get(x, (0,0))[0])
    df["lon"] = df["City"].map(lambda x: city_coords.get(x, (0,0))[1])

    fig = px.density_mapbox(
        df, lat="lat", lon="lon", z="Complaint Count", radius=40,
        center=dict(lat=21.0, lon=78.0), zoom=3.5,
        mapbox_style="carto-darkmatter",
        hover_name="City",
        color_continuous_scale="YlOrRd"
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        font=dict(color="#fff", size=16)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No city-wise complaint data available.")

st.markdown('<div class="section-header"><h3>🔎 City-wise Complaint Table</h3></div>', unsafe_allow_html=True)

if city_data:
    st.dataframe(df.style.background_gradient(cmap="YlOrRd"), use_container_width=True)
else:
    st.info("No data to display.")

st.markdown("""
<div style="text-align: center; padding: 2rem; background: white; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #7f8c8d; margin: 0;">
        🗺️ <strong>Crime Heatmap</strong> | Visualize hotspots for rapid response and resource allocation.
    </p>
</div>
""", unsafe_allow_html=True)