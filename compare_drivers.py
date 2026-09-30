import fastf1
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "Q")
session.load()

drivers = ["LEC", "VER"]

plt.figure(figsize=(12, 6))

for driver in drivers:
    driver_laps = session.laps.pick_driver(driver)
    fastest_lap = driver_laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry().add_distance()

    plt.plot(
        telemetry["Distance"],
        telemetry["Speed"],
        label=f"{driver} - {fastest_lap['LapTime']}"
    )

plt.title("Bahrain Qualifying: Driver Speed Comparison")
plt.xlabel("Distance around lap (m)")
plt.ylabel("Speed (km/h)")
plt.legend()
plt.grid(True)

plt.savefig("driver_speed_comparison.png", dpi=150)

plt.show()