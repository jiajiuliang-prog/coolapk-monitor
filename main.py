import os
import requests
import feedparser
import json

RSS_URL = "https://rsshub.app/coolapk/hot"
STATE_FILE = "last_id.txt"

def notify(title, content):
    print(f"New Post: {title}")
    
    # Bark
    bark_url = os.getenv("BARK_URL")
    if bark_url:
        requests.get(f"{bark_url}/{title}/{content}")
        
    # Pushdeer
    pushdeer_key = os.getenv("PUSHDEER_KEY")
    if pushdeer_key:
        requests.get("https://api2.pushdeer.com/message/push", params={"pushkey": pushdeer_key, "text": title, "desp": content})

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No entries found.")
        return

    latest_entry = feed.entries[0]
    latest_id = latest_entry.id

    # Read last seen ID
    last_id = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()

    if latest_id != last_id:
        notify(latest_entry.title, latest_entry.link)
        
        # Save new state
        with open(STATE_FILE, "w") as f:
            f.write(latest_id)
        print(f"Updated last_id to {latest_id}")
    else:
        print("No new posts.")

if __name__ == "__main__":
    main()
