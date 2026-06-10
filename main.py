import requests
import feedparser
import os
import time

# Configuration
RSS_URL = "https://rsshub.app/coolapk/hot"
STATE_FILE = "last_id.txt"
BARK_URL = os.environ.get("BARK_URL")

def notify_bark(title, content):
    if not BARK_URL:
        print("BARK_URL not set, skipping notification")
        return
    
    # Ensure title and content are URL encoded or at least safe
    # BARK API: https://api.day.app/your_key/title/content
    import urllib.parse
    safe_title = urllib.parse.quote(title)
    safe_content = urllib.parse.quote(content)
    
    url = f"{BARK_URL.rstrip('/')}/{safe_title}/{safe_content}"
    print(f"Sending notification to Bark...")
    try:
        r = requests.get(url)
        r.raise_for_status()
        print("Bark notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Bark notification: {e}")

def main():
    print(f"Fetching RSS feed from {RSS_URL}...")
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        print(f"Failed to parse feed: {e}")
        return
    
    if not feed.entries:
        print("No entries found in feed.")
        return

    # Load last seen ID
    last_id = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()

    new_entries = []
    for entry in feed.entries:
        if entry.id == last_id:
            break
        new_entries.append(entry)

    if not new_entries:
        print("No new posts.")
        # FORCE NOTIFICATION FOR TESTING
        if os.environ.get("GITHUB_EVENT_NAME") == "push":
             print("Push event detected, sending test notification...")
             notify_bark("Coolapk Monitor Test", "Test notification triggered by manual push!")
        return

    print(f"Found {len(new_entries)} new posts.")
    
    # Notify for the newest post
    latest = new_entries[0]
    notify_bark("Coolapk: " + getattr(latest, 'title', 'New Post'), getattr(latest, 'link', ''))

    # Update state
    with open(STATE_FILE, "w") as f:
        f.write(feed.entries[0].id)

if __name__ == "__main__":
    main()
