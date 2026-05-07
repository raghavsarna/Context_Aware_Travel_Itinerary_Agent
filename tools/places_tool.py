import requests

import config


def fetch_places(destination: str, interests: list[str]) -> list[dict]:
    """Fetch places via Serper.dev Google Search API.

    Returns list of {name, snippet, link}. Falls back to generic placeholders on failure.
    """

    if not config.SERPER_API_KEY:
        config.warn_once(
            "SERPER_API_KEY",
            "  [TOOL] SERPER_API_KEY is not set. Using places fallbacks.",
        )
        return [
            {
                "name": f"Popular {interest} spot in {destination}",
                "snippet": "Highly recommended",
                "link": "",
            }
            for interest in interests
        ]

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": config.SERPER_API_KEY, "Content-Type": "application/json"}
    query = f"top places to visit in {destination} for {', '.join(interests[:3])}"
    payload = {"q": query, "num": 10}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        places = []
        for item in results.get("organic", [])[:8]:
            places.append(
                {
                    "name": item.get("title", "Unknown Place"),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                }
            )
        return places

    except Exception as e:
        print(f"  [TOOL] Places/Serper API failed: {e}")
        return [
            {
                "name": f"Popular {interest} spot in {destination}",
                "snippet": "Highly recommended",
                "link": "",
            }
            for interest in interests
        ]
