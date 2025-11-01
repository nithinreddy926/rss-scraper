import feedparser
import pandas as pd
import hashlib
import json
import os
from datetime import datetime
from supabase import create_client, Client

# ✅ Supabase credentials
SUPABASE_URL = "https://bwtgiawaktzohibphcgx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3dGdpYXdha3R6b2hpYnBoY2d4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4Njk1NzUsImV4cCI6MjA3NjQ0NTU3NX0.vt01f-cymLgyCRcZ0d_zdv8Lu04yhiYg_F2kU08mX4c"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

csv_file = "news_data.csv"
config_file = "rss_links.json"

# ✅ Load RSS feed config
with open(config_file, "r") as f:
    rss_sources = json.load(f)

all_articles = []

# ✅ Loop through all sources & categories
for source, categories in rss_sources.items():
    for category, rss_url in categories.items():
        print(f"Fetching: {source} -> {category}")

        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            published = entry.get("published", datetime.utcnow().isoformat())

            # Unique ID for each article
            uid = hashlib.sha256(link.encode()).hexdigest()

            all_articles.append({
                "id": uid,
                "title": title,
                "link": link,
                "published": published,
                "source": source,
                "category": category
            })

# ✅ Load existing CSV to avoid duplicates
if os.path.exists(csv_file):
    old_data = pd.read_csv(csv_file)
else:
    old_data = pd.DataFrame(columns=["id","title","link","published","source","category"])

# ✅ Convert to DataFrame
df = pd.DataFrame(all_articles)

# ✅ Filter new rows only
new_rows = df[~df['id'].isin(old_data['id'])]

# ✅ Save updated CSV
final_df = pd.concat([old_data, new_rows], ignore_index=True)
final_df.to_csv(csv_file, index=False)

print(f"✅ New articles added: {len(new_rows)}")

if len(new_rows) > 0:
    try:
        res = supabase.table("news").upsert(new_rows.to_dict(orient="records")).execute()
        print("✅ Uploaded to Supabase")
    except Exception as e:
        print("❌ Error uploading:", e)
else:
    print("No new news to upload.")
