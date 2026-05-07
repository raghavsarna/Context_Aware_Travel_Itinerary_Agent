import os


_warned_missing_keys: set[str] = set()


def load_dotenv(dotenv_path: str) -> None:
    """Minimal .env loader (no external dependency).

    Supports lines like KEY=VALUE, ignores blanks and comments (# ...).
    Does not override already-set environment variables.
    """

    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        return


def warn_once(key: str, message: str) -> None:
    if key in _warned_missing_keys:
        return
    _warned_missing_keys.add(key)
    print(message)


def init_env() -> None:
    """Load .env next to this file (if present)."""

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# Load env immediately on import.
init_env()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
