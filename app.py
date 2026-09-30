import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="F1 Performance Explorer",
    layout="wide"
)

st.title("F1 Performance Explorer")
st.write(
    "Real 2024 Bahrain Grand Prix qualifying analysis "
    "using FastF1 telemetry."
)

def load_driver_data(driver):
    file_path = f"data/{driver}_telemetry.csv"

    data = pd.read_csv(file_path)

    data["SessionTime"] = pd.to_timedelta(
        data["SessionTime"]
    )

    data["Distance"] = pd.to_numeric(
        data["Distance"],
        errors="coerce"
    )

    data["Speed"] = pd.to_numeric(
        data["Speed"],
        errors="coerce"
    )

    return data.dropna(
        subset=["Distance", "Speed", "SessionTime"]
    )


def convert_brake_value(value):
    text = str(value).strip().lower()

    if text == "true":
        return 100.0

    if text == "false":
        return 0.0

    try:
        return float(value)
    except ValueError:
        return 0.0


drivers = ["LEC", "VER"]

driver_1 = st.sidebar.selectbox(
    "Main driver",
    drivers,
    index=0
)

driver_2 = st.sidebar.selectbox(
    "Comparison driver",
    drivers,
    index=1
)

telemetry_1 = load_driver_data(driver_1)
telemetry_2 = load_driver_data(driver_2)

telemetry_1["BrakeValue"] = telemetry_1["Brake"].apply(
    convert_brake_value
)

telemetry_2["BrakeValue"] = telemetry_2["Brake"].apply(
    convert_brake_value
)

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

    time_1 = (
        telemetry_1["SessionTime"]
        .dt.total_seconds()
        .to_numpy()
    )

    time_2 = (
        telemetry_2["SessionTime"]
        .dt.total_seconds()
        .to_numpy()
    )

    time_1 = time_1 - time_1[0]
    time_2 = time_2 - time_2[0]

    comparison_time = np.interp(
        telemetry_1["Distance"],
        telemetry_2["Distance"],
        time_2
    )

    delta = comparison_time - time_1

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        telemetry_1["Distance"],
        delta,
        color="purple"
    )

    ax.axhline(
        0,
        color="black",
        linestyle="--"
    )

    ax.set_xlabel("Distance around lap (m)")
    ax.set_ylabel(
        f"Delta: {driver_2} - {driver_1} (seconds)"
    )

    ax.set_title("Time Difference Around the Lap")
    ax.grid(True)

    st.pyplot(fig)

    st.write(
        "Positive values mean the comparison driver "
        "is behind the main driver."
    )

with tab3:
    st.header(f"{driver_1} Braking Analysis")

    braking_data = telemetry_1.copy()

    braking_data["Braking"] = (
        braking_data["BrakeValue"] > 5
    )

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
    speed_axis.set_ylabel(
        "Speed (km/h)",
        color="blue"
    )

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
        braking_data["BrakeValue"],
        color="red",
        alpha=0.5
    )

    brake_axis.set_ylabel(
        "Brake",
        color="red"
    )

    st.pyplot(fig)

    st.subheader("Braking Point Data")

    st.dataframe(
        braking_points[
            ["Distance", "Speed", "BrakeValue"]
        ].reset_index(drop=True)
    )

with tab4:
    st.header(
        f"{driver_1} Minimum Cornering Speeds"
    )

    cornering_data = telemetry_1.copy()

    cornering_data["SmoothSpeed"] = (
        cornering_data["Speed"]
        .rolling(
            window=25,
            center=True
        )
        .mean()
    )

    corner_points = (
        cornering_data[
            ["Distance", "Speed", "SmoothSpeed"]
        ]
        .dropna()
        .nsmallest(8, "SmoothSpeed")
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
    ax.set_title(
        "Approximate Minimum Cornering Speeds"
    )

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
    "The telemetry was downloaded from FastF1 and saved "
    "as real F1 session data for reliable deployment."
)