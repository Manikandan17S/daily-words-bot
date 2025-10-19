import json, random, os, asyncio
from telegram import Bot
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
bot = Bot(token=TOKEN)

client = MongoClient(MONGODB_URI)
db = client["telegrambot"]
subs_col = db["subscribers"]

# Load subscribers from MongoDB
subscribers = [s["chat_id"] for s in subs_col.find()]

# Load words
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

selection = random.sample(words, k=random.randint(5,10))
lines = [f"• *{w['word']}* – _{w['tamil']}_" for w in selection]
message = "🌅 *Word List for Today*\n\n" + "\n".join(lines)

async def broadcast():
    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

if __name__ == "__main__":
    asyncio.run(broadcast())
