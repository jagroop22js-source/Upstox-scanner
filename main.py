import requests
import os
from flask import Flask
from datetime import datetime
import pandas as pd
import numpy as np

app = Flask(__name__)

TOKEN = os.environ.get("UPSTOX_TOKEN")
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def get_instrument_master():
    """Saare F&O instruments ki list"""
    url = "https://api.upstox.com/v2/instrument/type/FUT"
    r = requests.get(url, headers=headers)
    data = r.json()
    return data['data'] # list of dicts

def get_ltp(instrument_key):
    url = "https://api.upstox.com/v2/market-quote/ltp"
    r = requests.get(url, headers=headers, params={"instrument_key": instrument_key})
    data = r.json()
    key = list(data["data"].keys())[0]
    return float(data["data"][key]["last_price"])

def get_candle_rsi(instrument_key):
    """Last 30 candles se RSI 14"""
    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/1minute/30"
    r = requests.get(url, headers=headers)
    data = r.json()

    if 'data' not in data or not data['data']['candles']:
        return None

    candles = data['data']['candles']
    df = pd.DataFrame(candles, columns=['time','o','h','l','c','v','oi'])
    df['c'] = df['c'].astype(float)

    delta = df['c'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def scan_all_futures_rsi():
    results = []
    instruments = get_instrument_master()

    # Sirf NSE ke stocks le, expiry nearest wali
    seen_stocks = set()

    for inst in instruments:
        name = inst['name'] # RELIANCE, TCS etc
        exchange = inst['exchange']
        instrument_key = inst['instrument_key'] # NSE_FO|RELIANCE25MAYFUT

        if exchange!= 'NSE' or name in seen_stocks:
            continue

        seen_stocks.add(name)

        try:
            ltp = get_ltp(instrument_key)
            rsi = get_candle_rsi(instrument_key)

            if rsi is None:
                continue

            if rsi > 60:
                results.append(f"🚨 <b>{name}</b><br>Key: {instrument_key}<br>LTP: {ltp} | RSI: {rsi}<br><br>")

        except:
            continue

    return "".join(results) if results else "Abhi koi stock RSI 60 cross nahi kar raha"

@app.route("/")
def home():
    data = scan_all_futures_rsi()
    return f"<h3>All F&O Stocks ATM RSI > 60 Scanner</h3>Scan time: {datetime.now().strftime('%H:%M:%S')}<br><br>{data}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
