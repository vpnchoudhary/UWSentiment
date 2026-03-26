"""UW Sentiment Agent — Daily sentiment analysis of University of Washington Seattle
from public forums (Reddit, Facebook, Instagram).

Usage:
    python main.py              Run once immediately
    python main.py --schedule   Run daily at midnight (default) or SCHEDULE_TIME from .env
    python main.py --time 08:00 Run daily at a custom time
"""

import argparse
import logging
import sys
import time

import schedule

from src.agent import UWSentimentAgent
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_agent():
    """Execute the sentiment agent."""
    try:
        agent = UWSentimentAgent()
        result = agent.run()
        logger.info(f"Daily sentiment: {result['overall_sentiment']} ({result['sentiment_score']})")
    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="UW Sentiment Agent")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run on a daily schedule (default: midnight)",
    )
    parser.add_argument(
        "--time",
        type=str,
        default=None,
        help="Schedule time in HH:MM format (default from .env or 00:00)",
    )
    args = parser.parse_args()

    if args.schedule:
        schedule_time = args.time or Config.SCHEDULE_TIME
        logger.info(f"Scheduling daily run at {schedule_time}")
        schedule.every().day.at(schedule_time).do(run_agent)

        # Run once immediately on startup
        logger.info("Running initial collection...")
        run_agent()

        logger.info(f"Agent scheduled — next run at {schedule_time}. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # Single run
        run_agent()


if __name__ == "__main__":
    main()
