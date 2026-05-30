import requests
import os
from flask import Flask
from datetime import datetime
import numpy as np

app = Flask(__name__)

TOKEN = os.environ.get("UPSTOX_TOKEN")
headers = {"Accept": "application/json", "Authorization": f"Bearer {TOKEN}"}

def get_ltp(instrument_key):
    url = "https://api.upstox.com/v2/market-quote/ltp"
    r = requests.get(url, headers=headers, params={"instrument_key": instrument_key})
    data = r.json()
    key = list(data["data"].keys())[0]
    return float(data["data"][key]["last_price"])

def rsi_calc(closes, period=14):
    """Numpy nal RSI calculate"""
    closes = np.array(closes, dtype=float)
    deltas = np.diff(closes)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down!= 0 else 100
    rsi = np.zeros_like(closes)
    rsi[:period] = 100. - 100./(1.+rs)

    for i in range(period, len(closes)):
        delta = deltas[i-1]
        upval = delta if delta > 0 else 0.
        downval = -delta if delta < 0 else 0.
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down if down!= 0 else 100
        rsi[i] = 100. - 100./(1.+rs)
    return round(rsi[-1], 2)

def get_rsi(instrument_key):
    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/1minute/30"
    r = requests.get(url, headers=headers)
    data = r.json()
    if 'data' not in data or not data['data']['candles']:
        return None
    closes = [c[4] for c in data['data']['candles']] # close price index 4
    if len(closes) < 15:
        return None
    return rsi_calc(closes)

def get_nearest_expiry(stock_name):
    url = "https://api.upstox.com/v2/option/contract"
    params = {"instrument_key": f"NSE_EQ|{stock_name}"}
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    if 'data' not in data or not data['data']:
        return None
    expiries = sorted([i['expiry'] for i in data['data']])
    dt = datetime.strptime(expiries[0], "%Y-%m-%d")
    return dt.strftime("%y%b%d").upper()

def get_atm_option_key(stock_name, spot_price):
    step = 5
    if "NIFTY" in stock_name:
        step = 50
    elif "BANKNIFTY" in stock_name or "FINNIFTY" in stock_name:
        step = 100

    atm = round(spot_price / step) * step
    expiry = get_nearest_expiry(stock_name)
    if not expiry:
        return None, None
    option_key = f"NSE_FO|{stock_name}{expiry}{atm}CE"
    return option_key, atm

def scan_all
