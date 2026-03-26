import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Reddit API
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "UWSentimentAgent/1.0")

    # Facebook Graph API
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")

    # Instagram Graph API
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

    # Schedule
    SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "00:00")

    # Storage
    DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sentiment_results.json")

    # Search terms for University of Washington Seattle
    SEARCH_TERMS = [
        "University of Washington",
        "UW Seattle",
        "UDub",
        "U-Dub",
        "UW Huskies",
    ]

    # Subreddits to scan
    SUBREDDITS = [
        "udub",
        "seattle",
        "washington",
        "college",
        "ApplyingToCollege",
        "collegeresults",
    ]

    # Max posts to fetch per source per run
    MAX_POSTS_PER_SOURCE = 100
