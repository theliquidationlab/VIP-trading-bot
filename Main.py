# main.py
from flask import Flask, request
import requests
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import os

# ------------------- CONFIG -------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8271119506:AAEjWJtR4qElqLfCl7Die1Marbo1UiRSurw")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")  # Replace with your chat ID

MT5_PATH = os.environ.get("MT5_PATH", "C:\\Program Files\\MetaTrader 5\\terminal64.exe")
MT5_ACCOUNT = int(os.environ.get("MT5_ACCOUNT", "12345678"))
MT5_PASSWORD = os.environ.get("MT5_PASSWORD", "password")
MT5_SERVER = os.environ.get("MT5_SERVER", "BrokerServer")

LOT_SIZE = 0.1

TP1_PIPS = 20
TP2_PIPS = 40
TP3_PIPS = 60
SL_PIPS = 50

TRAILING_STOP_ACTIVE = True
TRAILING_STOP_PIPS = 15

# ------------------- INITIALIZE -----------------
app = Flask(__name__)
if not mt5.initialize(path=MT5_PATH):
    print("MT5 initialize() failed")
    mt5.shutdown()
else:
    mt5.login(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER)
    print("MT5 connected!")

trade_log = pd.DataFrame(columns=["asset","direction","entry","SL","TP1","TP2","TP3","status","pips"])

# ------------------- FUNCTIONS -----------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    requests.get(url)

def pips_to_price(symbol, pips):
    tick = mt5.symbol_info(symbol).point
    return pips * tick

def calculate_tp_sl(symbol, entry, direction):
    if direction.upper() == "BUY":
        tp1 = entry + pips_to_price(symbol, TP1_PIPS)
        tp2 = entry + pips_to_price(symbol, TP2_PIPS)
        tp3 = entry + pips_to_price(symbol, TP3_PIPS)
        sl = entry - pips_to_price(symbol, SL_PIPS)
    else:
        tp1 = entry - pips_to_price(symbol, TP1_PIPS)
        tp2 = entry - pips_to_price(symbol, TP2_PIPS)
        tp3 = entry - pips_to_price(symbol, TP3_PIPS)
        sl = entry + pips_to_price(symbol, SL_PIPS)
    return tp1, tp2, tp3, sl

def open_trade(symbol, direction, lot, entry_price):
    tp1, tp2, tp3, sl = calculate_tp_sl(symbol, entry_price, direction)
    order_type = mt5.ORDER_TYPE_BUY if direction.upper() == "BUY" else mt5.ORDER_TYPE_SELL
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp3,
        "deviation": 20,
        "magic": 123456,
        "comment": "VIP Bot"
    }
    
    result = mt5.order_send(request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        send_telegram(f"💰 Trade executed: {symbol} {direction}\nEntry: {entry_price}\nTP1:{tp1} TP2:{tp2} TP3:{tp3}\nSL:{sl}")
        trade_log.loc[len(trade_log)] = [symbol, direction, entry_price, sl, tp1, tp2, tp3, "OPEN", 0]
    else:
        send_telegram(f"❌ Trade failed: {result.comment}")

# ------------------- WEBHOOK -------------------
@app.route('/')
def home():
    return "VIP Bot Running"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    symbol = data.get("asset")
    direction = data.get("direction")
    entry_price = data.get("price", 0)
    lot = data.get("lot", LOT_SIZE)
    
    open_trade(symbol, direction, lot, entry_price)
    return "ok", 200

# ------------------- RUN SERVER -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
