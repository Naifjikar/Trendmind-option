import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def capture_contract_screenshot(ticker, strike, expiry):
    os.makedirs("images", exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{ticker}_{timestamp}.png"
    path = os.path.join("images", filename)

    url = f"https://app.webull.com/options/{ticker}?strike={strike}&expiration={expiry}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # ينتظر 5 ثواني لتحميل الصفحة

        page.screenshot(path=path, full_page=False)
        browser.close()

    return path
