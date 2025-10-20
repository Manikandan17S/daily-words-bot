from flask import Flask, request
import os, json, random
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from threading import Lock
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUBSCRIBERS_FILE = "subscribers.json"

# Telegram bot
bot = Bot(token=TOKEN)

# Thread-safe lock for file operations
_lock = Lock()

# Load words
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# JSON helper functions
def load_subscribers():
    """Load subscriber chat IDs from JSON file"""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("subscribers", [])
    except:
        return []

def save_subscribers(subscribers):
    """Save subscriber chat IDs to JSON file"""
    with _lock:
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"subscribers": subscribers}, f, ensure_ascii=False, indent=2)

# Initialize subscribers file on startup
if not os.path.exists(SUBSCRIBERS_FILE):
    save_subscribers([])

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json()
    print("Received update:", update_data, flush=True)
    msg = update_data.get("message")
    
    if msg and msg.get("text") == "/start":
        chat_id = msg["chat"]["id"]
        print(f"New subscriber: {chat_id}", flush=True)
        
        try:
            subscribers = load_subscribers()
            if chat_id not in subscribers:
                subscribers.append(chat_id)
                save_subscribers(subscribers)
                asyncio.run(bot.send_message(
                    chat_id=chat_id,
                    text="✅ Subscribed! You'll receive daily English-Tamil words every morning at 7 AM IST. 🌅"
                ))
                print(f"✅ Added subscriber: {chat_id}", flush=True)
            else:
                asyncio.run(bot.send_message(
                    chat_id=chat_id,
                    text="You're already subscribed! 💙"
                ))
                print(f"ℹ️ Already subscribed: {chat_id}", flush=True)
        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
    
    return "OK"

# Health check endpoint
@app.route("/")
def home():
    return "Daily Words Bot is running! 🚀"

# Broadcast function
async def send_daily_words():
    print("🚀 Starting daily broadcast...", flush=True)
    subscribers = load_subscribers()
    
    if not subscribers:
        print("No subscribers yet.", flush=True)
        return
    
    print(f"Found {len(subscribers)} subscribers", flush=True)
    
    # Pick 5 random words
    selection = random.sample(words, k=5)
    lines = [f"• *{w['word']}* – _{w['tamil']}_" for w in selection]
    message = "🌅 *Word List for Today*\n\n" + "\n".join(lines)
    
    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            print(f"✅ Sent to {chat_id}", flush=True)
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}", flush=True)

# Schedule daily broadcast at 7:00 AM IST
def scheduled_broadcast():
    asyncio.run(send_daily_words())

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_broadcast, trigger="cron", hour=16, minute=15, timezone="Asia/Kolkata")
scheduler.start()

print(f"✅ Scheduler started. Next broadcast: {scheduler.get_jobs()}", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
