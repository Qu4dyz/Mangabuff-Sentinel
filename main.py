import discord
from discord.ext import tasks, commands
from discord.ui import Button, View
import requests
import re
import json
import os
import datetime
import sqlite3
import io
from dotenv import load_dotenv

# Load private keys from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# === 🌐 MANGABUFF API ===
URL_BASE = "https://mangabuff.ru"
URL_NOTIFICATIONS = "https://mangabuff.ru/notifications"
REGEX_ITEM = r'data-id="([^"]+)".*?src="([^"]+)".*?class="notifications__name">\s*(.*?)</div>'

# === 📂 DATA STORAGE ===
SESSION_FILE = "session_cache.json"
WATCHLIST_FILE = "watchlist.json"
DB_FILE = "notifications.db"


# === 🗄️ DATABASE HELPERS ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS processed (notif_id TEXT PRIMARY KEY)')
    conn.commit()
    conn.close()


def is_processed(notif_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT 1 FROM processed WHERE notif_id = ?', (notif_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def mark_processed_db(notif_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO processed (notif_id) VALUES (?)', (notif_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


# === 🛠️ FILE HELPERS ===
def load_json(filename, default=None):
    if default is None: default = []
    if not os.path.exists(filename): return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)


def get_headers(session_data):
    return {
        "User-Agent": session_data.get("agent", "Mozilla/5.0"),
        "X-CSRF-TOKEN": session_data.get("csrf", ""),
        "X-Requested-With": "XMLHttpRequest"
    }


def clean_html(raw_html):
    clean = re.sub(r'<[^>]+>', '', raw_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def clean_url(url):
    if not url: return None
    if not url.startswith("http"): url = f"{URL_BASE}{url}"
    return url.replace("mangabuff.ru//", "mangabuff.ru/").replace("/x70//img", "/x70/img")


# === 🎮 INTERACTIVE BUTTONS ===
class NotificationView(View):
    def __init__(self, notif_id, link=None):
        super().__init__(timeout=None)
        self.notif_id = notif_id
        if link: self.add_item(Button(label="🔗 Open", url=f"{URL_BASE}{link}"))

    @discord.ui.button(label="📖 Mark Read", style=discord.ButtonStyle.green, custom_id="mark_read_static")
    async def mark_read(self, interaction: discord.Interaction, button: Button):
        success = self._api_request(f"{URL_NOTIFICATIONS}/{self.notif_id}/read", method="POST")
        if success:
            await interaction.response.send_message("✅ Marked as read!", ephemeral=True)
            button.disabled = True
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message("❌ Failed. Session invalid?", ephemeral=True)

    @discord.ui.button(label="🗑️ Delete", style=discord.ButtonStyle.danger, custom_id="delete_static")
    async def delete_notif(self, interaction: discord.Interaction, button: Button):
        success = self._api_request(f"{URL_NOTIFICATIONS}/{self.notif_id}", method="POST", data={"_method": "DELETE"})
        if success:
            await interaction.response.send_message("🗑️ Deleted.", ephemeral=True)
            await interaction.message.delete()
        else:
            await interaction.response.send_message("❌ Failed to delete.", ephemeral=True)

    def _api_request(self, url, method="POST", data=None):
        session = load_json(SESSION_FILE, {})
        if not session: return False
        try:
            res = requests.post(url, cookies=session.get("cookies", {}), headers=get_headers(session), data=data)
            return res.status_code == 200
        except:
            return False


# === 🤖 BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    init_db()
    print(f'✅ Logged in as {bot.user}')
    if not check_notifications.is_running(): check_notifications.start()


@tasks.loop(minutes=5)
async def check_notifications():
    session = load_json(SESSION_FILE, {})
    if not session: return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return

    try:
        res = requests.get(URL_NOTIFICATIONS, cookies=session.get("cookies", {}), headers=get_headers(session))
        if res.status_code == 200:
            items = re.findall(REGEX_ITEM, res.text, re.DOTALL)
            watchlist = load_json(WATCHLIST_FILE, [])

            for n_id, img_src, raw_content in items:
                if is_processed(n_id): continue  # <--- DB CHECK

                text_content = clean_html(raw_content)
                link_match = re.search(r'href="([^"]+)"', raw_content)
                item_link = link_match.group(1) if link_match else None

                should_notify = False
                color = 0x8b00ff

                if "обмен" in text_content.lower():
                    color, should_notify = 0xFF0000, True
                elif "купил ваш" in text_content.lower():
                    color, should_notify = 0xF1C40F, True
                elif "свиток" in text_content.lower() or "получили новую карту" in text_content.lower():
                    color, should_notify = 0x3498DB, True
                else:
                    if not watchlist or any(w.lower() in text_content.lower() for w in watchlist):
                        should_notify, color = True, 0x2ECC71

                if should_notify:
                    file_attachment = None
                    full_img_url = clean_url(img_src)
                    if full_img_url:
                        img_res = requests.get(full_img_url, cookies=session.get("cookies", {}),
                                               headers=get_headers(session))
                        if img_res.status_code == 200:
                            file_attachment = discord.File(io.BytesIO(img_res.content), filename="thumb.jpg")

                    embed = discord.Embed(description=f"**{text_content}**", color=color,
                                          timestamp=datetime.datetime.now())
                    if file_attachment: embed.set_thumbnail(url="attachment://thumb.jpg")
                    embed.set_footer(text="MangaBuff Sentinel")

                    view = NotificationView(n_id, item_link)
                    view.children[0].custom_id = f"read_{n_id}"
                    view.children[1].custom_id = f"del_{n_id}"

                    await channel.send(embed=embed, view=view,
                                       file=file_attachment) if file_attachment else await channel.send(embed=embed,
                                                                                                        view=view)

                    mark_processed_db(n_id)  # <--- DB SAVE
    except Exception as e:
        print(f"Error: {e}")


bot.run(DISCORD_TOKEN)