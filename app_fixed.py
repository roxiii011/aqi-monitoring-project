"""
app.py
AirWatch India — Live AQI Monitoring & Health Advisory System
Main Home Dashboard for Third-Year BCS College Mini-Project.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

from live_aqi import (
    MAJOR_INDIAN_CITIES,
    AQI_CATEGORIES,
    search_indian_cities,
    fetch_live_air_quality,
    get_aqi_category_info
)
from health_advisory import get_advisory_by_category

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="AirWatch India | Live AQI Monitoring & Health Advisory",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Load Custom CSS ----------
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------- Session State Initialization ----------
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Delhi"
if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = MAJOR_INDIAN_CITIES["Delhi"]["lat"]
if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = MAJOR_INDIAN_CITIES["Delhi"]["lon"]
if "selected_state" not in st.session_state:
    st.session_state.selected_state = MAJOR_INDIAN_CITIES["Delhi"]["state"]

# ---------- Sidebar Controls ----------
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/wind.png", width=110)
    st.title("AirWatch India")
    st.caption("College Mini-Project | BCS 3rd Year")
    st.markdown("---")

    st.subheader("📍 Select or Search Indian City")
    
    # 1. Preset Major Cities
    city_options = list(MAJOR_INDIAN_CITIES.keys())
    default_index = city_options.index(st.session_state.selected_city) if st.session_state.selected_city in city_options else 0
    
    dropdown_city = st.selectbox(
        "Choose from Major Indian Hubs:",
        options=city_options,
        index=default_index,
        help="Select any of the top 25 monitored Indian metropolitan hubs"
    )

    if dropdown_city != st.session_state.selected_city and dropdown_city in MAJOR_INDIAN_CITIES:
        st.session_state.selected_city = dropdown_city
        st.session_state.selected_lat = MAJOR_INDIAN_CITIES[dropdown_city]["lat"]
        st.session_state.selected_lon = MAJOR_INDIAN_CITIES[dropdown_city]["lon"]
        st.session_state.selected_state = MAJOR_INDIAN_CITIES[dropdown_city]["state"]

    # 2. Custom India-Only City Search
    st.markdown("##### Or Search Any Indian Location:")
    search_query = st.text_input(
        "Type City / Town Name (India Only):",
        placeholder="e.g. Nashik, Kanpur, Mysuru...",
        help="Strictly validated to locations within the Republic of India"
    )

    if search_query:
        search_results = search_indian_cities(search_query, max_results=5)
        if search_results:
            st.success(f"Found {len(search_results)} Indian location(s):")
            for res in search_results:
                btn_label = f"📌 {res['name']} ({res['state']})"
                if st.button(btn_label, key=f"search_{res['name']}_{res['lat']}"):
                    st.session_state.selected_city = res["name"]
                    st.session_state.selected_lat = res["lat"]
                    st.session_state.selected_lon = res["lon"]
                    st.session_state.selected_state = res["state"]
                    st.rerun()
        else:
            st.warning(f"No Indian cities found matching '{search_query}'. Please verify spelling.")

    st.markdown("---")
    
    # Refresh Button
    if st.button("🔄 Refresh Live Readings", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.toast("Cache cleared! Fetching fresh atmospheric readings...")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Quick Links")
    st.markdown("- 🌐 [1_Live_AQI](pages/1_Live_AQI.py)")
    st.markdown("- 📊 [2_City_Comparison](pages/2_City_Comparison.py)")
    st.markdown("- 🏥 [3_Health_Advisory](pages/3_Health_Advisory.py)")
    st.markdown("- 🤖 [4_ML_Prediction](pages/4_ML_Prediction.py)")
    st.markdown("- ℹ️ [5_About_Project](pages/5_About_Project.py)")
    
    st.caption("Data source: Open-Meteo CAMS Atmospheric Assimilation (CPCB NAQI Standards)")

# ---------- Hero Banner ----------
st.markdown(
    f"""
    <div class="hero-banner">
        <h1>🇮🇳 AirWatch India — Live AQI Monitoring & Health Advisory</h1>
        <p>Real-time atmospheric monitoring, official Central Pollution Control Board (CPCB) National AQI calculations, and Machine Learning health intelligence for Indian cities.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Quick City Chips Bar ----------
st.markdown("##### ⚡ Quick Select Indian Metros:")
metro_cols = st.columns(8)
metro_list = ["Delhi", "Mumbai", "Pune", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]

for i, m_city in enumerate(metro_list):
    with metro_cols[i]:
        btn_type = "primary" if st.session_state.selected_city == m_city else "secondary"
        if st.button(m_city, key=f"chip_{m_city}", type=btn_type, use_container_width=True):
            st.session_state.selected_city = m_city
            st.session_state.selected_lat = MAJOR_INDIAN_CITIES[m_city]["lat"]
            st.session_state.selected_lon = MAJOR_INDIAN_CITIES[m_city]["lon"]
            st.session_state.selected_state = MAJOR_INDIAN_CITIES[m_city]["state"]
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Fetch Live Data ----------
with st.spinner(f"Retrieving latest air quality measurements for {st.session_state.selected_city}..."):
    data = fetch_live_air_quality(
        st.session_state.selected_lat,
        st.session_state.selected_lon,
        st.session_state.selected_city
    )

# ---------- Check for API Errors ----------
if data.get("status") == "ERROR":
    st.error(f"⚠️ Live Data Unavailable: {data.get('error_message')}")
    st.info("The application strictly displays verified real-time measurements and does not fabricate readings. Please verify internet access or click 'Refresh Live Readings'.")
    st.stop()

# Extract fields
city_name = data.get("city")
current_state = st.session_state.selected_state
timestamp = data.get("timestamp")
source = data.get("source")
data_type = data.get("data_type")
aqi = data.get("indian_aqi")
category = data.get("indian_category")
cat_info = data.get("category_info", {})
dominant_pol = data.get("dominant_pollutant", "PM2.5")
us_aqi = data.get("us_aqi")
pollutants = data.get("pollutants", {})
advisory = get_advisory_by_category(category)

# ---------- Status & Source Strip ----------
col_meta1, col_meta2 = st.columns([2, 1])
with col_meta1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
            <span class="status-pill status-pill-live">● LIVE SATELLITE & SENSOR STREAM</span>
            <span style="color: #475569; font-size: 0.9rem;">📍 <strong>{city_name}, {current_state}</strong> (Lat: {st.session_state.selected_lat}°, Lon: {st.session_state.selected_lon}°)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_meta2:
    st.markdown(
        f"""
        <div style="text-align: right; color: #64748b; font-size: 0.85rem; margin-bottom: 12px;">
            🕒 <strong>Last Updated:</strong> {timestamp}<br>
            📡 <strong>Source:</strong> {source}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Top Highlights Row: Scorecard & Health Advisory ----------
row1_left, row1_right = st.columns([1, 1.4])

with row1_left:
    st.markdown(
        f"""
        <div class="aqi-scorecard">
            <span style="font-size: 0.88rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                CPCB National AQI (India)
            </span>
            <div class="aqi-big-number" style="color: {cat_info.get('color', '#00b050')};">
                {aqi if aqi is not None else '--'}
            </div>
            <div class="category-badge" style="background-color: {cat_info.get('color', '#00b050')}; color: {cat_info.get('text_color', '#ffffff')};">
                {category}
            </div>
            <div style="font-size: 0.92rem; color: #334155; margin-top: 6px; font-weight: 600;">
                Primary Driver: <span style="color: #0f766e;">{dominant_pol}</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 10px;">
                US EPA AQI: <strong>{us_aqi if us_aqi is not None else 'N/A'}</strong> | Scale: CPCB 0–500 Standard
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1_right:
    st.markdown(
        f"""
        <div class="advisory-box" style="border-left-color: {cat_info.get('color', '#0f766e')};">
            <h4 style="color: {cat_info.get('color', '#0f766e')} !important;">
                🏥 Health Advisory: {category}
            </h4>
            <p style="font-size: 0.95rem; color: #1e293b; margin-bottom: 0.8rem;">
                <strong>Health Impact:</strong> {advisory.get('health_impact')}
            </p>
            <div style="background: #ffffff; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; border: 1px solid #e2e8f0; font-size: 0.88rem;">
                🚶 <strong>General Public:</strong> {advisory.get('general_public')}
            </div>
            <div style="background: #ffffff; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; border: 1px solid #e2e8f0; font-size: 0.88rem;">
                🫁 <strong>Sensitive Groups (Asthma, Heart, Seniors, Kids):</strong> {advisory.get('sensitive_groups')}
            </div>
            <div style="background: #ffffff; border-radius: 8px; padding: 10px 14px; border: 1px solid #e2e8f0; font-size: 0.88rem;">
                😷 <strong>Mask & Air Quality Advice:</strong> {advisory.get('masks')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Key Criteria Pollutants Grid ----------
st.subheader("🧪 Live Pollutant Concentrations & CPCB Sub-Indices")
st.caption("Calculated strictly according to Central Pollution Control Board (CPCB) sub-index linear interpolation breakpoints.")

p_cols = st.columns(6)
key_pollutants = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

for i, p_name in enumerate(key_pollutants):
    p_info = pollutants.get(p_name, {})
    val = p_info.get("value")
    unit = p_info.get("unit", "µg/m³")
    sub = p_info.get("sub_index")
    
    sub_cat_info = get_aqi_category_info(sub) if sub is not None else {}
    sub_color = sub_cat_info.get("color", "#64748b")
    sub_cat_name = sub_cat_info.get("name", "N/A")

    with p_cols[i]:
        val_str = f"{val:.1f}" if val is not None else "--"
        sub_str = f"{int(round(sub))}" if sub is not None else "--"
        st.markdown(
            f"""
            <div class="pollutant-card">
                <div class="pollutant-name">{p_name}</div>
                <div class="pollutant-value">{val_str}</div>
                <div class="pollutant-unit">{unit}</div>
                <div class="pollutant-subindex" style="background-color: {sub_color}20; color: {sub_color}; border: 1px solid {sub_color}50;">
                    Sub-Index: <strong>{sub_str}</strong> ({sub_cat_name})
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Interactive Hourly Trend Preview ----------
hourly_df = data.get("hourly_df")
if hourly_df is not None and not hourly_df.empty:
    st.subheader(f"📈 72-Hour Atmospheric Trend & Forecast for {city_name}")
    st.caption("Displaying 48 hours of historical atmospheric observations plus 24 hours forward forecast.")

    fig = go.Figure()

    if "pm2_5" in hourly_df.columns:
        fig.add_trace(go.Scatter(
            x=hourly_df["time"],
            y=hourly_df["pm2_5"],
            mode="lines+markers",
            name="PM2.5 (µg/m³)",
            line=dict(color="#0f766e", width=2.5),
            marker=dict(size=4)
        ))

    if "pm10" in hourly_df.columns:
        fig.add_trace(go.Scatter(
            x=hourly_df["time"],
            y=hourly_df["pm10"],
            mode="lines",
            name="PM10 (µg/m³)",
            line=dict(color="#d97706", width=2, dash="dot")
        ))

    # CPCB 24-hr standard thresholds for PM2.5 (60 µg/m³) and PM10 (100 µg/m³)
    fig.add_hline(y=60, line_dash="dash", line_color="#00b050", annotation_text="CPCB PM2.5 24h Safe Limit (60 µg/m³)", annotation_position="bottom right")
    fig.add_hline(y=100, line_dash="dash", line_color="#f59e0b", annotation_text="CPCB PM10 24h Safe Limit (100 µg/m³)", annotation_position="top right")

    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Timeline (Asia/Kolkata)",
        yaxis_title="Concentration (µg/m³)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- CPCB National AQI Scale Reference Table ----------
with st.expander("📖 View Official Indian CPCB AQI Breakpoint Classification Table"):
    st.markdown(
        """
        The Indian National Air Quality Index (NAQI) was launched under the **Swachh Bharat Abhiyan** by the 
        Central Pollution Control Board (CPCB) and Ministry of Environment, Forest and Climate Change (MoEFCC).
        
        | AQI Category | Index Range | PM2.5 (µg/m³) | PM10 (µg/m³) | NO₂ (µg/m³) | CO (mg/m³) | Associated Health Impact |
        | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
        | 🟢 **Good** | 0 – 50 | 0 – 30 | 0 – 50 | 0 – 40 | 0 – 1.0 | Minimal impact |
        | 🟡 **Satisfactory** | 51 – 100 | 31 – 60 | 51 – 100 | 41 – 80 | 1.1 – 2.0 | Minor breathing discomfort to sensitive people |
        | 🟠 **Moderately Polluted** | 101 – 200 | 61 – 90 | 101 – 250 | 81 – 180 | 2.1 – 10.0 | Breathing discomfort to people with asthma & heart ailments |
        | 🔴 **Poor** | 201 – 300 | 91 – 120 | 251 – 350 | 181 – 280 | 10.1 – 17.0 | Breathing discomfort to most people on prolonged exposure |
        | 🟣 **Very Poor** | 301 – 400 | 121 – 250 | 351 – 430 | 281 – 400 | 17.1 – 34.0 | Respiratory illness on prolonged exposure |
        | 🟤 **Severe** | 401 – 500 | 250+ | 430+ | 400+ | 34.0+ | Healthy people affected; serious impact on vulnerable groups |
        """
    )

st.markdown("---")

# ---------- Footer ----------
col_foot1, col_foot2 = st.columns([2, 1])
with col_foot1:
    st.caption("🎓 **Third-Year BCS College Mini-Project** | Developed by Student: Gauri Madake | AirWatch India")
with col_foot2:
    st.caption("🔬 Live Atmospheric Assimilation by Copernicus CAMS & Open-Meteo | Zero synthetic data")