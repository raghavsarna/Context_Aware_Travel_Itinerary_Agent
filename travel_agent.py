"""Context-Aware Travel Itinerary Architect (modular version).

Pipeline
--------
1) LLM extracts preferences
2) TOOL calls fetch real weather + places
3) LLM ranks places
4) LLM drafts itinerary
5) LLM optimizes timing using weather (no geography/distance assumptions)
6) LLM critiques and refines

Environment configuration
-------------------------
Secrets MUST NOT be hardcoded. Configure API keys via environment variables or a local
`.env` file (loaded automatically).

Required (depending on which steps you want to work):
- GROQ_API_KEY: Groq API key for LLM steps (1,3,4,5,6)
- OPENWEATHER_API_KEY: OpenWeatherMap API key for weather tool call (step 2)
- SERPER_API_KEY: Serper.dev API key for places tool call (step 2)

Optional:
- GROQ_MODEL: Groq model name (default: llama-3.3-70b-versatile)

State structure
---------------
The agent writes intermediate artifacts into a single `state` dict:
- raw_input: original user text
- parsed_preferences: structured preferences extracted from raw_input
- external_data: { destination, weather, places }
- ranked_places: LLM filtered + ranked lists
- itinerary_draft: initial day-by-day plan
- optimized_itinerary: weather-aware version
- critique: issues/suggestions/final_changes
- final_itinerary: final day-by-day plan

Outputs
-------
Writes `output.json` (structured) and `output.md` (human-readable) into this folder.
"""

from state import initial_state
from output_writer import save_output

from steps.step1_extract import step1_extract_preferences
from steps.step2_fetch import step2_fetch_external_data
from steps.step3_rank import step3_filter_and_rank
from steps.step4_itinerary import step4_generate_itinerary
from steps.step5_optimize import step5_weather_optimize
from steps.step6_critique import step6_critique_and_refine


def run_agent(user_input: str) -> dict:
    print("=" * 60)
    print("   TRAVEL ITINERARY AGENT — MULTI-STEP LLM PIPELINE")
    print("=" * 60)

    state = initial_state()
    state["raw_input"] = user_input
    print(f"\nUser input: {user_input[:120]}{'...' if len(user_input) > 120 else ''}")

    step1_extract_preferences(state)
    step2_fetch_external_data(state)  # TOOL CALL — real external API
    step3_filter_and_rank(state)
    step4_generate_itinerary(state)
    step5_weather_optimize(state)
    step6_critique_and_refine(state)
    save_output(state)

    print("\n" + "=" * 60)
    print("   AGENT COMPLETE — State Summary")
    print("=" * 60)
    print("  raw_input         → SET")
    print(f"  parsed_preferences→ {list(state['parsed_preferences'].keys())}")
    print(
        "  external_data     → "
        f"places: {len(state['external_data'].get('places', []))}, "
        f"weather days: {len(state['external_data'].get('weather', {}))}"
    )
    print(
        "  ranked_places     → "
        f"must: {len(state['ranked_places'].get('must_visit', []))}, "
        f"optional: {len(state['ranked_places'].get('optional', []))}"
    )
    print(f"  itinerary_draft   → {len(state['itinerary_draft'])} days")
    print(f"  optimized_itinery → {len(state['optimized_itinerary'])} days")
    print(f"  critique          → {len(state['critique'].get('issues', []))} issues")
    print(f"  final_itinerary   → {len(state['final_itinerary'])} days")
    print("\n  Output files: output.json, output.md")
    print("=" * 60)

    return state


if __name__ == "__main__":
    sample_input = (
        "I want to visit Goa for 3 days next month. I'm on a medium budget and love beaches, "
        "nightlife, and local food. I prefer relaxed mornings and don't want to travel too much "
        "between locations. Evenings outdoors are a must."
    )

    final_state = run_agent(sample_input)
