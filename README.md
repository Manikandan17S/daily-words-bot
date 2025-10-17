# Daily English–Tamil Words Bot

This project sends 5–10 random English–Tamil word pairs daily via Telegram.

## Setup

1. Create a Telegram bot and get `BOT_TOKEN` and `CHAT_ID`.
2. Add repository secrets in GitHub:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Push this repo to GitHub.

## Usage

- GitHub Actions will run `bot.py` daily at 01:00 UTC.
- Adjust schedule in `.github/workflows/daily.yml`.
