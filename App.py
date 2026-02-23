import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Get Telegram credentials from Railway environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Function to send Telegram message
def send_telegram(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(TELEGRAM_URL, json=payload)
    except Exception as e:
        print("Telegram send error:", e)

# Webhook route for TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return "No data received", 400

    action = data.get("action")
    symbol = data.get("symbol")
    entry = data.get("entry")
    tp1 = data.get("TP1")
    tp2 = data.get("TP2")
    tp3 = data.get("TP3")
    sl = data.get("SL")

    if action and symbol:
        msg = f"💎 *VIP Trade Signal* 💎\n\n"
        msg += f"Asset: `{symbol}`\n"
        msg += f"Direction: *{action}*\n"
        msg += f"Entry: `{entry}`\n"
        msg += f"TP1: `{tp1}`\n"
        msg += f"TP2: `{tp2}`\n"
        msg += f"TP3: `{tp3}`\n"
        msg += f"SL: `{sl}`\n\n"
        msg += "⚡ Good luck, Liquid Nation! ⚡"

        send_telegram(msg)
        return "Alert sent", 200
    else:
        return "Invalid data", 400

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
