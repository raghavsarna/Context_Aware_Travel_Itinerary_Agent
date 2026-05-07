import json
import os


def save_output(state: dict, output_dir: str | None = None) -> None:
    print("\n[OUTPUT] Saving structured final output...")

    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    prefs = state["parsed_preferences"]
    critique = state["critique"]
    final = state["final_itinerary"]
    weather = state.get("external_data", {}).get("weather", {})

    itinerary_readable: dict = {}
    for day, info in final.items():
        if isinstance(info, dict):
            itinerary_readable[day] = {
                "activities": info.get("activities", []),
                "weather_note": info.get("weather_note", ""),
            }
        else:
            itinerary_readable[day] = {"activities": info, "weather_note": ""}

    output = {
        "destination": prefs.get("destination"),
        "duration_days": prefs.get("duration_days"),
        "budget": prefs.get("budget"),
        "travel_style": prefs.get("travel_style"),
        "interests": prefs.get("interests"),
        "summary": f"{prefs.get('duration_days')}-day {prefs.get('travel_style')} itinerary for {prefs.get('destination')} optimized for weather and user comfort.",
        "itinerary": itinerary_readable,
        "weather_data": weather,
        "weather_adjustments": "Activities were timed to avoid extreme heat, rain, and high humidity based on real forecast data.",
        "critique_summary": {
            "issues_found": critique.get("issues", []),
            "changes_made": critique.get("final_changes", []),
        },
        "ranked_places": state["ranked_places"],
        "notes": "Avoided geographic distance optimization due to LLM hallucination risk. Used weather-based scheduling instead.",
    }

    json_path = os.path.join(output_dir, "output.json")
    md_path = os.path.join(output_dir, "output.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    md_lines = [f"# Travel Itinerary: {prefs.get('destination')}\n"]
    md_lines.append(
        f"**Duration:** {prefs.get('duration_days')} days | **Budget:** {prefs.get('budget')} | **Style:** {prefs.get('travel_style')}\n"
    )
    md_lines.append(f"**Interests:** {', '.join(prefs.get('interests', []))}\n\n---\n")

    for day, info in itinerary_readable.items():
        md_lines.append(f"## {day}")
        if info.get("weather_note"):
            md_lines.append(f"*{info['weather_note']}*\n")
        for i, act in enumerate(info.get("activities", []), 1):
            md_lines.append(f"{i}. {act}")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("*Weather data sourced from OpenWeatherMap API. Places sourced from Serper search API.*")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("  Saved: output.json and output.md")
