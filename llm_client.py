import time

import requests

import config


def call_groq(system_prompt: str, user_prompt: str, retries: int = 2):
    """Call Groq OpenAI-compatible chat completions endpoint.

    Returns the raw assistant message content (string) or None on failure.
    """

    if not config.GROQ_API_KEY:
        config.warn_once(
            "GROQ_API_KEY",
            "  [LLM] GROQ_API_KEY is not set. Skipping LLM call and using fallbacks.",
        )
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```", 2)[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return clean.strip()
        except requests.HTTPError as e:
            body = ""
            try:
                body = (e.response.text or "").strip()
            except Exception:
                body = ""
            preview = body[:500].replace("\n", " ") if body else "(no response body)"
            print(
                f"  [LLM] Attempt {attempt+1} failed: HTTP {getattr(e.response, 'status_code', '?')} — {preview}"
            )
            if attempt < retries:
                time.sleep(2)
        except Exception as e:
            print(f"  [LLM] Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(2)

    return None
