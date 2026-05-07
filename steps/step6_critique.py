import json

from llm_client import call_groq
from utils import safe_json


def step6_critique_and_refine(state: dict) -> None:
    print("\n[STEP 6] Self-critique and final refinement...")

    prefs = state["parsed_preferences"]
    optimized = state["optimized_itinerary"]

    system = """You are a critical travel itinerary reviewer. Evaluate the itinerary and produce a refined version.
Return ONLY a valid JSON object with this exact structure:
{
  \"issues\": [list of specific problems found],
  \"suggestions\": [list of concrete improvements],
  \"final_changes\": [list of changes actually made],
  \"final_itinerary\": {
    \"Day 1\": {\"activities\": [...], \"weather_note\": \"...\"},
    \"Day 2\": {\"activities\": [...], \"weather_note\": \"...\"}
  },
  \"summary\": \"One paragraph summary of the complete trip\"
}
No markdown. No extra text. Only JSON."""

    user = f"""Review this optimized travel itinerary and refine it:

{json.dumps(optimized, indent=2)}

Original user preferences:
- Destination: {prefs.get('destination')}
- Duration: {prefs.get('duration_days')} days
- Budget: {prefs.get('budget')}
- Travel style: {prefs.get('travel_style')}
- Interests: {prefs.get('interests')}
- Constraints: {prefs.get('constraints')}

Check for: overpacked days, missing meals, repeated activity types, mismatches with user preferences.
Fix what you find and return the improved itinerary."""

    raw = call_groq(system, user)
    parsed = safe_json(raw)

    if not parsed:
        print("  [STEP 6] Parse failed, using optimized itinerary as final.")
        parsed = {
            "issues": ["Could not auto-critique — parser error"],
            "suggestions": [],
            "final_changes": [],
            "final_itinerary": optimized,
            "summary": f"Itinerary for {prefs.get('destination')} over {prefs.get('duration_days')} days.",
        }

    state["critique"] = {
        "issues": parsed.get("issues", []),
        "suggestions": parsed.get("suggestions", []),
        "final_changes": parsed.get("final_changes", []),
    }
    state["final_itinerary"] = parsed.get("final_itinerary", optimized)

    print(f"  Issues found: {len(state['critique'].get('issues', []))}")
    print(f"  Changes made: {state['critique'].get('final_changes', [])}")
    print(f"  Summary: {parsed.get('summary', '')[:120]}...")
