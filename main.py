from flask import Flask, request
import requests
from datetime import datetime
from screenshot import capture_contract_screenshot

app = Flask(__name__)

BOT_TOKEN = "7975838878:AAEb26zn8MdDMD-ZzHDDFJTw8QrbPDo2kKI"
PRIVATE_CHANNEL_ID = "-1002757012569"
PUBLIC_CHANNEL_ID = "-1002570389914"

contracts = {}

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    ticker = data.get("ticker", "N/A")
    price = float(data.get("price", 0))
    contract_type = data.get("type", "CALL").upper()

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
        "sent_targets": set()
    }

    message = f"""{ticker}
{contract_type}
نقطة الدخول: {price}
الوقف: كسر {stop_loss} بإغلاق شمعة 3 دقائق
الأهداف: 30% - 60% - 100%
"""

    image_path = capture_contract_screenshot(ticker, price)
    send_photo(PRIVATE_CHANNEL_ID, image_path, message)
    contracts[ticker]["screenshot_entry"] = image_path
    return "OK", 200

@app.route('/price_update', methods=['POST'])
def price_update():
    data = request.json
    ticker = data.get("ticker")
    current_price = float(data.get("price", 0))

    if ticker not in contracts:
        return "Contract not tracked", 200

    contract = contracts[ticker]
    updated = False

    if current_price > contract["high"]:
        contract["high"] = current_price

    for level, label in [("target1", "✅ تحقق الهدف الأول"), ("target2", "✅ تحقق الهدف الثاني"), ("target3", "✅ تحقق الهدف الثالث")]:
        if current_price >= contract[level] and level not in contract["sent_targets"]:
            img = capture_contract_screenshot(ticker, current_price)
            send_photo(PRIVATE_CHANNEL_ID, img, f"{ticker}\n{label}")
            contract["sent_targets"].add(level)
            updated = True

    if current_price >= contract["extra_trigger"] and "extra" not in contract["sent_targets"]:
        img = capture_contract_screenshot(ticker, current_price)
        send_photo(PRIVATE_CHANNEL_ID, img)
        contract["sent_targets"].add("extra")
        updated = True

    return "Updated" if updated else "No update", 200

@app.route('/daily_summary', methods=['GET'])
def daily_summary():
    if not contracts:
        return "No contracts today", 200

    best = max(contracts.items(), key=lambda x: x[1]["high"] / x[1]["entry"])
    ticker, data = best
    entry = data["entry"]
    high = data["high"]
    percent = round((high - entry) / entry * 100, 2)

    caption = f"""{ticker} - {data['type']}
نقطة الدخول: {entry}
أعلى سعر: {high}
نسبة الربح: {percent}% 💰
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(data["screenshot_entry"], 'rb') as photo:
        for channel in [PRIVATE_CHANNEL_ID, PUBLIC_CHANNEL_ID]:
            requests.post(url, data={"chat_id": channel, "caption": caption}, files={"photo": photo})

    return "Summary sent", 200

def send_photo(chat_id, image_path, caption=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as photo:
        requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": photo})
