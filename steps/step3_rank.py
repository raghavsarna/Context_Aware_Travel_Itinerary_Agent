import json

from llm_client import call_groq
from utils import safe_json


def step3_filter_and_rank(state: dict) -> None:
    print("\n[STEP 3] Filtering and ranking places using LLM reasoning...")

    prefs = state["parsed_preferences"]
    external = state["external_data"]

    system = """You are a travel advisor. Given user preferences and a raw list of places, categorize them.
Return ONLY a valid JSON object with this structure:
{
  \"must_visit\": [list of place names with one-line reason each as \"name: reason\"],
  \"optional\": [list of place names],
  \"avoid\": [list of place names with reason],
  \"reasoning_summary\": \"2-3 sentence explanation of your filtering logic\"
}
No markdown. No extra text. Only JSON."""

    user = f"""User preferences:
{json.dumps(prefs, indent=2)}

Available places from real-world search:
{json.dumps(external['places'], indent=2)}

Weather context:
{json.dumps(external['weather'], indent=2)}

Rank and filter these places based on the user's interests, budget, travel style, and constraints."""

    raw = call_groq(system, user)
    parsed = safe_json(raw)

    if not parsed:
        print("  [STEP 3] Parse failed, using fallback ranking.")
        names = [p.get("name") for p in external.get("places", []) if isinstance(p, dict) and p.get("name")]
        parsed = {
            "must_visit": names[:3],
            "optional": names[3:6],
            "avoid": [],
            "reasoning_summary": "Default ranking applied due to parsing error.",
        }

    state["ranked_places"] = parsed
    print(
        f"  Must visit: {len(parsed.get('must_visit', []))} places | Optional: {len(parsed.get('optional', []))} | Avoid: {len(parsed.get('avoid', []))}"
    )
    print(f"  Reasoning: {parsed.get('reasoning_summary', '')[:100]}...")
