from llm_client import call_groq
from utils import safe_json


def step1_extract_preferences(state: dict) -> None:
    print("\n[STEP 1] Extracting user preferences from raw input...")

    system = """You are a travel intent parser. Extract structured travel preferences from user input.
Return ONLY a valid JSON object with these exact keys:
{
  \"destination\": string,
  \"duration_days\": integer,
  \"budget\": \"low\" | \"medium\" | \"high\",
  \"interests\": [list of strings],
  \"constraints\": [list of strings],
  \"travel_style\": string,
  \"start_date\": string or null
}
No explanation. No markdown. Only the JSON object."""

    user = f"Extract travel preferences from this input:\n\n{state['raw_input']}"

    raw = call_groq(system, user)
    parsed = safe_json(raw)

    if not parsed:
        print("  [STEP 1] JSON parse failed, using fallback defaults.")
        parsed = {
            "destination": "unknown",
            "duration_days": 3,
            "budget": "medium",
            "interests": ["sightseeing"],
            "constraints": [],
            "travel_style": "balanced",
            "start_date": None,
        }

    state["parsed_preferences"] = parsed
    print(
        f"  Destination: {parsed.get('destination')} | Days: {parsed.get('duration_days')} | Budget: {parsed.get('budget')}"
    )
    print(f"  Interests: {parsed.get('interests')}")
