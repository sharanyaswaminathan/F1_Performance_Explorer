import os
import fastf1
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

st.set_page_config(
    page_title="F1 Performance Explorer",
    layout="wide"
)

st.title("F1 Performance Explorer")
st.write("Real F1 qualifying-session analysis using FastF1 telemetry.")

year = st.sidebar.selectbox("Year", [2024])
event = st.sidebar.selectbox("Event", ["Bahrain"])
session_type = st.sidebar.selectbox(
    "Session",
    ["Qualifying"]
)

session_code = "Q"

with st.spinner("Loading real F1 session data..."):
    session = fastf1.get_session(year, event, session_code)
    session.load()

drivers = sorted(session.laps["Driver"].dropna().unique())

driver_1 = st.sidebar.selectbox("Main driver", drivers)
driver_2 = st.sidebar.selectbox(
    "Comparison driver",
    [driver for driver in drivers if driver != driver_1]
)

lap_1 = session.laps[
    session.laps["Driver"] == driver_1
].pick_fastest()

lap_2 = session.laps[
    session.laps["Driver"] == driver_2
].pick_fastest()

telemetry_1 = lap_1.get_telemetry().add_distance()
telemetry_2 = lap_2.get_telemetry().add_distance()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Speed Comparison",
        "Delta Time",
        "Braking",
        "Cornering Speed"
    ]
)

with tab1:
    st.header("Speed Comparison")

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        telemetry_1["Distance"],
        telemetry_1["Speed"],
        label=driver_1
    )

    ax.plot(
        telemetry_2["Distance"],
        telemetry_2["Speed"],
        label=driver_2
    )

    ax.set_xlabel("Distance around lap (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title(f"{driver_1} vs {driver_2} Speed")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

with tab2:
    st.header("Delta Time")

    time_1 = telemetry_1["SessionTime"].dt.total_seconds()
    time_2 = telemetry_2["SessionTime"].dt.total_seconds()

    time_1 = time_1 - time_1.iloc[0]
    time_2 = time_2 - time_2.iloc[0]

    time_2_at_distance_1 = np.interp(
        telemetry_1["Distance"],
        telemetry_2["Distance"],
        time_2
    )

    delta = time_2_at_distance_1 - time_1

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        telemetry_1["Distance"],
        delta,
        color="purple"
    )

    ax.axhline(0, color="black", linestyle="--")
    ax.set_xlabel("Distance around lap (m)")
    ax.set_ylabel(f"Delta: {driver_2} - {driver_1} (seconds)")
    ax.set_title("Time Difference Around the Lap")
    ax.grid(True)

    st.pyplot(fig)

    st.write(
        "Positive values mean the comparison driver is behind "
        "the main driver at that point."
    )

with tab3:
    st.header(f"{driver_1} Braking Analysis")

    braking_data = telemetry_1.copy()
    braking_data["Braking"] = braking_data["Brake"] > 5

    braking_data["StartBraking"] = (
        braking_data["Braking"]
        & ~braking_data["Braking"].shift(
            1,
            fill_value=False
        )
    )

    braking_points = braking_data[
        braking_data["StartBraking"]
    ]

    fig, speed_axis = plt.subplots(figsize=(12, 5))

    speed_axis.plot(
        braking_data["Distance"],
        braking_data["Speed"],
        color="blue"
    )

    speed_axis.set_xlabel("Distance around lap (m)")
    speed_axis.set_ylabel("Speed (km/h)", color="blue")
    speed_axis.grid(True)

    for distance in braking_points["Distance"]:
        speed_axis.axvline(
            distance,
            color="red",
            linestyle="--",
            alpha=0.7
        )

    brake_axis = speed_axis.twinx()

    brake_axis.plot(
        braking_data["Distance"],
        braking_data["Brake"],
        color="red",
        alpha=0.5
    )

    brake_axis.set_ylabel("Brake", color="red")

    st.pyplot(fig)

    st.subheader("Braking Point Data")
    st.dataframe(
        braking_points[["Distance", "Speed", "Brake"]]
        .reset_index(drop=True)
    )

with tab4:
    st.header(f"{driver_1} Minimum Cornering Speeds")

    cornering_data = telemetry_1.copy()

    cornering_data["SmoothSpeed"] = (
        cornering_data["Speed"]
        .rolling(window=25, center=True)
        .mean()
    )

    possible_points = cornering_data[
        ["Distance", "Speed", "SmoothSpeed"]
    ].dropna()

    corner_points = possible_points.nsmallest(
        8,
        "SmoothSpeed"
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        cornering_data["Distance"],
        cornering_data["Speed"],
        color="blue"
    )

    ax.scatter(
        corner_points["Distance"],
        corner_points["Speed"],
        color="red",
        label="Minimum-speed points"
    )

    ax.set_xlabel("Distance around lap (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Approximate Minimum Cornering Speeds")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

    st.subheader("Minimum-Speed Data")
    st.dataframe(
        corner_points[
            ["Distance", "Speed", "SmoothSpeed"]
        ].reset_index(drop=True)
    )

st.divider()
st.caption(
    "Data source: FastF1 telemetry from a completed F1 session. "
    "This dashboard is not a real-time live timing system."
)