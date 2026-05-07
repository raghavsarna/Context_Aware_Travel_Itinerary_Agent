import json

from llm_client import call_groq
from utils import safe_json


def step5_weather_optimize(state: dict) -> None:
    print("\n[STEP 5] Optimizing itinerary based on weather (avoiding hallucination on geography)...")

    prefs = state["parsed_preferences"]
    draft = state["itinerary_draft"]
    weather = state.get("external_data", {}).get("weather", {})

    system = """You are a weather-aware travel optimizer. Your ONLY job is to adjust activity timing based on weather.
Rules you MUST follow:
1. Do NOT rearrange activities based on geography or distances — you don't know these.
2. ONLY shift or swap activities based on weather conditions (heat, rain, humidity, wind).
3. Prefer outdoor activities during mild/pleasant weather.
4. Move outdoor activities indoors or reschedule if weather is harsh.
5. Add brief weather notes to each day.
Return ONLY a valid JSON object with keys \"Day 1\", \"Day 2\", etc.
Each day value is an object: {\"activities\": [list of strings], \"weather_note\": string}
No markdown. No extra text. Only JSON."""

    user = f"""Original itinerary draft:
{json.dumps(draft, indent=2)}

Real weather data for each day:
{json.dumps(weather, indent=2)}

User preferences:
- Travel style: {prefs.get('travel_style')}
- Constraints: {prefs.get('constraints')}

Optimize the itinerary timing based ONLY on weather conditions."""

    raw = call_groq(system, user)
    parsed = safe_json(raw)

    if not parsed:
        print("  [STEP 5] Parse failed, carrying draft forward with weather notes.")
        parsed = {}
        for day, acts in draft.items():
            w = weather.get(day)
            if not w and isinstance(weather, dict):
                for k, v in weather.items():
                    if isinstance(k, str) and k.startswith(day):
                        w = v
                        break
            parsed[day] = {"activities": acts, "weather_note": f"Weather: {w or 'unknown'}"}

    state["optimized_itinerary"] = parsed
    for day, info in parsed.items():
        if isinstance(info, dict):
            note = info.get("weather_note", "")
            print(f"  {day}: {note[:80]}")
