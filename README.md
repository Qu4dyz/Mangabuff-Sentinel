# MangaBuff Sentinel 🛡️

An automated Discord bot for tracking MangaBuff notifications, trades, and market sales. 
Developed as a utility tool for active users of the platform.

## Features
- **Real-time Notifications:** Alerts for new manhwa chapters, trade offers, and market sales.
- **Interactive Controls:** Mark read or delete notifications directly from Discord.
- **Image Previews:** Automatically proxies images to bypass hotlink protection.
- **Watchlist:** Filter notifications to only see titles you care about.
- **Persistent Storage:** Uses SQLite to prevent duplicate alerts.

## Setup
1. Clone the repo.
2. Install dependencies: `pip install discord.py requests python-dotenv`
3. Create a `.env` file with your `DISCORD_TOKEN` and `CHANNEL_ID`.
4. Run your miner script once to generate `session_cache.json`.
5. Run `python main.py`.
