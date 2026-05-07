# Context-Aware Travel Itinerary Architect

A 6-step multi-step LLM agent using Groq API + real external tools.

## Chain Overview

| Step | Type | What it does |
|------|------|--------------|
| 1 | LLM | Extract structured preferences from raw user input |
| 2 | **TOOL** | Fetch real weather (OpenWeatherMap) + places (Serper) |
| 3 | LLM | Filter & rank places based on preferences + weather |
| 4 | LLM | Generate day-by-day itinerary draft |
| 5 | LLM | Optimize timing using weather data (no geography hallucination) |
| 6 | LLM | Self-critique and produce final refined itinerary |

## Setup

```bash
pip install -r requirements.txt
```

## API Keys needed

Create a local `.env` file (recommended) or export environment variables.

1) Copy the template:

```bash
cp .env.example .env
```

2) Fill in:

```bash
GROQ_API_KEY=...
OPENWEATHER_API_KEY=...
SERPER_API_KEY=...
```

Notes:
- `.env` is loaded automatically by `travel_agent.py` (no extra packages).
- Do not commit `.env` (it’s ignored by `.gitignore`).

## Run

```bash
python travel_agent.py
```

Edit the `sample_input` string at the bottom of the file to change destination/preferences.

## Output

- `output.json` — structured JSON with full itinerary, critique, weather data
- `output.md` — human-readable markdown itinerary

## Handling failures

- If the weather API fails: falls back to "weather data unavailable" strings, chain continues
- If Serper fails: falls back to generic interest-based placeholder places
- If any LLM call returns invalid JSON: safe fallback values are used, chain never crashes
- If LLM call itself fails: retries once after 2 seconds, then uses fallback

## What each step reads from state

- Step 1 reads: `raw_input` → writes: `parsed_preferences`
- Step 2 reads: `parsed_preferences` → writes: `external_data`
- Step 3 reads: `parsed_preferences` + `external_data` → writes: `ranked_places`
- Step 4 reads: `parsed_preferences` + `ranked_places` → writes: `itinerary_draft`
- Step 5 reads: `itinerary_draft` + `external_data.weather` + `parsed_preferences` → writes: `optimized_itinerary`
- Step 6 reads: `optimized_itinerary` + `parsed_preferences` → writes: `critique` + `final_itinerary`

## Design decision

Step 5 (optimization) deliberately avoids asking the LLM to compute distances or cluster locations geographically — LLMs hallucinate these. Instead it only reasons about weather and user comfort, using real tool data from Step 2.