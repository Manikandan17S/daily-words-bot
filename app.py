from flask import Flask, request
import os, json, random, sqlite3
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_FILE = "subscribers.db"

# Telegram bot
bot = Bot(token=TOKEN)

# Load words
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            chat_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json()
    print("Received update:", update_data, flush=True)
    msg = update_data.get("message")
    if msg and msg.get("text") == "/start":
        chat_id = msg["chat"]["id"]
        print(f"New subscriber: {chat_id}", flush=True)
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)", (chat_id,))
            conn.commit()
            bot.send_message(chat_id=chat_id, text="✅ Subscribed! You'll receive daily English-Tamil words every morning at 7 AM IST. 🌅")
        except Exception as e:
            print(f"Error: {e}", flush=True)
        finally:
            conn.close()
    return "OK"

# Health check endpoint
@app.route("/")
def home():
    return "Daily Words Bot is running! 🚀"

# Broadcast function
async def send_daily_words():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM subscribers")
    subscribers = [row[0] for row in cur.fetchall()]
    conn.close()
    
    if not subscribers:
        print("No subscribers yet.", flush=True)
        return
    
    # Pick 5 random words
    selection = random.sample(words, k=5)
    lines = [f"• *{w['word']}* – _{w['tamil']}_" for w in selection]
    message = "🌅 *Word List for Today*\n\n" + "\n".join(lines)
    
    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            print(f"Sent to {chat_id}", flush=True)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}", flush=True)

# Schedule daily broadcast at 7:00 AM IST
def scheduled_broadcast():
    asyncio.run(send_daily_words())

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_broadcast, trigger="cron", hour=7, minute=0, timezone="Asia/Kolkata")
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
