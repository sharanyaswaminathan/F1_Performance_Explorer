import fastf1
import pandas as pd
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "Q")
session.load()

lap = session.laps.pick_driver("LEC").pick_fastest()
data = lap.get_telemetry().add_distance()

# Smooth the speed slightly to remove tiny random fluctuations
data["SmoothSpeed"] = data["Speed"].rolling(
    window=25,
    center=True
).mean()

# Find possible local minimum-speed points
rolling_minimum = data["SmoothSpeed"].rolling(
    window=75,
    center=True
).min()

candidates = data[
    data["SmoothSpeed"] == rolling_minimum
].dropna(subset=["SmoothSpeed", "Distance", "Speed"])

# Keep minimum-speed points separated around the lap
selected_points = []

for index, row in candidates.sort_values("SmoothSpeed").iterrows():
    if all(
        abs(row["Distance"] - point["Distance"]) > 150
        for point in selected_points
    ):
        selected_points.append(row)

    if len(selected_points) == 8:
        break

corner_points = pd.DataFrame(selected_points)

print("Approximate minimum cornering speed points:")
print(
    corner_points[["Distance", "Speed", "SmoothSpeed"]]
    .sort_values("Distance")
    .to_string(index=False)
)

# Plot the result
plt.figure(figsize=(12, 6))

plt.plot(
    data["Distance"],
    data["Speed"],
    color="blue",
    label="Speed"
)

plt.scatter(
    corner_points["Distance"],
    corner_points["Speed"],
    color="red",
    s=50,
    label="Approximate cornering minimum"
)

plt.title("Leclerc Bahrain Qualifying Lap: Minimum Cornering Speeds")
plt.xlabel("Distance around lap (m)")
plt.ylabel("Speed (km/h)")
plt.grid(True)
plt.legend()

plt.savefig("minimum_cornering_speed.png", dpi=150)

plt.show()