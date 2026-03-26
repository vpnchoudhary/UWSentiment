import json
import logging
import os
from datetime import datetime, timezone

from src.config import Config

logger = logging.getLogger(__name__)


def load_results() -> list[dict]:
    """Load existing sentiment results from JSON file."""
    if not os.path.exists(Config.DATA_FILE):
        return []

    try:
        with open(Config.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading {Config.DATA_FILE}: {e}")
        return []


def save_results(results: list[dict]):
    """Save sentiment results to JSON file."""
    os.makedirs(os.path.dirname(Config.DATA_FILE), exist_ok=True)

    try:
        with open(Config.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {Config.DATA_FILE}")
    except IOError as e:
        logger.error(f"Error writing {Config.DATA_FILE}: {e}")


def append_daily_result(daily_result: dict):
    """Append a daily result to the JSON file, replacing any existing entry for the same date."""
    results = load_results()

    # Remove existing entry for the same date (in case of re-runs)
    today = daily_result.get("date", "")
    results = [r for r in results if r.get("date") != today]

    results.append(daily_result)
    save_results(results)
    logger.info(f"Appended results for {today} — total entries: {len(results)}")
