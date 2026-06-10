# Coolapk Monitor

This project monitors the Coolapk hot feed using RSSHub and runs automatically on GitHub Actions.

## How it works
1. It fetches the RSS feed from [RSSHub](https://rsshub.app/coolapk/hot).
2. It compares the latest post with a stored state file (`last_id.txt`).
3. If a new post is found, it sends a notification and updates the state.
4. The process is automated using GitHub Actions.

## Configuration
To receive notifications, set one of the following as a **GitHub Repository Secret**:
- `BARK_URL`: Your Bark endpoint (e.g., `https://api.day.app/yourkey/`)
- `PUSHDEER_KEY`: Your Pushdeer push key
- `TELEGRAM_TOKEN` & `TELEGRAM_CHAT_ID`: Your Telegram bot credentials

The workflow runs every 2 hours by default.
