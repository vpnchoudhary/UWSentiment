import logging

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

# Download VADER lexicon on first use
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)


class SentimentAnalyzer:
    """Analyzes sentiment of social media posts using VADER."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_posts(self, posts: list[dict]) -> dict:
        """Analyze a list of posts and return aggregated sentiment results.

        Returns:
            dict with sentiment scores, classification, and top topics.
        """
        if not posts:
            return {
                "posts_analyzed": 0,
                "avg_score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "top_topics": [],
            }

        scores = []
        positive = 0
        negative = 0
        neutral = 0
        topic_mentions = {}

        for post in posts:
            text = f"{post.get('title', '')} {post.get('text', '')}".strip()
            if not text:
                continue

            sentiment = self.analyzer.polarity_scores(text)
            compound = sentiment["compound"]
            scores.append(compound)

            if compound >= 0.05:
                positive += 1
            elif compound <= -0.05:
                negative += 1
            else:
                neutral += 1

            # Extract simple topic indicators
            self._extract_topics(text, topic_mentions)

        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Sort topics by frequency
        top_topics = sorted(topic_mentions.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "posts_analyzed": len(scores),
            "avg_score": round(avg_score, 4),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "top_topics": [{"topic": t, "mentions": c} for t, c in top_topics],
        }

    def classify_sentiment(self, score: float) -> str:
        """Classify an average compound score into a label."""
        if score >= 0.2:
            return "very positive"
        elif score >= 0.05:
            return "positive"
        elif score <= -0.2:
            return "very negative"
        elif score <= -0.05:
            return "negative"
        return "neutral"

    def generate_summary(self, overall_score: float, source_results: dict) -> str:
        """Generate a human-readable summary of the day's sentiment."""
        sentiment_label = self.classify_sentiment(overall_score)
        total_posts = sum(r.get("posts_analyzed", 0) for r in source_results.values())

        if total_posts == 0:
            return "No posts were collected today. Check API credentials and connectivity."

        sources_with_data = [
            name for name, r in source_results.items() if r.get("posts_analyzed", 0) > 0
        ]

        # Collect all top topics across sources
        all_topics = []
        for result in source_results.values():
            all_topics.extend(t["topic"] for t in result.get("top_topics", []))

        top_topics_str = ", ".join(all_topics[:5]) if all_topics else "general discussion"

        summary = (
            f"Overall sentiment towards University of Washington Seattle is {sentiment_label} "
            f"(score: {overall_score:.2f}) based on {total_posts} posts from "
            f"{', '.join(sources_with_data)}. "
            f"Top discussion topics: {top_topics_str}."
        )

        return summary

    def _extract_topics(self, text: str, topic_mentions: dict):
        """Extract UW-related topic keywords from text."""
        topics = {
            "academics": ["class", "professor", "course", "gpa", "major", "degree", "lecture"],
            "campus life": ["campus", "dorm", "housing", "dining", "student", "greek"],
            "admissions": ["admit", "acceptance", "application", "apply", "transfer", "rejected"],
            "athletics": ["husky", "football", "basketball", "game", "stadium"],
            "research": ["research", "lab", "publication", "professor", "phd"],
            "career": ["career", "internship", "job", "hire", "recruit", "salary"],
            "cs/engineering": ["cs", "cse", "engineering", "computer science", "paul allen"],
            "cost/finance": ["tuition", "financial aid", "scholarship", "cost", "expensive"],
        }

        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                topic_mentions[topic] = topic_mentions.get(topic, 0) + 1
