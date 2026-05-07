import requests

import config


def fetch_weather(city: str, days: int) -> dict:
    """Fetch and summarize forecast by day (OpenWeatherMap free tier).

    Returns a dict like {"Day 1 (YYYY-MM-DD)": "desc, avg 30°C", ...}
    or fallback values if the API call fails.
    """

    if not config.OPENWEATHER_API_KEY:
        config.warn_once(
            "OPENWEATHER_API_KEY",
            "  [TOOL] OPENWEATHER_API_KEY is not set. Using weather fallbacks.",
        )
        return {f"Day {i+1}": "weather data unavailable" for i in range(days)}

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": min(days * 8, 40),
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        day_summaries: dict[str, dict] = {}
        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]
            desc = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            if date not in day_summaries:
                day_summaries[date] = {"descriptions": [], "temps": []}
            day_summaries[date]["descriptions"].append(desc)
            day_summaries[date]["temps"].append(temp)

        weather: dict[str, str] = {}
        for i, (date, info) in enumerate(list(day_summaries.items())[:days]):
            avg_temp = round(sum(info["temps"]) / len(info["temps"]), 1)
            common_desc = max(set(info["descriptions"]), key=info["descriptions"].count)
            weather[f"Day {i+1} ({date})"] = f"{common_desc}, avg {avg_temp}°C"

        return weather

    except Exception as e:
        print(f"  [TOOL] Weather API failed: {e}")
        return {f"Day {i+1}": "weather data unavailable" for i in range(days)}
