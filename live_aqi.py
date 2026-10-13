"""
src/live_aqi.py
Live Air Quality retrieval and Indian National AQI (CPCB NAQI) calculation engine.
Supports Open-Meteo Atmospheric Models (free, no API key required) and
optional WAQI Ground Station API (when token is provided).
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import os
import streamlit as st

# ==============================================================================
# 1. CURATED INDIAN CITIES DATABASE (Strictly India)
# ==============================================================================
MAJOR_INDIAN_CITIES = {
    "Delhi": {
        "state": "Delhi NCT",
        "lat": 28.6139,
        "lon": 77.2090,
        "description": "National Capital Region, major northern monitoring zone"
    },
    "Mumbai": {
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "description": "Financial capital, coastal western region"
    },
    "Pune": {
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "description": "Western Maharashtra plateau, educational & IT hub"
    },
    "Bengaluru": {
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "description": "Deccan plateau, southern IT capital"
    },
    "Hyderabad": {
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "description": "Southern tech & pharmaceutical hub"
    },
    "Chennai": {
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "description": "Coromandel coast, major southeastern industrial port"
    },
    "Kolkata": {
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "description": "Eastern plains & Gangetic delta"
    },
    "Ahmedabad": {
        "state": "Gujarat",
        "lat": 23.0225,
        "lon": 72.5714,
        "description": "Western industrial & commercial center"
    },
    "Lucknow": {
        "state": "Uttar Pradesh",
        "lat": 26.8467,
        "lon": 80.9462,
        "description": "Central Indo-Gangetic Plain"
    },
    "Jaipur": {
        "state": "Rajasthan",
        "lat": 26.9124,
        "lon": 75.7873,
        "description": "Semi-arid northern-western zone"
    },
    "Chandigarh": {
        "state": "Chandigarh UT",
        "lat": 30.7333,
        "lon": 76.7794,
        "description": "Sub-Himalayan plains"
    },
    "Varanasi": {
        "state": "Uttar Pradesh",
        "lat": 25.3176,
        "lon": 82.9739,
        "description": "Middle Gangetic Valley"
    },
    "Patna": {
        "state": "Bihar",
        "lat": 25.5941,
        "lon": 85.1376,
        "description": "Eastern Indo-Gangetic Plain"
    },
    "Bhopal": {
        "state": "Madhya Pradesh",
        "lat": 23.2599,
        "lon": 77.4126,
        "description": "Central Indian plateau"
    },
    "Visakhapatnam": {
        "state": "Andhra Pradesh",
        "lat": 17.6868,
        "lon": 83.2185,
        "description": "Eastern coastal port"
    },
    "Surat": {
        "state": "Gujarat",
        "lat": 21.1702,
        "lon": 72.8311,
        "description": "Western textile & diamond industrial center"
    },
    "Kanpur": {
        "state": "Uttar Pradesh",
        "lat": 26.4499,
        "lon": 80.3319,
        "description": "Indo-Gangetic industrial basin"
    },
    "Nagpur": {
        "state": "Maharashtra",
        "lat": 21.1458,
        "lon": 79.0882,
        "description": "Geographical center of India, Vidarbha"
    },
    "Indore": {
        "state": "Madhya Pradesh",
        "lat": 22.7196,
        "lon": 75.8577,
        "description": "Malwa plateau"
    },
    "Guwahati": {
        "state": "Assam",
        "lat": 26.1445,
        "lon": 91.7362,
        "description": "Northeastern Brahmaputra valley"
    },
    "Amritsar": {
        "state": "Punjab",
        "lat": 31.6340,
        "lat": 31.6340,
        "lon": 74.8723,
        "description": "Northwestern agricultural & transit zone"
    },
    "Kochi": {
        "state": "Kerala",
        "lat": 9.9312,
        "lon": 76.2673,
        "description": "Southwestern Malabar coast"
    },
    "Coimbatore": {
        "state": "Tamil Nadu",
        "lat": 11.0168,
        "lon": 76.9558,
        "description": "Western Ghats rain-shadow plateau"
    },
    "Agra": {
        "state": "Uttar Pradesh",
        "lat": 27.1767,
        "lon": 78.0081,
        "description": "Yamuna basin, Taj Trapezium Zone"
    },
    "Srinagar": {
        "state": "Jammu & Kashmir",
        "lat": 34.0837,
        "lon": 74.7973,
        "description": "Kashmir valley montane climate"
    }
}


# ==============================================================================
# 2. CPCB INDIAN NATIONAL AIR QUALITY INDEX (NAQI) SPECIFICATION
# ==============================================================================
# Official breakpoints published by CPCB (Central Pollution Control Board, MoEFCC)
# Category ranges:
#   Good: 0-50
#   Satisfactory: 51-100
#   Moderately Polluted: 101-200
#   Poor: 201-300
#   Very Poor: 301-400
#   Severe: 401-500
AQI_CATEGORIES = [
    {
        "name": "Good",
        "min": 0,
        "max": 50,
        "color": "#00b050",
        "bg_light": "#e8f8f0",
        "text_color": "#ffffff",
        "summary": "Minimal health impact. Clean air."
    },
    {
        "name": "Satisfactory",
        "min": 51,
        "max": 100,
        "color": "#92d050",
        "bg_light": "#f1fae9",
        "text_color": "#1c3d11",
        "summary": "Minor breathing discomfort to sensitive individuals."
    },
    {
        "name": "Moderately Polluted",
        "min": 101,
        "max": 200,
        "color": "#ffc000",
        "bg_light": "#fff9e6",
        "text_color": "#4a3b00",
        "summary": "Breathing discomfort to people with asthma, heart & lung ailments."
    },
    {
        "name": "Poor",
        "min": 201,
        "max": 300,
        "color": "#ff6600",
        "bg_light": "#fff0e6",
        "text_color": "#ffffff",
        "summary": "Breathing discomfort to most people on prolonged exposure."
    },
    {
        "name": "Very Poor",
        "min": 301,
        "max": 400,
        "color": "#ff0000",
        "bg_light": "#ffe6e6",
        "text_color": "#ffffff",
        "summary": "Respiratory illness on prolonged exposure. Severe risk to elderly/children."
    },
    {
        "name": "Severe",
        "min": 401,
        "max": 500,
        "color": "#7f0000",
        "bg_light": "#f5e6e6",
        "text_color": "#ffffff",
        "summary": "Healthy people affected. Serious health consequences for vulnerable groups."
    }
]

# Pollutant Breakpoints: (B_low, B_high, I_low, I_high)
# Units: PM2.5 (µg/m³), PM10 (µg/m³), NO2 (µg/m³), SO2 (µg/m³), CO (mg/m³), O3 (µg/m³), NH3 (µg/m³)
CPCB_BREAKPOINTS = {
    "pm2_5": [
        (0.0, 30.0, 0, 50),
        (30.1, 60.0, 51, 100),
        (60.1, 90.0, 101, 200),
        (90.1, 120.0, 201, 300),
        (120.1, 250.0, 301, 400),
        (250.1, 500.0, 401, 500)
    ],
    "pm10": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500)
    ],
    "no2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 600.0, 401, 500)
    ],
    "so2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (380.1, 800.0, 201, 300),
        (800.1, 1600.0, 301, 400),
        (1600.1, 2000.0, 401, 500)
    ],
    "co": [  # In mg/m³
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
        (34.01, 50.0, 401, 500)
    ],
    "o3": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
        (748.1, 1000.0, 401, 500)
    ],
    "nh3": [
        (0.0, 200.0, 0, 50),
        (200.1, 400.0, 51, 100),
        (401.1, 800.0, 101, 200),
        (801.1, 1200.0, 201, 300),
        (1201.1, 1800.0, 301, 400),
        (1801.1, 2400.0, 401, 500)
    ]
}


def calculate_sub_index(pollutant_key: str, concentration: float) -> float:
    """
    Computes Indian CPCB sub-index for a specific pollutant concentration using
    linear interpolation between standard breakpoints:
    I = I_low + ((I_high - I_low) / (B_high - B_low)) * (C - B_low)
    """
    if concentration is None or np.isnan(concentration) or concentration < 0:
        return None

    key = pollutant_key.lower()
    if key not in CPCB_BREAKPOINTS:
        return None

    breakpoints = CPCB_BREAKPOINTS[key]

    for (b_low, b_high, i_low, i_high) in breakpoints:
        if b_low <= concentration <= b_high:
            sub = i_low + ((i_high - i_low) / (b_high - b_low)) * (concentration - b_low)
            return round(sub, 1)

    # If concentration exceeds highest breakpoint, extrapolate linearly or cap
    last_b_low, last_b_high, last_i_low, last_i_high = breakpoints[-1]
    if concentration > last_b_high:
        extra = last_i_low + ((last_i_high - last_i_low) / (last_b_high - last_b_low)) * (concentration - last_b_low)
        return min(500.0, round(extra, 1))

    return None


def get_aqi_category_info(aqi_value: float) -> dict:
    """
    Returns category name, color, and summary according to Indian CPCB standards.
    """
    if aqi_value is None or np.isnan(aqi_value):
        return {
            "name": "Data Unavailable",
            "min": 0,
            "max": 0,
            "color": "#808080",
            "bg_light": "#f0f0f0",
            "text_color": "#ffffff",
            "summary": "Measurements are currently insufficient or pending."
        }

    val = round(aqi_value)
    for cat in AQI_CATEGORIES:
        if cat["min"] <= val <= cat["max"]:
            return cat

    if val > 500:
        return AQI_CATEGORIES[-1]  # Severe

    return AQI_CATEGORIES[0]


def calculate_indian_aqi(pollutants: dict) -> dict:
    """
    Calculates overall Indian National AQI from raw pollutant measurements.
    
    CPCB Rule:
    - Overall AQI is the maximum of the individual sub-indices (dominant pollutant).
    - Statutory rule: At least 3 pollutants must be monitored, of which at least one
      must be either PM2.5 or PM10.
    
    Expected pollutants keys:
      pm2_5 (µg/m³), pm10 (µg/m³), no2 (µg/m³), so2 (µg/m³), co (µg/m³ or mg/m³), o3 (µg/m³), nh3 (µg/m³)
    """
    sub_indices = {}
    
    # Handle CO unit: if CO > 50, it is likely in µg/m³ from Open-Meteo, convert to mg/m³
    co_val = pollutants.get("co")
    if co_val is not None and not np.isnan(co_val):
        if co_val > 50.0:  # e.g., 850 µg/m³ -> 0.85 mg/m³
            co_val_mg = co_val / 1000.0
        else:
            co_val_mg = co_val
    else:
        co_val_mg = None

    eval_dict = {
        "pm2_5": pollutants.get("pm2_5"),
        "pm10": pollutants.get("pm10"),
        "no2": pollutants.get("no2"),
        "so2": pollutants.get("so2"),
        "co": co_val_mg,
        "o3": pollutants.get("o3"),
        "nh3": pollutants.get("nh3")
    }

    for p_key, p_val in eval_dict.items():
        if p_val is not None:
            sub = calculate_sub_index(p_key, p_val)
            if sub is not None:
                sub_indices[p_key] = sub

    if not sub_indices:
        return {
            "aqi": None,
            "category": "Data Unavailable",
            "category_info": get_aqi_category_info(None),
            "dominant_pollutant": "None",
            "sub_indices": {},
            "is_valid_cpcb": False,
            "message": "No valid pollutant measurements available."
        }

    # Check CPCB criteria
    has_particulate = ("pm2_5" in sub_indices) or ("pm10" in sub_indices)
    has_three_pollutants = len(sub_indices) >= 3
    is_valid_cpcb = has_particulate and has_three_pollutants

    dominant_pollutant = max(sub_indices, key=sub_indices.get)
    overall_aqi = sub_indices[dominant_pollutant]

    # Map dominant key to readable label
    name_map = {
        "pm2_5": "PM2.5",
        "pm10": "PM10",
        "no2": "NO₂",
        "so2": "SO₂",
        "co": "CO",
        "o3": "O₃",
        "nh3": "NH₃"
    }

    category_info = get_aqi_category_info(overall_aqi)

    return {
        "aqi": int(round(overall_aqi)),
        "category": category_info["name"],
        "category_info": category_info,
        "dominant_pollutant": name_map.get(dominant_pollutant, dominant_pollutant),
        "dominant_pollutant_raw": dominant_pollutant,
        "sub_indices": sub_indices,
        "is_valid_cpcb": is_valid_cpcb,
        "pollutant_count": len(sub_indices),
        "co_mg_m3": round(co_val_mg, 2) if co_val_mg is not None else None
    }


# ==============================================================================
# 3. INDIA-ONLY GEOCODING & CITY VALIDATION
# ==============================================================================
def search_indian_cities(query: str, max_results: int = 5) -> list:
    """
    Searches for cities and strictly enforces India validation (country_code == 'IN').
    Prevents foreign locations with identical names (e.g. Pune in Timor-Leste).
    """
    if not query or len(query.strip()) < 2:
        return []

    q = query.strip()

    # First check curated dictionary for exact or prefix match
    curated_matches = []
    for city_name, meta in MAJOR_INDIAN_CITIES.items():
        if q.lower() in city_name.lower():
            curated_matches.append({
                "name": city_name,
                "state": meta["state"],
                "country": "India",
                "country_code": "IN",
                "lat": meta["lat"],
                "lon": meta["lon"],
                "source": "Curated Indian Database"
            })

    # Query Open-Meteo Geocoding API
    api_matches = []
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=10&language=en&format=json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            for r in results:
                country_code = r.get("country_code", "").upper()
                country = r.get("country", "")
                
                # Strict check: MUST BE INDIA
                if country_code == "IN" or country.lower() == "india":
                    name = r.get("name", "")
                    state = r.get("admin1", "India")
                    # Avoid duplicate if already in curated_matches
                    if not any(c["name"].lower() == name.lower() for c in curated_matches):
                        api_matches.append({
                            "name": name,
                            "state": state,
                            "country": "India",
                            "country_code": "IN",
                            "lat": round(float(r.get("latitude")), 4),
                            "lon": round(float(r.get("longitude")), 4),
                            "source": "Open-Meteo Geocoding"
                        })
    except Exception as e:
        # Geocoding network fail, rely on curated list
        pass

    combined = curated_matches + api_matches
    return combined[:max_results]


# ==============================================================================
# 4. LIVE AIR QUALITY FETCHER (Open-Meteo API + Optional WAQI)
# ==============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_live_air_quality(lat: float, lon: float, city_name: str = "Unknown") -> dict:
    """
    Fetches real-time air quality readings and hourly history/forecast.
    Uses Open-Meteo Air Quality API (free, reliable, global coverage with CAMS).
    Cached for 5 minutes (300 seconds) to ensure responsive interaction and prevent rate limiting.
    
    Returns structured dictionary with:
    - current readings (pm2.5, pm10, no2, so2, co, o3, nh3)
    - calculated Indian CPCB NAQI
    - US AQI and European EAQI for reference
    - 72-hour hourly dataframe
    - status ('LIVE', 'CACHED', 'ERROR')
    - timestamp and data attribution
    """
    endpoint = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,ammonia,european_aqi,us_aqi",
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,ammonia,us_aqi",
        "past_days": 2,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata"
    }

    try:
        response = requests.get(endpoint, params=params, timeout=8)
        if response.status_code != 200:
            return {
                "status": "ERROR",
                "error_message": f"API returned status code {response.status_code}: {response.text[:200]}",
                "city": city_name,
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
            }

        data = response.json()
        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Extract current measurements
        pm2_5 = current.get("pm2_5")
        pm10 = current.get("pm10")
        no2 = current.get("nitrogen_dioxide")
        so2 = current.get("sulphur_dioxide")
        co = current.get("carbon_monoxide")  # in µg/m³
        o3 = current.get("ozone")
        nh3 = current.get("ammonia")
        us_aqi = current.get("us_aqi")
        european_aqi = current.get("european_aqi")
        data_time = current.get("time")

        pollutants_dict = {
            "pm2_5": pm2_5,
            "pm10": pm10,
            "no2": no2,
            "so2": so2,
            "co": co,
            "o3": o3,
            "nh3": nh3
        }

        # Calculate official Indian CPCB AQI
        cpcb_result = calculate_indian_aqi(pollutants_dict)

        # Build hourly DataFrame for trend analysis
        df_hourly = pd.DataFrame()
        if hourly and "time" in hourly:
            df_hourly["time"] = pd.to_datetime(hourly["time"])
            df_hourly["pm2_5"] = hourly.get("pm2_5", [])
            df_hourly["pm10"] = hourly.get("pm10", [])
            df_hourly["no2"] = hourly.get("nitrogen_dioxide", [])
            df_hourly["so2"] = hourly.get("sulphur_dioxide", [])
            df_hourly["co"] = hourly.get("carbon_monoxide", [])
            df_hourly["o3"] = hourly.get("ozone", [])
            df_hourly["us_aqi"] = hourly.get("us_aqi", [])

        # Format update timestamp
        if data_time:
            formatted_time = data_time.replace("T", " ") + " IST"
        else:
            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

        return {
            "status": "LIVE",
            "city": city_name,
            "lat": lat,
            "lon": lon,
            "timestamp": formatted_time,
            "source": "Open-Meteo Air Quality (Copernicus CAMS & ECMWF)",
            "data_type": "Latest Available Atmospheric Observation & Assimilation",
            "pollutants": {
                "PM2.5": {"value": pm2_5, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("pm2_5")},
                "PM10": {"value": pm10, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("pm10")},
                "NO2": {"value": no2, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("no2")},
                "SO2": {"value": so2, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("so2")},
                "CO": {"value": round(co / 1000.0, 2) if co is not None else None, "unit": "mg/m³", "sub_index": cpcb_result["sub_indices"].get("co")},
                "O3": {"value": o3, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("o3")},
                "NH3": {"value": nh3, "unit": "µg/m³", "sub_index": cpcb_result["sub_indices"].get("nh3")}
            },
            "indian_aqi": cpcb_result["aqi"],
            "indian_category": cpcb_result["category"],
            "category_info": cpcb_result["category_info"],
            "dominant_pollutant": cpcb_result["dominant_pollutant"],
            "sub_indices": cpcb_result["sub_indices"],
            "is_valid_cpcb": cpcb_result["is_valid_cpcb"],
            "us_aqi": us_aqi,
            "european_aqi": european_aqi,
            "hourly_df": df_hourly,
            "raw_current": current
        }

    except requests.exceptions.Timeout:
        return {
            "status": "ERROR",
            "error_message": "Connection to the Air Quality API timed out (server took > 8 seconds to respond).",
            "city": city_name,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "ERROR",
            "error_message": f"Network request error: {str(e)}",
            "city": city_name,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error_message": f"Unexpected error while processing air quality data: {str(e)}",
            "city": city_name,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }


def fetch_waqi_air_quality(lat: float, lon: float, token: str = None) -> dict:
    """
    Fetches real-time CPCB ground-station readings from WAQI API if a valid token is provided.
    """
    if not token:
        token = os.getenv("WAQI_API_TOKEN", "")

    if not token or token.strip() == "" or token == "demo":
        return {
            "status": "UNAVAILABLE",
            "message": "WAQI Ground-Station integration requires a valid personal API token. Obtain free from https://aqicn.org/data-platform/token/"
        }

    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token.strip()}"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "ok":
                d = data.get("data", {})
                return {
                    "status": "LIVE",
                    "aqi": d.get("aqi"),
                    "dominant_pollutant": d.get("dominentpol"),
                    "station_name": d.get("city", {}).get("name"),
                    "attributions": [a.get("name") for a in d.get("attributions", [])],
                    "time": d.get("time", {}).get("s")
                }
            else:
                return {"status": "ERROR", "message": data.get("data", "Invalid response from WAQI")}
        return {"status": "ERROR", "message": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
