# 🛡️ MangaBuff Sentinel

**MangaBuff Sentinel** is an automated Discord bot designed for users of the MangaBuff platform. It monitors your account for new manga chapters, trade offers, and market sales, providing a real-time "Command Center" directly in your Discord server.

## ✨ Features
* **Real-time Monitoring:** Checks for updates every 5 minutes.
* **Interactive Controls:** **Read**, **Delete**, or **Open** notifications via Discord buttons.
* **Smart Filtering:** Use the `!watch` command to only get pings for specific manhwa titles.
* **Image Proxying:** Automatically downloads and uploads thumbnails to Discord to bypass site hotlink protection.
* **Persistent Storage:** Uses a SQLite database to ensure you never receive the same notification twice.

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.8+** installed.
```bash
pip install discord.py requests python-dotenv
```
2. Discord Bot Setup
Go to the Discord Developer Portal.

Create a New Application and name it (e.g., "MangaBuff Sentinel").

Navigate to the Bot tab and enable Message Content Intent under the "Privileged Gateway Intents" section.

Reset and copy your Token.

Invite the bot to your server using the OAuth2 URL Generator (Scopes: bot, applications.commands; Permissions: Administrator or Manage Messages/Embed Links).

3. Environment Configuration
Create a file named .env in the root directory and paste your credentials:

```
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=your_target_channel_id
```
4. Session Configuration
To access your personal notifications, the bot needs your session data.

Log into MangaBuff in your browser.

Open Developer Tools (F12) -> Network tab.

Refresh the page and click on the request named notifications.

In the Headers tab, find Request Headers and copy your User-Agent and Cookie values.

Create a session_cache.json file in the bot folder using this format:

JSON
```
{
    "cookies": {
        "mangabuff_session": "PASTE_VALUE_OF_MANGABUFF_SESSION_COOKIE_HERE"
    },
    "agent": "PASTE_YOUR_FULL_USER_AGENT_HERE",
    "csrf": "PASTE_CSRF_TOKEN_FROM_PAGE_SOURCE_OR_HEADERS"
}
```
🎮 Commands
!watch [Title] — Adds a manga to your watchlist (e.g., !watch Solo Leveling).

!unwatch [Title] — Removes a manga from your watchlist.

!list — Shows your current watchlist. If empty, all notifications are sent.

🛠️ Tech Stack
Language: Python 3.12

Library: Discord.py (Asynchronous)

Database: SQLite3 (Persistence)

API: REST (Requests)

⚖️ Disclaimer
This project is an unofficial utility tool created for educational purposes. It is not affiliated with or endorsed by MangaBuff. Use at your own risk.
