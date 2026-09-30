import pandas as pd
import matplotlib.pyplot as plt

# Read the real F1 telemetry
data = pd.read_csv("fastest_lap_telemetry.csv")

# Convert FastF1 time into seconds
data["Time"] = pd.to_timedelta(data["Time"])
time_seconds = data["Time"].dt.total_seconds()

# Create three graphs
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(time_seconds, data["Speed"])
plt.title("Charles Leclerc - Bahrain Qualifying Lap")
plt.ylabel("Speed (km/h)")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(time_seconds, data["Throttle"])
plt.ylabel("Throttle (%)")
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(time_seconds, data["Brake"])
plt.xlabel("Time (seconds)")
plt.ylabel("Brake")
plt.grid(True)

plt.tight_layout()

# Save the graph for the published project
plt.savefig("speed_throttle_brake.png", dpi=150)

plt.show()