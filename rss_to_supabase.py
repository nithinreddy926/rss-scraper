#!/usr/bin/env python3
"""
rss_to_supabase.py
- Parses Times of India Top Stories RSS
- Saves only new articles to news_data.csv
- Uploads new articles to Supabase (upsert)
"""

import os
import time
import hashlib
import feedparser
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# --- Config ---
RSS_FEED_URL = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
CSV_FILE = "news_data.csv"

# --- Load env ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")

# --- Create Supabase client ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def make_id_from_link(link: str) -> str:
    """Create deterministic unique id from link using sha256."""
    return hashlib.sha256(link.encode("utf-8")).hexdigest()

def parse_entry_published(entry) -> str:
    """Try to return an ISO8601 timestamp for the entry, or fallback to published text."""
    try:
        if "published_parsed" in entry and entry.published_parsed:
            # published_parsed is a time.struct_time
            ts = time.mktime(entry.published_parsed)
            return datetime.fromtimestamp(ts).isoformat()
        # fallback
        return entry.get("published", "")
    except Exception:
        return entry.get("published", "")

def read_existing_csv(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        try:
            return pd.read_csv(path, dtype=str)
        except Exception as e:
            print(f"Warning: failed to read existing CSV ({e}). Creating new dataframe.")
    # default empty DF with expected columns
    return pd.DataFrame(columns=["id", "title", "link", "published", "description"])

def save_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"CSV saved to: {path} (rows: {len(df)})")

def upload_to_supabase(rows: list):
    if not rows:
        print("No rows to upload.")
        return
    try:
        # upsert accepts a list of dicts; ensure keys match table columns
        res = supabase.table("news").upsert(rows).execute()
        # res is a PostgrestResponse-like object — print summary
        print("Supabase upsert response:", getattr(res, "status_code", None), getattr(res, "data", None))
    except Exception as e:
        print("Error uploading to Supabase:", e)

def main():
    # Load existing CSV and determine already-seen ids
    df_existing = read_existing_csv(CSV_FILE)
    existing_ids = set(df_existing["id"].dropna().astype(str).tolist())

    # Parse feed
    print("Fetching RSS feed:", RSS_FEED_URL)
    feed = feedparser.parse(RSS_FEED_URL)
    if feed.bozo:
        print("Warning: feedparser reported a problem with the feed (bozo). Continuing anyway.")

    new_rows = []
    for entry in feed.entries:
        link = entry.get("link", "").strip()
        if not link:
            continue  # skip if no link

        uid = make_id_from_link(link)
        if uid in existing_ids:
            # already saved
            continue

        title = entry.get("title", "").strip()
        description = entry.get("description", "").strip()
        published = parse_entry_published(entry)

        row = {
            "id": uid,
            "title": title,
            "link": link,
            "published": published,
            "description": description
        }
        new_rows.append(row)

    if not new_rows:
        print("No new articles found. Exiting.")
        return

    # Append new rows to CSV
    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    save_csv(df_combined, CSV_FILE)
    print(f"Added {len(new_rows)} new articles.")

    # Upload to Supabase
    print("Uploading new articles to Supabase...")
    upload_to_supabase(new_rows)
    print("Done.")

if __name__ == "__main__":
    main()
