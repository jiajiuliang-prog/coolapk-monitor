import requests
import feedparser
import os
import time
import urllib.parse

# Configuration
RSS_URL = "https://rsshub.app/coolapk/hot"
STATE_FILE = "last_id.txt"
BARK_URL = os.environ.get("BARK_URL")

def notify_bark(title, content):
    if not BARK_URL:
        print("BARK_URL is empty or not set in Environment Variables")
        return
    
    # BARK API can be:
    # 1. https://api.day.app/KEY/title/content
    # 2. https://api.day.app/KEY?title=...&body=...
    
    # Let's try the more robust query parameter method
    base_url = BARK_URL.rstrip('/')
    if '/igws' in base_url and '?' not in base_url:
        # If the user provided the full URL like https://api.day.app/KEY/
        # we construct the parameters
        params = {
            "title": title,
            "body": content,
            "group": "CoolapkMonitor"
        }
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
    else:
        # Fallback to the path-based URL if it's just the key or a different format
        safe_title = urllib.parse.quote(title)
        safe_content = urllib.parse.quote(content)
        url = f"{base_url}/{safe_title}/{safe_content}"

    print(f"DEBUG: Attempting to send notification to: {BARK_URL[:25]}...")
    try:
        r = requests.get(url, timeout=10)
        print(f"Bark Response Status: {r.status_code}")
        print(f"Bark Response Body: {r.text}")
        r.raise_for_status()
        print("Bark notification command executed.")
    except Exception as e:
        print(f"Failed to send Bark notification: {e}")

def main():
    print("--- Coolapk Monitor Start ---")
    print(f"Fetching RSS feed from {RSS_URL}...")
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        print(f"CRITICAL: Failed to parse feed: {e}")
        return
    
    if not feed.entries:
        print("No entries found in feed. RSSHub might be down or rate-limited.")
        return

    # Load last seen ID
    last_id = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()
            print(f"Last processed ID: {last_id}")

    new_entries = []
    for entry in feed.entries:
        if entry.id == last_id:
            break
        new_entries.append(entry)

    # For testing purposes, we always send a notification on 'push'
    if os.environ.get("GITHUB_EVENT_NAME") == "push":
        print("Manual Push detected: Sending TEST notification regardless of feed state.")
        notify_bark("Coolapk Monitor Test", "Connection successful! Monitoring is active.")

    if not new_entries:
        print("No new posts found since last check.")
    else:
        print(f"Found {len(new_entries)} new posts.")
        # Notify for the newest post
        latest = new_entries[0]
        notify_bark("Coolapk: " + getattr(latest, 'title', 'New Post'), getattr(latest, 'link', ''))

    # Always update state to the latest entry to avoid duplicate notifications
    if feed.entries:
        with open(STATE_FILE, "w") as f:
            f.write(feed.entries[0].id)
        print(f"Updated state with latest ID: {feed.entries[0].id}")

    print("--- Coolapk Monitor End ---")

if __name__ == "__main__":
    main()
