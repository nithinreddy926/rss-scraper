# Live Web News Search

A semantic news search engine that fetches articles directly from the web using NewsAPI and ranks them by relevance using sentence transformers.

## Features

- **Live Web Search**: Fetches fresh news articles from the web on each query using NewsAPI
- **Semantic Ranking**: Uses sentence-transformers to rank articles by semantic similarity to your query
- **No Database Required**: Results are fetched and processed in real-time
- **Interactive Mode**: Command-line interface for continuous searching
- **Customizable Results**: Choose how many top results to display

## How It Works

1. Takes your search query
2. Fetches up to 50 relevant articles from NewsAPI (from thousands of news sources worldwide)
3. Generates semantic embeddings for articles and query using `multi-qa-MiniLM-L6-cos-v1` model
4. Ranks articles by cosine similarity
5. Returns top 5 (or custom number) most relevant results

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/nithinreddy926/rss-scraper.git
cd rss-scraper
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get NewsAPI Key
- Go to [https://newsapi.org/](https://newsapi.org/)
- Sign up for a free account
- Copy your API key

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your NewsAPI key
```

## Usage

### Interactive Mode
```bash
python live_web_search.py
```

Then enter your queries:
```
Search: artificial intelligence breakthroughs
Search: climate change solutions
Search: quit
```

### Single Query Mode
```bash
python live_web_search.py "machine learning trends"
```

### Custom Number of Results
```bash
python live_web_search.py "data science" -k 10
```

## Example Output

```
====================================================================================================
Found 5 relevant articles from the web:
====================================================================================================

Rank 1 | Score: 0.8542
Title: New AI Model Achieves Human-Level Performance
Source: TechCrunch | Published: 2026-01-08T10:30:00Z
Snippet: Researchers announce breakthrough in artificial intelligence with a new model that matches human performance...
URL: https://techcrunch.com/example-article
----------------------------------------------------------------------------------------------------

Rank 2 | Score: 0.8234
...
```

## Technical Details

- **News Source**: NewsAPI.org (access to 80,000+ news sources)
- **Embedding Model**: sentence-transformers/multi-qa-MiniLM-L6-cos-v1
- **Similarity Metric**: Cosine similarity via normalized dot product
- **Languages**: Currently supports English articles

## Differences from Previous RSS-Based System

| Feature | Old RSS System | New Web Search |
|---------|---------------|----------------|
| Data Source | Fixed RSS feeds | NewsAPI (80,000+ sources) |
| Freshness | Every 6 hours | Real-time on query |
| Storage | Supabase + FAISS | No storage needed |
| Coverage | ~10 news sources | Global news coverage |
| Setup Complexity | Complex (DB + scheduler) | Simple (just API key) |

## Requirements

- Python 3.8+
- NewsAPI key (free tier: 100 requests/day)
- 2GB RAM minimum for embedding model

## Limitations

- NewsAPI free tier: 100 requests per day
- Maximum 50 articles per query
- Articles from last 30 days only (free tier)

## License

MIT

## Author

Nithin Reddy
