# 🇮🇳 AirWatch India — Live AQI Monitoring & Health Advisory System

> **Bachelor of Computer Science (BCS) — Year III College Mini-Project**  
> *Developed for Academic Evaluation & Environmental Health Informatics*

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.43-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random--Forest-F7931E.svg)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive--Charts-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()

---

## 📌 1. Project Overview & Problem Statement

Air pollution is one of the most pressing environmental health challenges across India. Particulate matter ($PM_{2.5}$ and $PM_{10}$) frequently crosses hazardous thresholds due to vehicular congestion, stubble burning, and meteorological thermal inversions.

**AirWatch India** is a data-connected, responsive web application engineered to solve three major challenges:
1. **Statutory Scale Incompatibilities:** Many commercial apps report air quality using US EPA or Chinese scales. AirWatch India strictly implements the official **Central Pollution Control Board (CPCB) National Air Quality Index (NAQI)** standards published by the Ministry of Environment, Forest and Climate Change (MoEFCC).
2. **Actionable Health Guidance:** Converts raw pollutant data into personalized, actionable health advisories for high-risk demographics (asthma patients, children, pregnant women, elderly).
3. **Machine Learning Intelligence:** Reuses a pre-trained **Random Forest Regressor** to predict AQI from pollutant interactions, enabling scenario simulation and live-versus-model comparative analytics.

> ⚠️ **Zero Synthetic Data Guarantee:** This is a real data-connected application. It connects live to atmospheric assimilation sensors and never manufactures fake readings.

---

## 🏗️ 2. System Architecture & Workflows

### A. Live Telemetry Pipeline Flow
```
[ Open-Meteo CAMS Atmospheric API ]
                 │
                 ▼
[ India-Only Validation Layer ] (Filters country_code == 'IN')
                 │
                 ▼
[ CPCB NAQI Sub-Index Engine ] (Piecewise Linear Interpolation)
                 │
                 ▼
[ Live Dashboard & Health Advisory ] (Streamlit + Plotly Charts)
```

### B. Machine Learning Training & Inference Workflow
```
[ Historical Dataset (city_day.csv) ] 29,531 records
                 │
                 ▼
[ Data Preprocessing & 80/20 Train-Test Split ]
                 │
                 ▼
[ RandomForestRegressor (100 Trees, random_state=42) ]
                 │
                 ▼
[ Model Evaluation ] Verified MAE: 20.55 | Verified R²: 0.9096
                 │
                 ▼
[ Serialized Weights ] aqi_model.pkl & feature_columns.pkl
                 │
                 ▼
[ Multi-Mode Inference ] Live Stream Bridge & 12-Feature Simulator
```

---

## 🧪 3. Indian CPCB NAQI Calculation Engine

According to statutory guidelines from the Central Pollution Control Board (CPCB):
1. **Sub-Index Formula:** For any pollutant concentration $C$, its sub-index $I$ is calculated via:
   $$I = I_{low} + \frac{I_{high} - I_{low}}{B_{high} - B_{low}} \times (C - B_{low})$$
   where $[B_{low}, B_{high}]$ are pollutant breakpoints and $[I_{low}, I_{high}]$ are category index bounds.
2. **Overall AQI Rule:** Overall AQI is the **maximum of all sub-indices** (the *dominant pollutant*).
3. **CPCB Breakpoints:**
   - 🟢 **Good (0 – 50):** $PM_{2.5} \le 30$, $PM_{10} \le 50$, $NO_2 \le 40$, $CO \le 1.0$ mg/m³
   - 🟡 **Satisfactory (51 – 100):** $PM_{2.5} \le 60$, $PM_{10} \le 100$, $NO_2 \le 80$, $CO \le 2.0$ mg/m³
   - 🟠 **Moderately Polluted (101 – 200):** $PM_{2.5} \le 90$, $PM_{10} \le 250$, $NO_2 \le 180$, $CO \le 10.0$ mg/m³
   - 🔴 **Poor (201 – 300):** $PM_{2.5} \le 120$, $PM_{10} \le 350$, $NO_2 \le 280$, $CO \le 17.0$ mg/m³
   - 🟣 **Very Poor (301 – 400):** $PM_{2.5} \le 250$, $PM_{10} \le 430$, $NO_2 \le 400$, $CO \le 34.0$ mg/m³
   - 🟤 **Severe (401 – 500):** $PM_{2.5} > 250$, $PM_{10} > 430$, $NO_2 > 400$, $CO > 34.0$ mg/m³

---

## 🤖 4. Machine Learning Model Verification

The project integrates a pre-trained `RandomForestRegressor` serialized via Joblib:

| Parameter / Metric | Verified Value | Source / Evidence |
| :--- | :--- | :--- |
| **Algorithm** | Random Forest Regressor (100 Trees) | `aqi_model.pkl` |
| **Training Dataset** | CPCB `city_day.csv` (2015–2020) | CAAQMS Indian stations |
| **Training Split** | 80% Train, 20% Test (`random_state=42`) | Notebook Cell 17 |
| **Target Variable** | Recorded Indian AQI | Float continuous |
| **Input Features (12)** | `PM2.5`, `PM10`, `NO`, `NO2`, `NOx`, `NH3`, `CO`, `SO2`, `O3`, `Benzene`, `Toluene`, `Xylene` | `feature_columns.pkl` |
| **Verified Test R² Score** | **0.9096 (90.96% variance)** | Notebook Cell 20 Output |
| **Verified Test MAE** | **20.55 AQI points** | Notebook Cell 20 Output |
| **Observed Baseline** | R² ~0.8803, MAE ~19.96 | Prior experimental run |
| **Top Driver Pollutants** | **PM2.5 (49.07%)**, **CO (36.81%)** | Feature Importance Gini Splits |

---

## 🌐 5. Live Telemetry API: Selection & Setup

### Selected Primary Provider: **Open-Meteo Air Quality API**
- **Cost & Access:** **100% Free, NO API Key Required**.
- **Data Source:** European Copernicus Atmosphere Monitoring Service (CAMS) & ECMWF numerical atmospheric modeling.
- **Coverage:** Universal coordinate coverage across the entire Indian subcontinent.
- **Pollutants Monitored:** $PM_{2.5}$, $PM_{10}$, $NO_2$, $SO_2$, $CO$, $O_3$, $NH_3$ in physical concentrations ($\mu g/m^3$).
- **Uptime:** High reliability, zero rate-limit blocks for academic usage.

### Optional Ground-Station Provider: **WAQI (World Air Quality Index)**
- If you have an API token from [WAQI Data Platform](https://aqicn.org/data-platform/token/), create a `.env` file:
  ```env
  WAQI_API_TOKEN=your_token_here
  ```
- *Note:* The application works completely out-of-the-box without requiring this token.

---

## 📁 6. Project Structure

```
AQI Project/
├── app.py                      # Primary Home Dashboard & Overview
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation & Viva prep
├── .env.example                # Environment configuration template
├── .gitignore                  # Git ignore rules
├── aqi_model.pkl               # Serialized Random Forest Regressor (165 MB)
├── feature_columns.pkl         # Serialized 12-feature schema
├── AQI_Project (2).ipynb       # Jupyter notebook with training & verification
├── assets/
│   └── style.css               # Modern green, teal, white & dark navy stylesheet
├── data/
│   └── city_day.csv            # Historical CPCB dataset (2015–2020)
├── src/
│   ├── live_aqi.py             # CPCB NAQI engine, Open-Meteo client & India search
│   ├── prediction.py           # ML inference pipeline, feature mapping & explainability
│   ├── health_advisory.py      # CPCB health advisories & activity risk calculator
│   └── data_processing.py      # Historical dataset loader & aggregation utilities
└── pages/
    ├── 1_Live_AQI.py           # Deep-dive city page (gauge charts & 72h time-series)
    ├── 2_City_Comparison.py    # Multi-city rankings & historical comparative trends
    ├── 3_Health_Advisory.py    # Health portal, mask guide & interactive safety calculator
    ├── 4_ML_Prediction.py      # 4 ML inference modes, simulator & ground-truth tester
    └── 5_About_Project.py      # College methodology, architecture & BCS viva questions
```

---

## 🚀 7. How to Run the Application in VS Code on Windows

### Step 1: Open the Project in VS Code
1. Open **VS Code**.
2. Go to **File → Open Folder...** and select `AQI Project`.

### Step 2: Open PowerShell Terminal
In VS Code, press ``Ctrl + ` `` (backtick) or go to **Terminal → New Terminal**.

### Step 3: Activate the Virtual Environment
Activate the existing virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays a script execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` and retry activation).*

### Step 4: Install Any Missing Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Launch the Streamlit Web Application
```powershell
streamlit run app.py
```

Streamlit will launch local server and open your browser automatically:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

---

## 🎓 8. BCS College Viva Defense Q&A

**Q1: How do you justify that the live data is real and not hardcoded?**  
*Answer:* The application connects asynchronously to the Open-Meteo Air Quality REST endpoint (`https://air-quality-api.open-meteo.com/v1/air-quality`) passing the latitude and longitude of the chosen Indian city. The raw payload containing ISO 8601 timestamps and pollutant concentrations in $\mu g/m^3$ is dynamically parsed and passed to our CPCB sub-index math engine. Clicking 'Refresh Live Readings' invalidates the 5-minute memory cache and triggers an updated HTTP request.

**Q2: What is the difference between statutory CPCB AQI and ML Predicted AQI?**  
*Answer:* CPCB AQI is a regulatory index derived using a piecewise maximum sub-index rule (the worst pollutant determines the score). In contrast, the Random Forest model is a statistical non-linear regression ensemble that models the combined interaction of all 12 pollutants based on 5 years of historical training data.

**Q3: Why was CO divided by 1000 in your live ML prediction?**  
*Answer:* Dimension and unit alignment. In the historical training dataset `city_day.csv`, Carbon Monoxide (CO) was recorded in milligrams per cubic meter ($mg/m^3$), whereas the Open-Meteo API returns CO in micrograms per cubic meter ($\mu g/m^3$). Feeding raw $\mu g/m^3$ (e.g. 1000) into a model expecting $mg/m^3$ (e.g. 1.0) would distort the decision trees.

---

## ⚖️ 9. Medical & Data Disclaimer

*AirWatch India is developed strictly for educational, academic, and general awareness purposes. It retrieves data from third-party atmospheric models and does not measure air quality directly. Health advisories are based on published public health baselines and do not substitute for professional medical diagnoses.*
