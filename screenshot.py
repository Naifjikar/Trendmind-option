import os
from datetime import datetime
from PIL import Image, ImageDraw

def capture_contract_screenshot(ticker, price):
    os.makedirs("images", exist_ok=True)
    path = f"images/{ticker}_{datetime.now().strftime('%H%M%S')}.png"
    img = Image.new('RGB', (400, 200), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((10, 80), f"{ticker} - ${price}", fill=(255, 255, 255))
    img.save(path)
    return path
