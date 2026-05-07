from tools.places_tool import fetch_places
from tools.weather_tool import fetch_weather


def step2_fetch_external_data(state: dict) -> None:
    print("\n[STEP 2] Fetching external data (TOOL CALL — NOT LLM) ...")
    print("  This step uses real external APIs, not LLM knowledge.")

    prefs = state["parsed_preferences"]
    destination = prefs.get("destination", "Paris")
    days = prefs.get("duration_days", 3)
    interests = prefs.get("interests", ["sightseeing"])

    weather = fetch_weather(destination, days)
    places = fetch_places(destination, interests)

    state["external_data"] = {
        "places": places,
        "weather": weather,
        "destination": destination,
    }

    print(f"  Fetched {len(places)} places and {len(weather)} days of weather data.")
    print(f"  Weather snapshot: {list(weather.items())[0] if weather else 'N/A'}")
