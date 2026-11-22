import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Disaster Alert & Smart Response",
    page_icon="🌍",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: #0b1220;
    color: #f1f5f9;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #e2e8f0;
}
[data-testid="stMetric"] {
    background: #172338;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #293b55;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🌍 Disaster Alert & Smart Response System")
st.caption("Environmental Risk Monitoring • Multi-Hazard Assessment • Smart Alerts")

st.info(
    "Prototype mode: Enter sample environmental readings below. "
    "Risk levels are based on illustrative rule-based thresholds, "
    "not live sensor data or official warnings."
)

# ---------- RISK FUNCTIONS ----------
def flood_risk(rain, water, soil):
    if rain >= 100 or water >= 4.0 or soil >= 90:
        return "HIGH", "Severe rainfall, water level or soil saturation threshold reached."
    if rain >= 50 or water >= 2.5 or soil >= 70:
        return "MEDIUM", "Rainfall, water level or soil moisture is elevated."
    return "LOW", "No flood threshold reached."

def cyclone_risk(wind, pressure, rain):
    if wind >= 100 or pressure <= 980:
        return "HIGH", "High wind speed or very low pressure detected."
    if wind >= 60 or pressure <= 1000 or rain >= 100:
        return "MEDIUM", "Wind, pressure or rainfall conditions are elevated."
    return "LOW", "No cyclone threshold reached."

def wildfire_risk(temp, humidity, wind):
    if temp >= 40 and humidity <= 30 and wind >= 40:
        return "HIGH", "Hot, dry and windy conditions detected."
    if temp >= 35 and humidity <= 50:
        return "MEDIUM", "Temperature and humidity indicate elevated fire-weather conditions."
    return "LOW", "No wildfire threshold reached."

def landslide_risk(rain, soil):
    if rain >= 150 or soil >= 90:
        return "HIGH", "Very heavy rainfall or high soil moisture detected."
    if rain >= 75 or soil >= 70:
        return "MEDIUM", "Rainfall or soil moisture is elevated."
    return "LOW", "No landslide threshold reached."

def extreme_weather_risk(temp, wind):
    if temp >= 45 or wind >= 120:
        return "HIGH", "Extreme temperature or wind threshold reached."
    if temp >= 38 or wind >= 70:
        return "MEDIUM", "Temperature or wind conditions are elevated."
    return "LOW", "No extreme-weather threshold reached."

def earthquake_risk(seismic):
    if seismic >= 6:
        return "HIGH", "Seismic activity reading is in the high prototype category."
    if seismic >= 4:
        return "MEDIUM", "Seismic activity reading is in the medium prototype category."
    return "LOW", "Seismic activity reading is in the low prototype category."

# ---------- INPUT FORM ----------
st.subheader("📡 Environmental Monitoring Inputs")
st.write("Enter readings to assess all six hazard categories.")

with st.form("disaster_inputs"):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        temperature = st.number_input("Temperature (°C)", -20.0, 60.0, 25.0)
        humidity = st.number_input("Humidity (%)", 0.0, 100.0, 45.0)

    with c2:
        rainfall = st.number_input("Rainfall (mm)", 0.0, 1000.0, 40.0)
        wind = st.number_input("Wind speed (km/h)", 0.0, 300.0, 25.0)

    with c3:
        water = st.number_input("Water level (m)", 0.0, 20.0, 1.5)
        soil = st.number_input("Soil moisture (%)", 0.0, 100.0, 50.0)

    with c4:
        pressure = st.number_input("Pressure (hPa)", 800.0, 1100.0, 1010.0)
        seismic = st.number_input("Seismic activity reading", 0.0, 10.0, 2.5)

    submitted = st.form_submit_button(
        "🔍 ANALYSE DISASTER RISKS",
        use_container_width=True
    )

# ---------- RESULTS ----------
if submitted:
    results = [
        ("🌊 Flood", flood_risk(rainfall, water, soil)),
        ("🌀 Cyclone", cyclone_risk(wind, pressure, rainfall)),
        ("🔥 Wildfire", wildfire_risk(temperature, humidity, wind)),
        ("⛰️ Landslide", landslide_risk(rainfall, soil)),
        ("🌡️ Extreme Weather", extreme_weather_risk(temperature, wind)),
        ("🌎 Seismic Activity", earthquake_risk(seismic))
    ]

    levels = [result[1][0] for result in results]
    high_count = levels.count("HIGH")
    medium_count = levels.count("MEDIUM")
    low_count = levels.count("LOW")

    st.divider()
    st.subheader("🚨 Disaster Risk Assessment")
    st.caption("Assessment generated: " + datetime.now().strftime("%d %b %Y, %I:%M:%S %p"))

    m1, m2, m3 = st.columns(3)
    m1.metric("🔴 High Risk", high_count)
    m2.metric("🟠 Medium Risk", medium_count)
    m3.metric("🟢 Low Risk", low_count)

    if high_count > 0:
        st.error("HIGH RISK CONDITIONS: Review the affected categories and follow official local guidance.")
    elif medium_count > 0:
        st.warning("MODERATE CONDITIONS: Continue monitoring and check official updates.")
    else:
        st.success("LOW RISK: No high or medium prototype thresholds were reached.")

    st.subheader("Hazard-wise Results")
    cards = st.columns(3)

    for index, (name, (level, reason)) in enumerate(results):
        with cards[index % 3]:
            st.markdown(f"### {name}")
            if level == "HIGH":
                st.error(f"🔴 {level}")
            elif level == "MEDIUM":
                st.warning(f"🟠 {level}")
            else:
                st.success(f"🟢 {level}")
            st.write(reason)

    with st.expander("View entered environmental readings"):
        st.write({
            "Temperature (°C)": temperature,
            "Humidity (%)": humidity,
            "Rainfall (mm)": rainfall,
            "Wind speed (km/h)": wind,
            "Water level (m)": water,
            "Soil moisture (%)": soil,
            "Pressure (hPa)": pressure,
            "Seismic activity reading": seismic
        })

    st.caption(
        "Important: This is an educational prototype. "
        "It does not predict earthquakes or replace official disaster alerts. "
        "Thresholds require validation before real-world use."
    )

else:
    st.info("Enter the environmental readings above and click ANALYSE DISASTER RISKS to view results.")

# ---------- FOOTER ----------
st.divider()
st.caption("AI-Based Disaster Alert and Smart Response System | Student Project Prototype")
