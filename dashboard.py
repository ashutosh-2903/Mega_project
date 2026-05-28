import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from firebase_config import db

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Telematics Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ======================================================
# CUSTOM BACKGROUND
# ======================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right,
        #0f2027,
        #203a43,
        #2c5364);
    color: white;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.4);
}

/* Plotly */
.js-plotly-plot {
    border-radius: 15px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# TITLE
# ======================================================
st.title("🚗 Smart Fleet Dashboard")
st.caption("Live Vehicle Tracking + Route History")

# ======================================================
# LOAD FIRESTORE DATA
# ======================================================
@st.cache_data(ttl=30)
def load_data():

    docs = db.collection("telemetry").stream()

    data = []

    for doc in docs:
        data.append(doc.to_dict())

    return pd.DataFrame(data)

# ======================================================
# FETCH DATA
# ======================================================
try:

    df = load_data()

except Exception as e:

    st.error(f"Firestore Error: {e}")
    st.stop()

# ======================================================
# EMPTY CHECK
# ======================================================
if df.empty:

    st.warning("No telemetry data found")
    st.stop()

# ======================================================
# CLEAN DATA
# ======================================================
for col in ["latitude", "longitude", "speed"]:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# remove invalid rows
df = df.dropna(
    subset=["latitude", "longitude"]
)

# sort timestamp
if "timestamp" in df.columns:

    try:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        df = df.sort_values("timestamp")

    except:
        pass

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("🎛️ Controls")

# vehicle filter
if "vehicle_id" in df.columns:

    vehicles = df["vehicle_id"].unique()

    selected_vehicle = st.sidebar.selectbox(
        "Select Vehicle",
        vehicles
    )

    df = df[
        df["vehicle_id"] == selected_vehicle
    ]

# speed limit
speed_limit = st.sidebar.slider(
    "Speed Limit",
    0,
    200,
    80
)

# ======================================================
# KPI SECTION
# ======================================================
st.subheader("📊 Fleet Statistics")

col1, col2, col3 = st.columns(3)

if "speed" in df.columns:

    col1.metric(
        "🚀 Max Speed",
        f"{df['speed'].max():.1f} km/h"
    )

    col2.metric(
        "⚡ Avg Speed",
        f"{df['speed'].mean():.1f} km/h"
    )

    col3.metric(
        "🐢 Min Speed",
        f"{df['speed'].min():.1f} km/h"
    )

# ======================================================
# ALERTS
# ======================================================
st.subheader("🚨 Alerts")

if "speed" in df.columns:

    overspeed = df[
        df["speed"] > speed_limit
    ]

    if len(overspeed) > 0:

        st.error(
            f"Overspeed Events: {len(overspeed)}"
        )

        st.dataframe(
            overspeed,
            use_container_width=True
        )

    else:

        st.success(
            "✅ All vehicles within speed limit"
        )

st.divider()

# ======================================================
# MAP
# ======================================================
# ---------------- MAP ----------------
if "latitude" in df.columns and "longitude" in df.columns:

    st.subheader("🗺️ Live Route + Current Location")

    # LIMIT DATA (IMPORTANT)
    route_df = df.tail(50)

    route_path = route_df[["longitude", "latitude"]].values.tolist()

    layers = []

    # Route line
    if len(route_path) > 1:

        layers.append(
            pdk.Layer(
                "PathLayer",
                data=[{"path": route_path}],
                get_path="path",
                get_color=[0, 200, 255],
                width_scale=8,
                width_min_pixels=2
            )
        )

    # Latest position only
    latest = df.iloc[-1]

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=[{
                "latitude": latest["latitude"],
                "longitude": latest["longitude"]
            }],
            get_position='[longitude, latitude]',
            get_color=[0, 255, 0],
            get_radius=120
        )
    )

    view_state = pdk.ViewState(
        latitude=latest["latitude"],
        longitude=latest["longitude"],
        zoom=13,
        pitch=40
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v10"
        )
    )
# ======================================================
# SPEED GRAPH
# ======================================================
if "speed" in df.columns:

    st.subheader("📈 Speed Trend")

    fig = px.line(
        df,
        x="timestamp" if "timestamp" in df.columns else df.index,
        y="speed",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================================
# RAW DATA
# ======================================================
with st.expander("📦 View Data"):

    st.dataframe(
        df,
        use_container_width=True
    )