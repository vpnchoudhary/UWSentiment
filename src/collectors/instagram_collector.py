import logging

import requests

from src.config import Config

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class InstagramCollector:
    """Collects public posts about UW Seattle from Instagram Graph API.

    NOTE: Instagram's Graph API requires a Meta Business app with Instagram
    Basic Display or Instagram Graph API access. Hashtag search requires an
    approved Instagram Business/Creator account. Without approval, this collector
    will return empty results. See: https://developers.facebook.com/docs/instagram-api
    """

    def __init__(self):
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN

    def collect(self) -> list[dict]:
        """Fetch public Instagram posts via hashtag search for UW Seattle."""
        if not self.access_token:
            logger.warning(
                "Instagram access token not configured — skipping. "
                "Set INSTAGRAM_ACCESS_TOKEN in .env (requires approved Meta app)"
            )
            return []

        posts = []
        hashtags = ["universityofwashington", "uwseattle", "uwhuskies", "udub"]

        for tag in hashtags:
            try:
                # Step 1: Get hashtag ID
                tag_response = requests.get(
                    f"{GRAPH_API_BASE}/ig_hashtag_search",
                    params={
                        "q": tag,
                        "user_id": "me",
                        "access_token": self.access_token,
                    },
                    timeout=30,
                )
                tag_response.raise_for_status()
                tag_data = tag_response.json()

                if not tag_data.get("data"):
                    continue

                hashtag_id = tag_data["data"][0]["id"]

                # Step 2: Get recent media for hashtag
                media_response = requests.get(
                    f"{GRAPH_API_BASE}/{hashtag_id}/recent_media",
                    params={
                        "user_id": "me",
                        "fields": "caption,timestamp,permalink,like_count,comments_count",
                        "access_token": self.access_token,
                        "limit": 25,
                    },
                    timeout=30,
                )
                media_response.raise_for_status()
                media_data = media_response.json()

                for item in media_data.get("data", []):
                    caption = item.get("caption", "")
                    if not caption:
                        continue
                    posts.append({
                        "source": "instagram",
                        "title": "",
                        "text": caption,
                        "score": item.get("like_count", 0),
                        "num_comments": item.get("comments_count", 0),
                        "created_utc": item.get("timestamp", ""),
                        "url": item.get("permalink", ""),
                    })

            except requests.exceptions.HTTPError as e:
                logger.warning(f"Instagram API error for #{tag}: {e}")
            except Exception as e:
                logger.error(f"Error collecting Instagram data for #{tag}: {e}")

        logger.info(f"Instagram: collected {len(posts)} posts")
        return posts
