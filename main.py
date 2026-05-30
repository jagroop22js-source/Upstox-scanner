import requests
import os
import time

TOKEN = os.environ.get("UPSTOX_TOKEN")

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

symbols = [
    "NSE_INDEX|Nifty 50",
    "NSE_INDEX|Nifty Bank",
    "NSE_INDEX|Nifty Fin Service",
    "NSE_INDEX|Nifty Midcap Select"
]

while True:
    print("=" * 40)

    for symbol in symbols:
        url = "https://api.upstox.com/v2/market-quote/ltp"
        r = requests.get(
            url,
            headers=headers,
            params={"instrument_key": symbol}
        )

        data = r.json()

        try:
            key = list(data["data"].keys())[0]
            price = data["data"][key]["last_price"]

            print(f"{symbol}")
            print(f"Price = {price}")
            print("-" * 30)

        except Exception as e:
            print(symbol, "ERROR")

    time.sleep(60)
