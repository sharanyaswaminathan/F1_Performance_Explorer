import fastf1

# Save downloaded data inside the cache folder
fastf1.Cache.enable_cache("cache")

# Choose a real F1 qualifying session
session = fastf1.get_session(2024, "Bahrain", "Q")

print("Loading the F1 session...")
session.load()

# Save all lap information
session.laps.to_csv("session_laps.csv", index=False)

# Select the fastest lap in the session
fastest_lap = session.laps.pick_fastest()

# Get telemetry for that lap
telemetry = fastest_lap.get_telemetry()

# Save the telemetry
telemetry.to_csv("fastest_lap_telemetry.csv", index=False)

print("F1 data downloaded successfully!")
print("Driver:", fastest_lap["Driver"])
print("Lap time:", fastest_lap["LapTime"])
print("Telemetry rows:", len(telemetry))