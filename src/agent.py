import logging
from datetime import datetime, timezone

from src.collectors.reddit_collector import RedditCollector
from src.collectors.facebook_collector import FacebookCollector
from src.collectors.instagram_collector import InstagramCollector
from src.analyzer import SentimentAnalyzer
from src.storage import append_daily_result

logger = logging.getLogger(__name__)


class UWSentimentAgent:
    """Autonomous agent that collects and analyzes sentiment about UW Seattle."""

    def __init__(self):
        self.collectors = {
            "reddit": RedditCollector(),
            "facebook": FacebookCollector(),
            "instagram": InstagramCollector(),
        }
        self.analyzer = SentimentAnalyzer()

    def run(self):
        """Execute a single collection and analysis cycle."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info(f"=== UW Sentiment Agent — Starting run for {today} ===")

        source_results = {}
        all_scores = []

        for name, collector in self.collectors.items():
            logger.info(f"Collecting from {name}...")
            try:
                posts = collector.collect()
                result = self.analyzer.analyze_posts(posts)
                source_results[name] = result

                if result["posts_analyzed"] > 0:
                    all_scores.extend([result["avg_score"]] * result["posts_analyzed"])

                logger.info(
                    f"  {name}: {result['posts_analyzed']} posts, "
                    f"avg score: {result['avg_score']}"
                )
            except Exception as e:
                logger.error(f"Error processing {name}: {e}")
                source_results[name] = {
                    "posts_analyzed": 0,
                    "avg_score": 0.0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "top_topics": [],
                    "error": str(e),
                }

        # Calculate overall sentiment
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        overall_sentiment = self.analyzer.classify_sentiment(overall_score)
        summary = self.analyzer.generate_summary(overall_score, source_results)

        daily_result = {
            "date": today,
            "overall_sentiment": overall_sentiment,
            "sentiment_score": round(overall_score, 4),
            "summary": summary,
            "sources": source_results,
        }

        append_daily_result(daily_result)

        logger.info(f"Overall sentiment: {overall_sentiment} ({overall_score:.4f})")
        logger.info(f"Summary: {summary}")
        logger.info(f"=== Run complete for {today} ===")

        return daily_result
