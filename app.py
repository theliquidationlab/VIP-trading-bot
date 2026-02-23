import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Load environment variables from Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_telegram(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram error:", e)


@app.route("/")
def home():
    return "Liquidity Labs Bot Running", 200


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
        message = (
            f"💎 *VIP Trade Signal* 💎\n\n"
            f"Asset: `{symbol}`\n"
            f"Direction: *{action}*\n"
            f"Entry: `{entry}`\n"
            f"TP1: `{tp1}`\n"
            f"TP2: `{tp2}`\n"
            f"TP3: `{tp3}`\n"
            f"SL: `{sl}`\n\n"
            f"⚡ Liquidation Labs VIP ⚡"
        )

        send_telegram(message)
        return "Alert sent", 200

    return "Invalid data", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
