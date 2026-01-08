import streamlit as st
import os
from newsapi import NewsApiClient
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Live News Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = None

class LiveNewsSearch:
    def __init__(self):
        """Initialize NewsAPI client and embedding model"""
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            raise ValueError("NEWSAPI_KEY not found in environment variables")
        
        self.newsapi = NewsApiClient(api_key=api_key)
        self.model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')
    
    def fetch_articles(self, query, language='en', page_size=50):
        """Fetch articles from NewsAPI"""
        try:
            response = self.newsapi.get_everything(
                q=query,
                language=language,
                sort_by='relevancy',
                page_size=page_size
            )
            
            articles = []
            for article in response.get('articles', []):
                text = f"{article.get('title', '')} {article.get('description', '')}"
                articles.append({
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', 'No description'),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'image': article.get('urlToImage', ''),
                    'text': text
                })
            return articles
        except Exception as e:
            st.error(f"Error fetching articles: {e}")
            return []
    
    def search(self, query, k=5):
        """Search for articles and rank by semantic similarity"""
        articles = self.fetch_articles(query)
        
        if not articles:
            return []
        
        texts = [a['text'] for a in articles]
        doc_embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]
        scores = np.dot(doc_embeddings, query_embedding)
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
                'description': article['description'],
                'image': article['image']
            })
        return results

# App UI
st.title("🔍 Live Web News Search")
st.markdown("Search news articles from 80,000+ sources worldwide, ranked by semantic relevance")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    num_results = st.slider("Number of results", 1, 20, 5)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app fetches live news articles using NewsAPI and ranks them using AI-powered semantic search.")
    st.markdown("**Powered by:**")
    st.markdown("- NewsAPI.org")
    st.markdown("- Sentence Transformers")

# Initialize search engine
try:
    if st.session_state.search_engine is None:
        with st.spinner("Loading AI model..."):
            st.session_state.search_engine = LiveNewsSearch()
except ValueError as e:
    st.error("❌ NewsAPI key not found! Please add your API key to the .env file.")
    st.info("Get your free API key at https://newsapi.org/")
    st.stop()

# Search interface
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("🔎 Enter your search query", placeholder="e.g., artificial intelligence, climate change, technology...")
with col2:
    st.write("")
    st.write("")
    search_button = st.button("Search", type="primary", use_container_width=True)

# Perform search
if search_button and query:
    with st.spinner(f"Fetching and analyzing articles for '{query}'..."):
        results = st.session_state.search_engine.search(query, k=num_results)
    
    if results:
        st.success(f"✅ Found {len(results)} relevant articles")
        st.markdown("---")
        
        # Display results
        for result in results:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if result['image']:
                    st.image(result['image'], use_container_width=True)
                else:
                    st.markdown("📰")
            
            with col2:
                st.markdown(f"### [{result['title']}]({result['url']})")
                st.markdown(f"**{result['source']}** | {result['published_at'][:10]} | Relevance: {result['score']:.2%}")
                st.markdown(result['description'])
                st.markdown("")
            
            st.markdown("---")
    else:
        st.warning("No articles found. Try a different query.")

elif not query and search_button:
    st.warning("Please enter a search query.")

# Example queries
if not query:
    st.markdown("### 💡 Example Queries")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Artificial Intelligence", use_container_width=True):
            st.experimental_rerun()
    with col2:
        if st.button("Climate Change", use_container_width=True):
            st.experimental_rerun()
    with col3:
        if st.button("Space Exploration", use_container_width=True):
            st.experimental_rerun()
