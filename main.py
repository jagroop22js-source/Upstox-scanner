import os
import time
import requests
from datetime import datetime

UPSTOX_TOKEN = os.getenv("UPSTOX_TOKEN")
TELEGRAM_BOT = os.getenv("TELEGRAM_BOT")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT")

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_TOKEN}"
}

STOCKS = {
    "NIFTY":"NSE_INDEX|Nifty 50",
    "BANKNIFTY":"NSE_INDEX|Nifty Bank",
    "FINNIFTY":"NSE_INDEX|Nifty Fin Service",
    "MIDCPNIFTY":"NSE_INDEX|Nifty Midcap Select",
    "RELIANCE":"NSE_EQ|INE002A01018",
    "HDFCBANK":"NSE_EQ|INE040A01034",
    "ICICIBANK":"NSE_EQ|INE090A01021",
    "SBIN":"NSE_EQ|INE062A01020",
    "INFY":"NSE_EQ|INE009A01021",
    "TCS":"NSE_EQ|INE467B01029",
    "AXISBANK":"NSE_EQ|INE238A01034",
    "KOTAKBANK":"NSE_EQ|INE237A01028",
    "LT":"NSE_EQ|INE018A01030",
    "ITC":"NSE_EQ|INE154A01025",
    "BHARTIARTL":"NSE_EQ|INE397D01024",
    "TATAMOTORS":"NSE_EQ|INE155A01022"
}

last_prices = {}

def telegram(msg):
    if not TELEGRAM_BOT or not TELEGRAM_CHAT:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT,
                "text": msg
            },
            timeout=10
        )
    except:
        pass

def get_ltp(key):
    try:
        r = requests.get(
            "https://api.upstox.com/v2/market-quote/ltp",
            headers=HEADERS,
            params={"instrument_key": key},
            timeout=10
        )

        data = r.json()

        if data.get("status") != "success":
            return None

        first_key = list(data["data"].keys())[0]
        return data["data"][first_key]["last_price"]

    except:
        return None

telegram("🚀 Scanner Started")

while True:

    print("=" * 50)
    print(datetime.now())

    for symbol, key in STOCKS.items():

        price = get_ltp(key)

        if price is None:
            continue

        print(f"{symbol} = {price}")

        if symbol in last_prices:

            old = last_prices[symbol]

            change = ((price - old) / old) * 100

            if change >= 1:

                msg = (
                    f"🔥 BUY ALERT\n\n"
                    f"{symbol}\n"
                    f"Price: {price}\n"
                    f"Move: +{round(change,2)}%"
                )

                telegram(msg)

            elif change <= -1:

                msg = (
                    f"🔻 SELL ALERT\n\n"
                    f"{symbol}\n"
                    f"Price: {price}\n"
                    f"Move: {round(change,2)}%"
                )

                telegram(msg)

        last_prices[symbol] = price

    time.sleep(300)
