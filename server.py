from flask import Flask, request
import os
from telegram import Bot
from pymongo import MongoClient

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["telegrambot"]
subs_col = db["subscribers"]

app = Flask(__name__)
bot = Bot(token=TOKEN)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    msg = update.get("message")
    if msg and msg.get("text") == "/start":
        chat_id = msg["chat"]["id"]
        # Upsert the user (insert if not present)
        subs_col.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)
        bot.send_message(chat_id=chat_id, text="Subscribed! You'll get daily words. 😊")
    return "OK"

if __name__ == "__main__":
    app.run(port=5000)
