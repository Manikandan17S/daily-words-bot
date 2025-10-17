from flask import Flask, request
import json, os
from telegram import Bot

app = Flask(__name__)
TOKEN = os.getenv("secrets.TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
SUB_FILE = "subscribers.json"

def load_subs():
    with open(SUB_FILE, "r") as f:
        return json.load(f)

def save_subs(subs):
    with open(SUB_FILE, "w") as f:
        json.dump(subs, f)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    msg = update.get("message")
    if msg and msg.get("text") == "/start":
        chat_id = msg["chat"]["id"]
        subs = load_subs()
        if chat_id not in subs:
            subs.append(chat_id)
            save_subs(subs)
            bot.send_message(chat_id=chat_id, text="Subscribed! You’ll get daily words. 😊")
    return "OK"

if __name__ == "__main__":
    app.run(port=5000)
