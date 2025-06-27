from flask import Flask, request
from telegram import Bot
from datetime import datetime
import os
from screenshot import capture_contract_screenshot  # تأكد أن هذا الملف موجود بنفس المجلد

app = Flask(__name__)

BOT_TOKEN = "7975838878:AAEb26zn8MdDMD-ZzHDDFJTw8QrbPDo2kKI"
PRIVATE_CHANNEL_ID = "-1002757012569"
PUBLIC_CHANNEL_ID = "-1002570389914"

bot = Bot(token=BOT_TOKEN)
contracts = {}

def send_photo(chat_id, image_path, caption):
    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    ticker = data.get("ticker", "N/A")
    price = float(data.get("price", 0))
    contract_type = data.get("type", "CALL").upper()
    strike = data.get("strike", "N/A")
    expiry = data.get("expiry", "N/A")

    target1 = round(price * 1.3, 2)
    target2 = round(price * 1.6, 2)
    target3 = round(price * 2.0, 2)
    extra_trigger = round(target3 + 0.5, 2)
    stop_loss = round(price - 0.45, 2)

    contracts[ticker] = {
        "entry": price,
        "target1": target1,
        "target2": target2,
        "target3": target3,
        "extra_trigger": extra_trigger,
        "high": price,
        "type": contract_type,
        "strike": strike,
        "expiry": expiry,
        "sent_targets": set()
    }

    message = f"""{ticker} - {contract_type}
Strike: {strike}
Expiry: {expiry}

📥 دخول: {price}
⛔️ وقف: {stop_loss}
🎯 أهداف:
- {target1}
- {target2}
- {target3}
"""

    image_path = capture_contract_screenshot(ticker, strike, expiry)
    send_photo(PRIVATE_CHANNEL_ID, image_path, message)
    contracts[ticker]["screenshot_entry"] = image_path

    return "OK", 200

# للتشغيل المحلي فقط (اختياري)
if __name__ == "__main__":
    app.run(debug=True)
