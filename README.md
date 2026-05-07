# Context-Aware Travel Itinerary Architect

A modular 6-step LLM agent that generates a weather-aware travel itinerary.

- **LLM**: Groq (OpenAI-compatible endpoint)
- **Tools (real APIs)**: OpenWeatherMap (forecast) + Serper.dev (places search)
- **Outputs**: `output.json` (structured) and `output.md` (human-readable)

## Quickstart

**Prereqs**: Python 3.10+ recommended.

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Configure keys (recommended: `.env`):

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```bash
GROQ_API_KEY=...
OPENWEATHER_API_KEY=...
SERPER_API_KEY=...
```

3) Run:

```bash
python travel_agent.py
```

When prompted, paste your trip request (multi-line supported; press **Enter on an empty line** to finish).

## What input should look like?

The agent works best if you describe:

- Destination (city/country)
- Duration (number of days)
- Budget (`low` / `medium` / `high`)
- Interests (beaches, museums, food, hiking, nightlife, etc.)
- Constraints (avoid early mornings, wheelchair-friendly, avoid long travel, etc.)
- Travel style (relaxed, packed, luxury, backpacking, family-friendly)
- Dates (optional)

Example:

> I want to visit Goa for 3 days next month. I'm on a medium budget and love beaches, nightlife, and local food. I prefer relaxed mornings and don't want to travel too much between locations. Evenings outdoors are a must.

## Chain Overview

| Step | Type | What it does |
|------|------|--------------|
| 1 | LLM | Extract structured preferences from raw user input |
| 2 | TOOL | Fetch real weather (OpenWeatherMap) + places (Serper) |
| 3 | LLM | Filter & rank places based on preferences + weather |
| 4 | LLM | Generate day-by-day itinerary draft |
| 5 | LLM | Optimize timing using weather data (no geography hallucination) |
| 6 | LLM | Self-critique and produce final refined itinerary |

## Project Structure

```text
.
├─ travel_agent.py          # main entrypoint/orchestrator (interactive prompt)
├─ config.py                # loads .env + provides env-backed configuration
├─ llm_client.py            # Groq chat completion helper
├─ output_writer.py         # writes output.json + output.md
├─ state.py                 # initial_state()
├─ utils.py                 # safe_json()
├─ steps/                   # pipeline steps (step1..step6)
│  ├─ step1_extract.py
│  ├─ step2_fetch.py
│  ├─ step3_rank.py
│  ├─ step4_itinerary.py
│  ├─ step5_optimize.py
│  └─ step6_critique.py
└─ tools/                   # external tool calls
	├─ weather_tool.py
	└─ places_tool.py
```

## Configuration

This repo intentionally avoids hardcoding secrets.

### Environment variables

- `GROQ_API_KEY` (required for steps 1/3/4/5/6)
- `OPENWEATHER_API_KEY` (required for step 2 weather)
- `SERPER_API_KEY` (required for step 2 places)
- `GROQ_MODEL` (optional, default `llama-3.3-70b-versatile`)

### `.env` loading

`.env` is loaded automatically by `config.py` on import (no extra package needed).

Security note:
- Do not commit `.env`.
- Rotate keys if you ever exposed them in code/history.

## Outputs

Running the agent generates:

- `output.json`: structured data for programmatic use
- `output.md`: readable itinerary (no internal/agent notes)

### `output.json` shape (high level)

```json
{
  "destination": "...",
  "duration_days": 3,
  "budget": "medium",
  "travel_style": "...",
  "interests": ["..."],
  "summary": "...",
  "itinerary": {
	 "Day 1": {"activities": ["..."], "weather_note": "..."}
  },
  "weather_data": {"Day 1 (YYYY-MM-DD)": "..."},
  "ranked_places": {"must_visit": [], "optional": [], "avoid": []}
}
```

## Failure Handling & Troubleshooting

The pipeline is designed to **never crash** if an API call fails.

- Missing `GROQ_API_KEY`: LLM steps are skipped and fallbacks are used.
- Missing `OPENWEATHER_API_KEY`: weather falls back to “weather data unavailable”.
- Missing `SERPER_API_KEY`: places fall back to generic placeholders.
- Invalid/blocked Groq key/org: Groq may return errors like `organization_restricted`.

Common fixes:

1) **Groq returns `organization_restricted`**
	- This is an account/org restriction on Groq’s side.
	- Use a different Groq org/key, or contact Groq support to unblock.

2) **OpenWeather returns 404**
	- Usually means the destination string wasn’t recognized (e.g., “unknown”).
	- Fix the input prompt (clear city name) and ensure step 1 LLM is working.

3) **Serper returns 401/403**
	- Check your `SERPER_API_KEY` and plan limits.

## Design Decision (No Geography Hallucinations)

Step 5 (optimization) deliberately avoids asking the LLM to compute distances or cluster locations geographically.
LLMs often hallucinate geographic facts, so the optimizer only reorders timing based on **real weather tool data**.