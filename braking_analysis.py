import fastf1
import pandas as pd
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "Q")
session.load()

lap = session.laps.pick_driver("LEC").pick_fastest()
data = lap.get_telemetry().add_distance()

# Brake is considered active when its value is greater than 5
data["Braking"] = data["Brake"] > 5

# Find where braking changes from False to True
data["StartBraking"] = (
    data["Braking"] &
    ~data["Braking"].shift(1, fill_value=False)
)

braking_points = data[data["StartBraking"]]

print("Braking points:")
print(braking_points[["Distance", "Speed", "Brake"]].to_string(index=False))

# Create the graph
fig, speed_axis = plt.subplots(figsize=(12, 6))

speed_axis.plot(
    data["Distance"],
    data["Speed"],
    color="blue",
    label="Speed"
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
    data["Distance"],
    data["Brake"],
    color="red",
    alpha=0.5,
    label="Brake"
)

brake_axis.set_ylabel("Brake", color="red")

plt.title("Leclerc Bahrain Qualifying Lap: Braking Points")
plt.tight_layout()

plt.savefig("braking_analysis.png", dpi=150)

plt.show()