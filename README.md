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

## Assignment Requirements (Checklist)

This project is built to match the “Multi-Step LLM Agent” assignment requirements:

- **Multi-step chaining (≥4 sequential LLM calls)**
  - This agent uses **5 sequential Groq LLM calls**: Steps **1, 3, 4, 5, 6**.
  - Each step consumes structured outputs from prior steps through a shared `state` object.
- **At least one tool call (non-LLM)**
  - Step **2** calls external APIs (OpenWeatherMap + Serper) to fetch real data.
- **Shared state across the chain**
  - A single `state` dictionary is created and passed through every step.
- **Structured final output**
  - Writes **`output.json`** and **`output.md`** (a user-actionable itinerary).
- **Modular code (not monolithic)**
  - Each step is a separate module under `steps/`.
- **No agent frameworks**
  - No LangChain / LlamaIndex / agent frameworks are used; chaining is implemented directly in Python.

Note: the assignment handout mentions “Grok API”; this repo uses the **Groq** OpenAI-compatible chat completions endpoint.

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

## How chaining works (data flow)

All intermediate artifacts are accumulated in a shared `state` dict.

- **Step 1 → `parsed_preferences`**
  - Extracts destination, duration, budget, interests, constraints, style, start date.
- **Step 2 → `external_data`**
  - Adds `{destination, weather, places}` from real APIs.
- **Step 3 → `ranked_places`**
  - Filters/labels “must_visit / optional / avoid” using `parsed_preferences + external_data`.
- **Step 4 → `itinerary_draft`**
  - Drafts a day-by-day plan conditioned on `ranked_places`.
- **Step 5 → `optimized_itinerary`**
  - Weather-aware timing changes using `external_data.weather`.
- **Step 6 → `critique` + `final_itinerary`**
  - Reviews and refines to produce the final structured itinerary.

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

## Prompt transparency (for the Prompt Design deliverable)

Each LLM step contains its full **system prompt** and **user prompt** directly in code.

- Step 1 prompts: `steps/step1_extract.py`
- Step 3 prompts: `steps/step3_rank.py`
- Step 4 prompts: `steps/step4_itinerary.py`
- Step 5 prompts: `steps/step5_optimize.py`
- Step 6 prompts: `steps/step6_critique.py`

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

## Limitations (honest failure modes)

- If LLM output is not valid JSON, the code falls back to defaults to keep the chain running.
- Geography/travel-time optimization is intentionally avoided (LLMs can hallucinate distances).
- Tool APIs can be rate-limited or return sparse results; the chain continues with fallbacks.

## Design Decision (No Geography Hallucinations)

Step 5 (optimization) deliberately avoids asking the LLM to compute distances or cluster locations geographically.
LLMs often hallucinate geographic facts, so the optimizer only reorders timing based on **real weather tool data**.