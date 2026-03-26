import logging
from datetime import datetime, timedelta, timezone

import praw
from prawcore.exceptions import ResponseException, OAuthException

from src.config import Config

logger = logging.getLogger(__name__)


class RedditCollector:
    """Collects posts and comments about UW Seattle from Reddit."""

    def __init__(self):
        self.reddit = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            if Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
                self.reddit = praw.Reddit(
                    client_id=Config.REDDIT_CLIENT_ID,
                    client_secret=Config.REDDIT_CLIENT_SECRET,
                    user_agent=Config.REDDIT_USER_AGENT,
                )
            else:
                # Read-only mode without credentials
                self.reddit = praw.Reddit(
                    client_id="",
                    client_secret="",
                    user_agent=Config.REDDIT_USER_AGENT,
                )
                logger.warning("Reddit credentials not set — using limited access mode")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    def collect(self) -> list[dict]:
        """Fetch recent posts and comments mentioning UW Seattle."""
        if not self.reddit:
            logger.error("Reddit client not available")
            return []

        posts = []
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        # Search specific subreddits
        for subreddit_name in Config.SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                for submission in subreddit.new(limit=Config.MAX_POSTS_PER_SOURCE):
                    created = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                    if created < yesterday:
                        continue

                    if self._is_relevant(submission.title + " " + (submission.selftext or "")):
                        posts.append({
                            "source": "reddit",
                            "subreddit": subreddit_name,
                            "title": submission.title,
                            "text": submission.selftext or "",
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "created_utc": created.isoformat(),
                            "url": f"https://reddit.com{submission.permalink}",
                        })

                        # Also collect top-level comments
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments[:10]:
                            posts.append({
                                "source": "reddit",
                                "subreddit": subreddit_name,
                                "title": "",
                                "text": comment.body,
                                "score": comment.score,
                                "num_comments": 0,
                                "created_utc": datetime.fromtimestamp(
                                    comment.created_utc, tz=timezone.utc
                                ).isoformat(),
                                "url": f"https://reddit.com{comment.permalink}",
                            })

            except (ResponseException, OAuthException) as e:
                logger.warning(f"Reddit API error for r/{subreddit_name}: {e}")
            except Exception as e:
                logger.error(f"Error collecting from r/{subreddit_name}: {e}")

        # Also search across all of Reddit
        try:
            for term in Config.SEARCH_TERMS[:2]:  # Limit to avoid rate limits
                for submission in self.reddit.subreddit("all").search(
                    term, sort="new", time_filter="day", limit=25
                ):
                    if self._is_relevant(submission.title + " " + (submission.selftext or "")):
                        posts.append({
                            "source": "reddit",
                            "subreddit": submission.subreddit.display_name,
                            "title": submission.title,
                            "text": submission.selftext or "",
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "created_utc": datetime.fromtimestamp(
                                submission.created_utc, tz=timezone.utc
                            ).isoformat(),
                            "url": f"https://reddit.com{submission.permalink}",
                        })
        except Exception as e:
            logger.warning(f"Reddit global search error: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_posts = []
        for post in posts:
            if post["url"] not in seen_urls:
                seen_urls.add(post["url"])
                unique_posts.append(post)

        logger.info(f"Reddit: collected {len(unique_posts)} unique posts/comments")
        return unique_posts

    def _is_relevant(self, text: str) -> bool:
        """Check if text mentions UW Seattle."""
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in Config.SEARCH_TERMS)
