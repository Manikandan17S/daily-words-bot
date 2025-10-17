import json, random, os, asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("secrets.TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

# Load subscribers
with open("subscribers.json", "r") as f:
    subscribers = json.load(f)

# Load words
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# Pick 5–10 random words
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
