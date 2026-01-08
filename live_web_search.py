#!/usr/bin/env python3
"""
Live Web News Search using NewsAPI
Fetches news articles directly from the web on each query
"""

import os
from newsapi import NewsApiClient
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
from datetime import datetime
import argparse

# Load environment variables
load_dotenv()

class LiveNewsSearch:
    def __init__(self):
        """Initialize NewsAPI client and embedding model"""
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            raise ValueError("NEWSAPI_KEY not found in environment variables")
        
        self.newsapi = NewsApiClient(api_key=api_key)
        print("Loading embedding model...")
        self.model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')
        print("Model loaded successfully!")
    
    def fetch_articles(self, query, language='en', page_size=50):
        """Fetch articles from NewsAPI"""
        try:
            # Get everything about the query from the last 7 days
            response = self.newsapi.get_everything(
                q=query,
                language=language,
                sort_by='relevancy',
                page_size=page_size
            )
            
            articles = []
            for article in response.get('articles', []):
                # Combine title and description for better search
                text = f"{article.get('title', '')} {article.get('description', '')}"
                
                articles.append({
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', 'No description'),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'text': text
                })
            
            print(f"Fetched {len(articles)} articles from the web")
            return articles
        
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def search(self, query, k=5):
        """Search for articles and rank by semantic similarity"""
        # Fetch articles from the web
        articles = self.fetch_articles(query)
        
        if not articles:
            print("No articles found")
            return []
        
        # Extract texts for embedding
        texts = [a['text'] for a in articles]
        
        # Generate embeddings
        print("Generating embeddings...")
        doc_embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]
        
        # Calculate similarity scores
        scores = np.dot(doc_embeddings, query_embedding)
        
        # Get top k results
        top_indices = np.argsort(-scores)[:k]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            article = articles[idx]
            results.append({
                'rank': rank,
                'score': float(scores[idx]),
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'published_at': article['published_at'],
                'snippet': article['description'][:200] + '...' if len(article['description']) > 200 else article['description']
            })
        
        return results
    
    def print_results(self, results):
        """Pretty print search results"""
        if not results:
            print("\nNo results found.")
            return
        
        print(f"\n{'='*100}")
        print(f"Found {len(results)} relevant articles from the web:")
        print(f"{'='*100}\n")
        
        for result in results:
            print(f"Rank {result['rank']} | Score: {result['score']:.4f}")
            print(f"Title: {result['title']}")
            print(f"Source: {result['source']} | Published: {result['published_at']}")
            print(f"Snippet: {result['snippet']}")
            print(f"URL: {result['url']}")
            print(f"{'-'*100}\n")

def main():
    parser = argparse.ArgumentParser(description='Search news articles from the web')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('-k', '--top-k', type=int, default=5, help='Number of results to return (default: 5)')
    args = parser.parse_args()
    
    # Initialize search engine
    engine = LiveNewsSearch()
    
    # Interactive mode if no query provided
    if not args.query:
        print("\nLive Web News Search Engine")
        print("Enter your query (or 'quit' to exit):\n")
        
        while True:
            query = input("Search: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if query:
                results = engine.search(query, k=args.top_k)
                engine.print_results(results)
    else:
        # Single query mode
        results = engine.search(args.query, k=args.top_k)
        engine.print_results(results)

if __name__ == "__main__":
    main()
