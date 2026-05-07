from llm_client import call_groq
from utils import safe_json


def step4_generate_itinerary(state: dict) -> None:
    print("\n[STEP 4] Generating structured itinerary draft...")

    prefs = state["parsed_preferences"]
    ranked = state["ranked_places"]
    days = prefs.get("duration_days", 3)

    system = """You are a travel planner. Create a detailed day-by-day itinerary.
Return ONLY a valid JSON object where keys are \"Day 1\", \"Day 2\", etc., each containing a list of activity strings.
Include arrival/departure logistics, meals, and transitions. Each day should have 4-6 activities.
No markdown. No extra text. Only JSON.
Example format:
{
  \"Day 1\": [\"Arrive at airport\", \"Check in hotel\", \"Lunch at local restaurant\", \"Visit beach\", \"Dinner\"],
  \"Day 2\": [\"Morning temple visit\", \"Lunch\", \"Afternoon market\", \"Evening show\"]
}"""

    user = f"""Create a {days}-day itinerary for {prefs.get('destination')}.

User preferences:
- Budget: {prefs.get('budget')}
- Travel style: {prefs.get('travel_style')}
- Interests: {', '.join(prefs.get('interests', []))}
- Constraints: {', '.join(prefs.get('constraints', []))}

Must-visit places: {ranked.get('must_visit', [])}
Optional places: {ranked.get('optional', [])}
Avoid: {ranked.get('avoid', [])}

Build a logical day-by-day plan."""

    raw = call_groq(system, user)
    parsed = safe_json(raw)

    if not parsed:
        print("  [STEP 4] Parse failed, building minimal fallback itinerary.")
        parsed = {f"Day {i+1}": ["Explore the city", "Local lunch", "Evening rest"] for i in range(days)}

    state["itinerary_draft"] = parsed
    for day, acts in parsed.items():
        if not isinstance(acts, list):
            continue
        print(f"  {day}: {' → '.join(acts[:3])}{'...' if len(acts) > 3 else ''}")
