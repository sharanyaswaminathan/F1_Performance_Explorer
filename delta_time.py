import fastf1
import numpy as np
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "Q")
session.load()

lec_lap = session.laps.pick_driver("LEC").pick_fastest()
ver_lap = session.laps.pick_driver("VER").pick_fastest()

lec_data = lec_lap.get_telemetry().add_distance()
ver_data = ver_lap.get_telemetry().add_distance()

lec_distance = lec_data["Distance"].to_numpy()
ver_distance = ver_data["Distance"].to_numpy()

lec_time = lec_data["SessionTime"].dt.total_seconds().to_numpy()
ver_time = ver_data["SessionTime"].dt.total_seconds().to_numpy()

# Start both laps at zero seconds
lec_time = lec_time - lec_time[0]
ver_time = ver_time - ver_time[0]

# Compare Verstappen's time with Leclerc's time
ver_time_at_lec_distance = np.interp(
    lec_distance,
    ver_distance,
    ver_time
)

delta = ver_time_at_lec_distance - lec_time

plt.figure(figsize=(12, 6))
plt.plot(lec_distance, delta, color="purple")

plt.axhline(0, color="black", linestyle="--")
plt.title("Bahrain Qualifying Delta Time: VER compared with LEC")
plt.xlabel("Distance around lap (m)")
plt.ylabel("Time difference (seconds)")
plt.grid(True)

plt.savefig("delta_time_comparison.png", dpi=150)

plt.show()