import os
import fastf1

os.makedirs("data", exist_ok=True)

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "Q")
session.load()

for driver in ["LEC", "VER"]:
    driver_laps = session.laps[
        session.laps["Driver"] == driver
    ]

    fastest_lap = driver_laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry().add_distance()

    telemetry.to_csv(
        f"data/{driver}_telemetry.csv",
        index=False
    )

session.laps.to_csv(
    "data/session_laps.csv",
    index=False
)

print("Real F1 dashboard data prepared successfully.")