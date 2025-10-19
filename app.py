from flask import Flask, request
import os, json, random
from telegram import Bot, Update
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from urllib.parse import quote_plus

app = Flask(__name__)

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Get MongoDB credentials separately and encode them
MONGO_USERNAME = quote_plus(os.getenv("MONGO_USERNAME", ""))
MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD", ""))
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "")

# Build MongoDB URI with encoded credentials
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/dailywords?retryWrites=true&w=majority"

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["dailywords"]
subs_collection = db["subscribers"]

# Telegram bot
bot = Bot(token=TOKEN)

# Load words
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json()
    msg = update_data.get("message")
    if msg and msg.get("text") == "/start":
        chat_id = msg["chat"]["id"]
        # Add subscriber if not exists
        if not subs_collection.find_one({"chat_id": chat_id}):
            subs_collection.insert_one({"chat_id": chat_id})
            bot.send_message(chat_id=chat_id, text="✅ Subscribed! You'll receive daily English-Tamil words every morning at 7 AM IST. 🌅")
        else:
            bot.send_message(chat_id=chat_id, text="You're already subscribed! 💙")
    return "OK"

# Health check endpoint
@app.route("/")
def home():
    return "Daily Words Bot is running! 🚀"

# Broadcast function
async def send_daily_words():
    subscribers = [doc["chat_id"] for doc in subs_collection.find()]
    if not subscribers:
        print("No subscribers yet.")
        return
    
    # Pick 5 random words
    selection = random.sample(words, k=5)
    lines = [f"• *{w['word']}* – _{w['tamil']}_" for w in selection]
    message = "🌅 *Word List for Today*\n\n" + "\n".join(lines)
    
    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            print(f"Sent to {chat_id}")
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

# Schedule daily broadcast at 7:00 AM IST
def scheduled_broadcast():
    asyncio.run(send_daily_words())

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_broadcast, trigger="cron", hour=7, minute=0, timezone="Asia/Kolkata")
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
