import logging

import requests

from src.config import Config

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookCollector:
    """Collects public posts about UW Seattle from Facebook Graph API.

    NOTE: Facebook's Graph API requires an approved app with Page Public Content
    Access permission to search public posts. Without approval, this collector
    will return empty results. See: https://developers.facebook.com/docs/graph-api
    """

    def __init__(self):
        self.access_token = Config.FACEBOOK_ACCESS_TOKEN

    def collect(self) -> list[dict]:
        """Fetch public Facebook posts mentioning UW Seattle."""
        if not self.access_token:
            logger.warning(
                "Facebook access token not configured — skipping. "
                "Set FACEBOOK_ACCESS_TOKEN in .env (requires approved Meta app)"
            )
            return []

        posts = []
        for term in Config.SEARCH_TERMS[:2]:
            try:
                response = requests.get(
                    f"{GRAPH_API_BASE}/search",
                    params={
                        "q": term,
                        "type": "post",
                        "access_token": self.access_token,
                        "fields": "message,created_time,permalink_url,reactions.summary(true)",
                        "limit": 50,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for item in data.get("data", []):
                    message = item.get("message", "")
                    if not message:
                        continue
                    posts.append({
                        "source": "facebook",
                        "title": "",
                        "text": message,
                        "score": item.get("reactions", {}).get("summary", {}).get("total_count", 0),
                        "num_comments": 0,
                        "created_utc": item.get("created_time", ""),
                        "url": item.get("permalink_url", ""),
                    })

            except requests.exceptions.HTTPError as e:
                logger.warning(f"Facebook API error for '{term}': {e}")
            except Exception as e:
                logger.error(f"Error collecting Facebook data for '{term}': {e}")

        logger.info(f"Facebook: collected {len(posts)} posts")
        return posts
