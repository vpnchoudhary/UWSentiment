# UWSentiment
Determine sentiments towards UW from public forums

## Overview
Autonomous Python agent that scans Reddit, Facebook, and Instagram daily for public sentiment towards the University of Washington Seattle. Results are stored in a JSON file with daily sentiment scores and summaries.

## Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Configure API credentials:**
   ```
   copy .env.example .env
   ```
   Edit `.env` with your API keys:
   - **Reddit** (required): Create an app at https://www.reddit.com/prefs/apps
   - **Facebook** (optional): Requires approved Meta app with Page Public Content Access
   - **Instagram** (optional): Requires Meta Business app with Instagram Graph API access

## Usage

**Run once:**
```
python main.py
```

**Run daily at midnight (scheduled):**
```
python main.py --schedule
```

**Run daily at a custom time:**
```
python main.py --schedule --time 08:00
```

## Output
Results are appended to `data/sentiment_results.json` with this structure:
```json
{
  "date": "2026-03-26",
  "overall_sentiment": "positive",
  "sentiment_score": 0.42,
  "summary": "Overall sentiment towards UW Seattle is positive...",
  "sources": {
    "reddit": { "posts_analyzed": 50, "avg_score": 0.38, "top_topics": [...] },
    "facebook": { "posts_analyzed": 0, "avg_score": 0, "top_topics": [] },
    "instagram": { "posts_analyzed": 0, "avg_score": 0, "top_topics": [] }
  }
}
```

## Architecture
- `src/collectors/` — Platform-specific data collectors (Reddit, Facebook, Instagram)
- `src/analyzer.py` — VADER sentiment analysis + topic extraction
- `src/storage.py` — JSON file storage with daily append
- `src/agent.py` — Main orchestrator
- `main.py` — Entry point with scheduler
