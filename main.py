from flask import Flask, request
import requests

app = Flask(__name__)

# إعدادات البوت
BOT_TOKEN = "7975838878:AAEb26zn8MdDMD-ZzHDDFJTw8QrbPDo2kKI"
PRIVATE_CHANNEL_ID = "-1002757012569"  # قناة VIP الخاصة

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    signal_type = data.get("type", "UNKNOWN")
    ticker = data.get("ticker", "N/A")
    price = data.get("price", "N/A")

    message = f"🚨 توصية {signal_type}\nالسهم: {ticker}\nالسعر: {price}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": PRIVATE_CHANNEL_ID,
        "text": message
    }

    requests.post(url, json=payload)
    return 'OK', 200
