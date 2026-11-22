import streamlit as st
import requests
from datetime import datetime, timedelta, timezone

# ---------- PAGE CONFIGURATION ----------
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
st.caption(
    "Environmental Risk Monitoring • Multi-Hazard Assessment • Smart Alerts"
)

st.info(
    "Weather readings are fetched automatically. "
    "Water level, soil moisture and seismic readings are currently manual. "
    "Risk levels use illustrative prototype rules, not official warnings."
)

# ---------- WEATHER API ----------
@st.cache_data(ttl=600)
def fetch_weather(city):

    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=15
    )

    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        raise ValueError("City not found. Try another city.")

    place = geo_data["results"][0]

    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m,"
                "surface_pressure"
            ),
            "wind_speed_unit": "kmh",
            "timezone": "auto"
        },
        timeout=15
    )

    weather_response.raise_for_status()
    weather_data = weather_response.json()

    return place, weather_data["current"]


# ---------- INDIA EARTHQUAKE MONITORING ----------
def fetch_india_earthquakes():

    start_date = (
        datetime.now(timezone.utc) - timedelta(days=30)
    ).strftime("%Y-%m-%d")

    response = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={
            "format": "geojson",
            "starttime": start_date,
            "minlatitude": 6,
            "maxlatitude": 37,
            "minlongitude": 68,
            "maxlongitude": 98,
            "minmagnitude": 2.5,
            "orderby": "time",
            "limit": 200
        },
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    events = []

    for feature in data.get("features", []):

        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get(
            "coordinates", [None, None, None]
        )

        event_time = properties.get("time")
        magnitude = properties.get("mag")

        if event_time is None:
            continue

        readable_time = datetime.fromtimestamp(
            event_time / 1000,
            tz=timezone.utc
        ).astimezone().strftime("%d %b %Y, %I:%M %p")

        events.append({
            "Magnitude": (
                round(magnitude, 1)
                if magnitude is not None else "N/A"
            ),
            "Location": properties.get("place", "Unknown location"),
            "Date & Time": readable_time,
            "Depth (km)": (
                round(coordinates[2], 1)
                if len(coordinates) > 2
                and coordinates[2] is not None
                else "N/A"
            ),
            "USGS Details": properties.get("url", "")
        })

    return events


# ---------- SESSION DEFAULTS ----------
defaults = {
    "temperature": 25.0,
    "humidity": 45.0,
    "rainfall": 40.0,
    "wind": 25.0,
    "pressure": 1010.0,
    "water": 1.5,
    "soil": 50.0,
    "seismic": 2.5
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- AUTOMATIC WEATHER SECTION ----------
st.subheader("🌦️ Automatic Weather Monitoring")

city = st.text_input(
    "Enter your city",
    value="Pune"
)

if st.button("🌍 FETCH LIVE WEATHER", use_container_width=True):

    try:
        place, current = fetch_weather(city.strip())

        st.session_state["temperature"] = float(
            current["temperature_2m"]
        )
        st.session_state["humidity"] = float(
            current["relative_humidity_2m"]
        )
        st.session_state["rainfall"] = float(
            current["precipitation"]
        )
        st.session_state["wind"] = float(
            current["wind_speed_10m"]
        )
        st.session_state["pressure"] = float(
            current["surface_pressure"]
        )

        st.session_state["weather_city"] = place["name"]
        st.session_state["weather_time"] = current["time"]

        st.success(
            f"Weather successfully fetched for {place['name']}!"
        )

    except (requests.RequestException, ValueError, KeyError) as error:
        st.error(f"Weather fetching failed: {error}")


# ---------- DISPLAY FETCHED WEATHER ----------
if "weather_city" in st.session_state:

    st.success(
        f"📍 Location: {st.session_state['weather_city']} "
        f"| Weather time: {st.session_state['weather_time']}"
    )

    st.markdown("### Current Weather Readings")

    w1, w2, w3, w4, w5 = st.columns(5)

    w1.metric("Temperature", f"{st.session_state['temperature']:.1f} °C")
    w2.metric("Humidity", f"{st.session_state['humidity']:.1f}%")
    w3.metric("Precipitation", f"{st.session_state['rainfall']:.1f} mm")
    w4.metric("Wind Speed", f"{st.session_state['wind']:.1f} km/h")
    w5.metric("Pressure", f"{st.session_state['pressure']:.1f} hPa")


# ---------- EARTHQUAKE MONITORING SECTION ----------
st.divider()
st.subheader("🌎 India Earthquake Monitoring")

st.caption(
    "Recent recorded earthquake events from the USGS public earthquake feed. "
    "Approximate India-region geographic filter • Magnitude 2.5+ • Last 30 days."
)

# Fetch once when the session starts
if "earthquake_events" not in st.session_state:
    try:
        st.session_state["earthquake_events"] = (
            fetch_india_earthquakes()
        )
        st.session_state["earthquake_error"] = None
        st.session_state["earthquake_updated"] = (
            datetime.now().astimezone().strftime("%d %b %Y, %I:%M %p")
        )
    except (requests.RequestException, ValueError) as error:
        st.session_state["earthquake_events"] = []
        st.session_state["earthquake_error"] = str(error)

# Manual refresh
if st.button("🔄 REFRESH EARTHQUAKE DATA", use_container_width=True):

    try:
        st.session_state["earthquake_events"] = (
            fetch_india_earthquakes()
        )
        st.session_state["earthquake_error"] = None
        st.session_state["earthquake_updated"] = (
            datetime.now().astimezone().strftime("%d %b %Y, %I:%M %p")
        )
        st.success("Earthquake data refreshed successfully!")

    except (requests.RequestException, ValueError) as error:
        st.session_state["earthquake_error"] = str(error)

if st.session_state.get("earthquake_error"):

    st.warning(
        "Earthquake data could not be fetched. "
        + st.session_state["earthquake_error"]
    )

else:

    events = st.session_state["earthquake_events"]

    st.caption(
        "Last updated: "
        + st.session_state.get("earthquake_updated", "Not available")
    )

    if events:

        magnitudes = [
            event["Magnitude"]
            for event in events
            if isinstance(event["Magnitude"], (int, float))
        ]

        largest = max(magnitudes) if magnitudes else 0

        e1, e2 = st.columns(2)

        e1.metric("Recorded Events Retrieved", len(events))
        e2.metric("Largest Magnitude", f"{largest:.1f}")

        st.markdown("### Recent Earthquake Events")

        st.dataframe(
            events[:10],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Showing up to 10 of the retrieved events. "
            "The geographic bounding box may include nearby border or offshore events."
        )

    else:

        st.info(
            "No matching earthquake events were returned "
            "for this region and time period."
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
st.divider()
st.subheader("📡 Environmental Monitoring Inputs")

st.write(
    "Weather values are populated automatically when available. "
    "Water level, soil moisture and seismic readings can be adjusted manually."
)

with st.form("disaster_inputs"):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        temperature = st.number_input(
            "Temperature (°C)", -20.0, 60.0,
            key="temperature"
        )

        humidity = st.number_input(
            "Humidity (%)", 0.0, 100.0,
            key="humidity"
        )

    with c2:
        rainfall = st.number_input(
            "Precipitation (mm)", 0.0, 1000.0,
            key="rainfall"
        )

        wind = st.number_input(
            "Wind speed (km/h)", 0.0, 300.0,
            key="wind"
        )

    with c3:
        water = st.number_input(
            "Water level (m)", 0.0, 20.0,
            key="water"
        )

        soil = st.number_input(
            "Soil moisture (%)", 0.0, 100.0,
            key="soil"
        )

    with c4:
        pressure = st.number_input(
            "Pressure (hPa)", 800.0, 1100.0,
            key="pressure"
        )

        seismic = st.number_input(
            "Seismic activity reading", 0.0, 10.0,
            key="seismic"
        )

    submitted = st.form_submit_button(
        "🔍 ANALYSE DISASTER RISKS",
        use_container_width=True
    )


# ---------- RESULTS ----------
if submitted:

    results = [
        ("🌊 Flood", flood_risk(temperature * 0 + rainfall, water, soil)),
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

    st.caption(
        "Assessment generated: "
        + datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
    )

    m1, m2, m3 = st.columns(3)

    m1.metric("🔴 High Risk", high_count)
    m2.metric("🟠 Medium Risk", medium_count)
    m3.metric("🟢 Low Risk", low_count)

    if high_count > 0:
        st.error(
            "HIGH RISK CONDITIONS: Review affected categories "
            "and follow official local guidance."
        )
    elif medium_count > 0:
        st.warning(
            "MODERATE CONDITIONS: Continue monitoring "
            "and check official updates."
        )
    else:
        st.success(
            "LOW RISK: No high or medium prototype thresholds were reached."
        )

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

    with st.expander("View environmental readings"):

        st.write({
            "Temperature (°C)": temperature,
            "Humidity (%)": humidity,
            "Precipitation (mm)": rainfall,
            "Wind speed (km/h)": wind,
            "Water level (m)": water,
            "Soil moisture (%)": soil,
            "Pressure (hPa)": pressure,
            "Seismic activity reading": seismic
        })

    st.caption(
        "Important: This is an educational prototype. "
        "It does not predict earthquakes or replace official disaster alerts. "
        "The earthquake feed shows recorded events and does not predict future events. "
        "Weather readings are not physical IoT sensor measurements. "
        "Thresholds require validation before real-world use."
    )

else:

    st.info(
        "Fetch weather data or enter environmental readings, "
        "then click ANALYSE DISASTER RISKS."
    )


# ---------- FOOTER ----------
st.divider()

st.caption(
    "AI-Based Disaster Alert and Smart Response System "
    "| Student Project Prototype"
)
