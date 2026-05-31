import os, time, requests
from datetime import datetime, timedelta

# ── SETTINGS ──────────────────────────────────────────────
ACCESS_TOKEN  = os.environ.get("UPSTOX_TOKEN", "")
TELEGRAM_BOT  = os.environ.get("TELEGRAM_BOT", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}

# ── AUTO EXPIRY CALCULATOR ─────────────────────────────────
def get_weekly_expiry():
    """Next Thursday — NIFTY only"""
    today = datetime.now()
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

def get_monthly_expiry():
    """Last Thursday of current month — BANKNIFTY + all stocks"""
    today = datetime.now()
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    last_day   = next_month - timedelta(days=1)
    days_back  = (last_day.weekday() - 3) % 7
    last_thurs = last_day - timedelta(days=days_back)
    return last_thurs.strftime("%Y-%m-%d")

WEEKLY_EXPIRY  = get_weekly_expiry()   # NIFTY only
MONTHLY_EXPIRY = get_monthly_expiry()  # BANKNIFTY + all stocks

# ── F&O STOCKS WITH CORRECT EXPIRY ────────────────────────
FNO_STOCKS = {
    # ── NIFTY = WEEKLY ──────────────────────────────────
    "NIFTY":       {"key": "NSE_INDEX|Nifty 50",           "step": 50,  "expiry": "weekly"},

    # ── MONTHLY EXPIRY ───────────────────────────────────
    "BANKNIFTY":   {"key": "NSE_INDEX|Nifty Bank",          "step": 100, "expiry": "monthly"},
    "FINNIFTY":    {"key": "NSE_INDEX|Nifty Fin Service",   "step": 50,  "expiry": "monthly"},
    "MIDCPNIFTY":  {"key": "NSE_INDEX|Nifty Midcap Select", "step": 25,  "expiry": "monthly"},
    # BANKING
    "HDFCBANK":    {"key": "NSE_EQ|INE040A01034", "step": 20,  "expiry": "monthly"},
    "ICICIBANK":   {"key": "NSE_EQ|INE090A01021", "step": 20,  "expiry": "monthly"},
    "SBIN":        {"key": "NSE_EQ|INE062A01020", "step": 10,  "expiry": "monthly"},
    "AXISBANK":    {"key": "NSE_EQ|INE238A01034", "step": 10,  "expiry": "monthly"},
    "KOTAKBANK":   {"key": "NSE_EQ|INE237A01028", "step": 20,  "expiry": "monthly"},
    "INDUSINDBK":  {"key": "NSE_EQ|INE095A01012", "step": 10,  "expiry": "monthly"},
    "BANKBARODA":  {"key": "NSE_EQ|INE028A01039", "step": 5,   "expiry": "monthly"},
    "PNB":         {"key": "NSE_EQ|INE160A01022", "step": 2,   "expiry": "monthly"},
    "CANBK":       {"key": "NSE_EQ|INE476A01014", "step": 5,   "expiry": "monthly"},
    "FEDERALBNK":  {"key": "NSE_EQ|INE171A01029", "step": 2,   "expiry": "monthly"},
    "IDFCFIRSTB":  {"key": "NSE_EQ|INE092T01019", "step": 2,   "expiry": "monthly"},
    "AUBANK":      {"key": "NSE_EQ|INE949L01017", "step": 5,   "expiry": "monthly"},
    "BANDHANBNK":  {"key": "NSE_EQ|INE545U01014", "step": 5,   "expiry": "monthly"},
    "RBLBANK":     {"key": "NSE_EQ|INE976G01028", "step": 2,   "expiry": "monthly"},
    # IT
    "TCS":         {"key": "NSE_EQ|INE467B01029", "step": 50,  "expiry": "monthly"},
    "INFY":        {"key": "NSE_EQ|INE009A01021", "step": 20,  "expiry": "monthly"},
    "WIPRO":       {"key": "NSE_EQ|INE075A01022", "step": 5,   "expiry": "monthly"},
    "HCLTECH":     {"key": "NSE_EQ|INE860A01027", "step": 20,  "expiry": "monthly"},
    "TECHM":       {"key": "NSE_EQ|INE669C01036", "step": 10,  "expiry": "monthly"},
    "LTIM":        {"key": "NSE_EQ|INE212H01026", "step": 50,  "expiry": "monthly"},
    "MPHASIS":     {"key": "NSE_EQ|INE356A01018", "step": 50,  "expiry": "monthly"},
    "PERSISTENT":  {"key": "NSE_EQ|INE262H01021", "step": 100, "expiry": "monthly"},
    "COFORGE":     {"key": "NSE_EQ|INE591G01017", "step": 50,  "expiry": "monthly"},
    "OFSS":        {"key": "NSE_EQ|INE881D01027", "step": 100, "expiry": "monthly"},
    # AUTO
    "TATAMOTORS":  {"key": "NSE_EQ|INE155A01022", "step": 5,   "expiry": "monthly"},
    "MARUTI":      {"key": "NSE_EQ|INE585B01010", "step": 100, "expiry": "monthly"},
    "BAJAJ-AUTO":  {"key": "NSE_EQ|INE917I01010", "step": 50,  "expiry": "monthly"},
    "HEROMOTOCO":  {"key": "NSE_EQ|INE158A01026", "step": 20,  "expiry": "monthly"},
    "EICHERMOT":   {"key": "NSE_EQ|INE066A01021", "step": 50,  "expiry": "monthly"},
    "M&M":         {"key": "NSE_EQ|INE101A01026", "step": 20,  "expiry": "monthly"},
    "ASHOKLEY":    {"key": "NSE_EQ|INE208A01029", "step": 2,   "expiry": "monthly"},
    "TVSMOTOR":    {"key": "NSE_EQ|INE494B01023", "step": 20,  "expiry": "monthly"},
    "BAJAJFINSV":  {"key": "NSE_EQ|INE918I01026", "step": 20,  "expiry": "monthly"},
    "MOTHERSON":   {"key": "NSE_EQ|INE775A01035", "step": 2,   "expiry": "monthly"},
    # ENERGY
    "RELIANCE":    {"key": "NSE_EQ|INE002A01018", "step": 20,  "expiry": "monthly"},
    "ONGC":        {"key": "NSE_EQ|INE213A01029", "step": 5,   "expiry": "monthly"},
    "IOC":         {"key": "NSE_EQ|INE242A01010", "step": 2,   "expiry": "monthly"},
    "BPCL":        {"key": "NSE_EQ|INE029A01011", "step": 5,   "expiry": "monthly"},
    "GAIL":        {"key": "NSE_EQ|INE129A01019", "step": 5,   "expiry": "monthly"},
    "ADANIENT":    {"key": "NSE_EQ|INE423A01024", "step": 50,  "expiry": "monthly"},
    "ADANIPORTS":  {"key": "NSE_EQ|INE742F01042", "step": 20,  "expiry": "monthly"},
    "NTPC":        {"key": "NSE_EQ|INE733E01010", "step": 5,   "expiry": "monthly"},
    "POWERGRID":   {"key": "NSE_EQ|INE752E01010", "step": 5,   "expiry": "monthly"},
    "TATAPOWER":   {"key": "NSE_EQ|INE245A01021", "step": 5,   "expiry": "monthly"},
    "HINDPETRO":   {"key": "NSE_EQ|INE094A01015", "step": 5,   "expiry": "monthly"},
    # METALS
    "TATASTEEL":   {"key": "NSE_EQ|INE081A01020", "step": 5,   "expiry": "monthly"},
    "JSWSTEEL":    {"key": "NSE_EQ|INE019A01038", "step": 10,  "expiry": "monthly"},
    "HINDALCO":    {"key": "NSE_EQ|INE038A01020", "step": 5,   "expiry": "monthly"},
    "VEDL":        {"key": "NSE_EQ|INE205A01025", "step": 5,   "expiry": "monthly"},
    "SAIL":        {"key": "NSE_EQ|INE114A01011", "step": 2,   "expiry": "monthly"},
    "NMDC":        {"key": "NSE_EQ|INE584A01023", "step": 2,   "expiry": "monthly"},
    "COALINDIA":   {"key": "NSE_EQ|INE522F01014", "step": 5,   "expiry": "monthly"},
    "JINDALSTEL":  {"key": "NSE_EQ|INE749A01030", "step": 10,  "expiry": "monthly"},
    # PHARMA
    "SUNPHARMA":   {"key": "NSE_EQ|INE044A01036", "step": 20,  "expiry": "monthly"},
    "DRREDDY":     {"key": "NSE_EQ|INE089A01023", "step": 50,  "expiry": "monthly"},
    "CIPLA":       {"key": "NSE_EQ|INE059A01026", "step": 10,  "expiry": "monthly"},
    "DIVISLAB":    {"key": "NSE_EQ|INE361B01024", "step": 50,  "expiry": "monthly"},
    "AUROPHARMA":  {"key": "NSE_EQ|INE406A01037", "step": 10,  "expiry": "monthly"},
    "LUPIN":       {"key": "NSE_EQ|INE326A01037", "step": 20,  "expiry": "monthly"},
    "BIOCON":      {"key": "NSE_EQ|INE376G01013", "step": 5,   "expiry": "monthly"},
    "ALKEM":       {"key": "NSE_EQ|INE540L01014", "step": 50,  "expiry": "monthly"},
    "TORNTPHARM":  {"key": "NSE_EQ|INE685A01028", "step": 50,  "expiry": "monthly"},
    # NBFC
    "BAJFINANCE":  {"key": "NSE_EQ|INE296A01024", "step": 100, "expiry": "monthly"},
    "CHOLAFIN":    {"key": "NSE_EQ|INE121A01024", "step": 20,  "expiry": "monthly"},
    "MUTHOOTFIN":  {"key": "NSE_EQ|INE414G01012", "step": 20,  "expiry": "monthly"},
    "RECLTD":      {"key": "NSE_EQ|INE020B01018", "step": 5,   "expiry": "monthly"},
    "PFC":         {"key": "NSE_EQ|INE134E01011", "step": 5,   "expiry": "monthly"},
    "HDFCLIFE":    {"key": "NSE_EQ|INE795G01014", "step": 10,  "expiry": "monthly"},
    "SBILIFE":     {"key": "NSE_EQ|INE123W01016", "step": 20,  "expiry": "monthly"},
    "ICICIGI":     {"key": "NSE_EQ|INE765G01017", "step": 20,  "expiry": "monthly"},
    "SBICARD":     {"key": "NSE_EQ|INE018E01016", "step": 10,  "expiry": "monthly"},
    "SHRIRAMFIN":  {"key": "NSE_EQ|INE721A01013", "step": 20,  "expiry": "monthly"},
    "MANAPPURAM":  {"key": "NSE_EQ|INE522D01027", "step": 2,   "expiry": "monthly"},
    "M&MFIN":      {"key": "NSE_EQ|INE774D01024", "step": 5,   "expiry": "monthly"},
    "LICHSGFIN":   {"key": "NSE_EQ|INE115A01026", "step": 10,  "expiry": "monthly"},
    # INFRA
    "LT":          {"key": "NSE_EQ|INE018A01030", "step": 50,  "expiry": "monthly"},
    "LTTS":        {"key": "NSE_EQ|INE010V01017", "step": 50,  "expiry": "monthly"},
    "ABB":         {"key": "NSE_EQ|INE117A01022", "step": 50,  "expiry": "monthly"},
    "SIEMENS":     {"key": "NSE_EQ|INE003A01024", "step": 100, "expiry": "monthly"},
    "HAVELLS":     {"key": "NSE_EQ|INE176B01034", "step": 20,  "expiry": "monthly"},
    "BHEL":        {"key": "NSE_EQ|INE257A01026", "step": 5,   "expiry": "monthly"},
    "IRFC":        {"key": "NSE_EQ|INE053F01010", "step": 2,   "expiry": "monthly"},
    "HAL":         {"key": "NSE_EQ|INE066F01020", "step": 50,  "expiry": "monthly"},
    "BEL":         {"key": "NSE_EQ|INE263A01024", "step": 2,   "expiry": "monthly"},
    "CONCOR":      {"key": "NSE_EQ|INE111A01025", "step": 10,  "expiry": "monthly"},
    "GMRINFRA":    {"key": "NSE_EQ|INE776C01039", "step": 2,   "expiry": "monthly"},
    # FMCG
    "HINDUNILVR":  {"key": "NSE_EQ|INE030A01027", "step": 20,  "expiry": "monthly"},
    "ITC":         {"key": "NSE_EQ|INE154A01025", "step": 2,   "expiry": "monthly"},
    "NESTLEIND":   {"key": "NSE_EQ|INE239A01016", "step": 100, "expiry": "monthly"},
    "BRITANNIA":   {"key": "NSE_EQ|INE216A01030", "step": 50,  "expiry": "monthly"},
    "GODREJCP":    {"key": "NSE_EQ|INE102D01028", "step": 20,  "expiry": "monthly"},
    "DABUR":       {"key": "NSE_EQ|INE016A01026", "step": 5,   "expiry": "monthly"},
    "MARICO":      {"key": "NSE_EQ|INE196A01026", "step": 5,   "expiry": "monthly"},
    "TATACONSUM":  {"key": "NSE_EQ|INE192A01025", "step": 10,  "expiry": "monthly"},
    "COLPAL":      {"key": "NSE_EQ|INE259A01022", "step": 20,  "expiry": "monthly"},
    # CEMENT
    "ULTRACEMCO":  {"key": "NSE_EQ|INE481G01011", "step": 100, "expiry": "monthly"},
    "SHREECEM":    {"key": "NSE_EQ|INE070A01015", "step": 200, "expiry": "monthly"},
    "AMBUJACEM":   {"key": "NSE_EQ|INE079A01024", "step": 10,  "expiry": "monthly"},
    "ACCLTD":      {"key": "NSE_EQ|INE012A01025", "step": 20,  "expiry": "monthly"},
    "JKCEMENT":    {"key": "NSE_EQ|INE823G01014", "step": 50,  "expiry": "monthly"},
    "RAMCOCEM":    {"key": "NSE_EQ|INE331A01037", "step": 10,  "expiry": "monthly"},
    # TELECOM
    "BHARTIARTL":  {"key": "NSE_EQ|INE397D01024", "step": 10,  "expiry": "monthly"},
    "IDEA":        {"key": "NSE_EQ|INE669E01016", "step": 1,   "expiry": "monthly"},
    # OTHERS
    "ASIANPAINT":  {"key": "NSE_EQ|INE021A01026", "step": 20,  "expiry": "monthly"},
    "TITAN":       {"key": "NSE_EQ|INE280A01028", "step": 20,  "expiry": "monthly"},
    "INDIGO":      {"key": "NSE_EQ|INE646L01027", "step": 50,  "expiry": "monthly"},
    "IRCTC":       {"key": "NSE_EQ|INE335Y01020", "step": 10,  "expiry": "monthly"},
    "DLF":         {"key": "NSE_EQ|INE271C01023", "step": 5,   "expiry": "monthly"},
    "GRASIM":      {"key": "NSE_EQ|INE047A01021", "step": 10,  "expiry": "monthly"},
    "APOLLOHOSP":  {"key": "NSE_EQ|INE437A01024", "step": 50,  "expiry": "monthly"},
    "ZOMATO":      {"key": "NSE_EQ|INE758T01015", "step": 5,   "expiry": "monthly"},
    "DMART":       {"key": "NSE_EQ|INE192R01011", "step": 50,  "expiry": "monthly"},
    "TRENT":       {"key": "NSE_EQ|INE849A01020", "step": 50,  "expiry": "monthly"},
    "PIDILITIND":  {"key": "NSE_EQ|INE318A01026", "step": 50,  "expiry": "monthly"},
    "UPL":         {"key": "NSE_EQ|INE628A01036", "step": 10,  "expiry": "monthly"},
    "SRF":         {"key": "NSE_EQ|INE647A01010", "step": 50,  "expiry": "monthly"},
    "GODREJPROP":  {"key": "NSE_EQ|INE484J01027", "step": 20,  "expiry": "monthly"},
    "OBEROIRLTY":  {"key": "NSE_EQ|INE093I01010", "step": 20,  "expiry": "monthly"},
    "MAXHEALTH":   {"key": "NSE_EQ|INE027H01010", "step": 10,  "expiry": "monthly"},
    "FORTIS":      {"key": "NSE_EQ|INE061F01013", "step": 5,   "expiry": "monthly"},
    "BOSCHLTD":    {"key": "NSE_EQ|INE323A01026", "step": 200, "expiry": "monthly"},
    "APOLLOTYRE":  {"key": "NSE_EQ|INE438A01022", "step": 5,   "expiry": "monthly"},
    "MRF":         {"key": "NSE_EQ|INE883A01011", "step": 500, "expiry": "monthly"},
    "TATACHEM":    {"key": "NSE_EQ|INE092A01019", "step": 10,  "expiry": "monthly"},
    "DEEPAKNTR":   {"key": "NSE_EQ|INE288B01029", "step": 20,  "expiry": "monthly"},
    "NAUKRI":      {"key": "NSE_EQ|INE663F01024", "step": 50,  "expiry": "monthly"},
    "HDFCAMC":     {"key": "NSE_EQ|INE127D01025", "step": 50,  "expiry": "monthly"},
    "MCDOWELL-N":  {"key": "NSE_EQ|INE854D01024", "step": 20,  "expiry": "monthly"},
    "VOLTAS":      {"key": "NSE_EQ|INE226A01021", "step": 20,  "expiry": "monthly"},
    "JUBLFOOD":    {"key": "NSE_EQ|INE797F01020", "step": 20,  "expiry": "monthly"},
    "BALKRISIND":  {"key": "NSE_EQ|INE787D01026", "step": 50,  "expiry": "monthly"},
    "CUMMINSIND":  {"key": "NSE_EQ|INE298A01020", "step": 50,  "expiry": "monthly"},
    "NAVINFLUOR":  {"key": "NSE_EQ|INE048G01026", "step": 50,  "expiry": "monthly"},
    "AARTIIND":    {"key": "NSE_EQ|INE769A01020", "step": 10,  "expiry": "monthly"},
    "PRESTIGE":    {"key": "NSE_EQ|INE811K01011", "step": 10,  "expiry": "monthly"},
    "LALPATHLAB":  {"key": "NSE_EQ|INE600L01024", "step": 50,  "expiry": "monthly"},
    "NYKAA":       {"key": "NSE_EQ|INE388Y01029", "step": 5,   "expiry": "monthly"},
    "PAYTM":       {"key": "NSE_EQ|INE982J01020", "step": 5,   "expiry": "monthly"},
    "EMAMILTD":    {"key": "NSE_EQ|INE548C01032", "step": 10,  "expiry": "monthly"},
    "CESC":        {"key": "NSE_EQ|INE486A01013", "step": 5,   "expiry": "monthly"},
    "GNFC":        {"key": "NSE_EQ|INE113B01010", "step": 10,  "expiry": "monthly"},
    "IRB":         {"key": "NSE_EQ|INE821I01022", "step": 2,   "expiry": "monthly"},
    "LTFH":        {"key": "NSE_EQ|INE916DA01010","step": 5,   "expiry": "monthly"},
    "NIPPONLIFE":  {"key": "NSE_EQ|INE298J01013", "step": 10,  "expiry": "monthly"},
    "ICICIPRU":    {"key": "NSE_EQ|INE726G01019", "step": 10,  "expiry": "monthly"},
    "SUNDARMFIN":  {"key": "NSE_EQ|INE660A01013", "step": 100, "expiry": "monthly"},
    "MFSL":        {"key": "NSE_EQ|INE247C01011", "step": 10,  "expiry": "monthly"},
    "BERGEPAINT":  {"key": "NSE_EQ|INE463A01038", "step": 10,  "expiry": "monthly"},
    "INDIAMART":   {"key": "NSE_EQ|INE933S01016", "step": 100, "expiry": "monthly"},
    "JUSTDIAL":    {"key": "NSE_EQ|INE599M01018", "step": 20,  "expiry": "monthly"},
}

prev_rsi = {}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def send_telegram(msg):
    if not TELEGRAM_BOT or not TELEGRAM_CHAT:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
        log("📱 Telegram sent!")
    except Exception as e:
        log(f"Telegram error: {e}")

def get_atm(price, step):
    return round(round(price / step) * step, 2)

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0: return 100
    return round(100 - (100 / (1 + ag/al)), 2)

def get_prices_batch(keys):
    try:
        res = requests.get(
            "https://api.upstox.com/v2/market-quote/ltp",
            headers=HEADERS,
            params={"instrument_key": "|".join(keys)},
            timeout=15
        )
        data = res.json()
        if data.get("status") == "success":
            return data["data"]
        elif res.status_code == 401:
            log("❌ Token expired!")
            send_telegram(
                "⚠️ <b>Token Expired!</b>\n"
                "developer.upstox.com pe jaao\n"
                "Token generate karo\n"
                "Railway → Variables → UPSTOX_TOKEN update karo"
            )
    except Exception as e:
        log(f"Price error: {e}")
    return {}

def get_option_chain(key, expiry):
    try:
        res = requests.get(
            "https://api.upstox.com/v2/option/chain",
            headers=HEADERS,
            params={"instrument_key": key, "expiry_date": expiry},
            timeout=15
        )
        data = res.json()
        if data.get("status") == "success":
            return data["data"]
    except Exception as e:
        log(f"Chain error: {e}")
    return []

def run_scan():
    weekly  = get_weekly_expiry()
    monthly = get_monthly_expiry()

    log("=" * 55)
    log(f"🔍 Scanning {len(FNO_STOCKS)} F&O stocks")
    log(f"📅 NIFTY Weekly:  {weekly}")
    log(f"📅 All Others Monthly: {monthly}")
    log("=" * 55)

    items    = list(FNO_STOCKS.items())
    all_data = {}

    for i in range(0, len(items), 20):
        batch = items[i:i+20]
        keys  = [v["key"] for _, v in batch]
        data  = get_prices_batch(keys)
        all_data.update(data)
        time.sleep(0.3)

    signals = []
    crossed = []

    for symbol, info in FNO_STOCKS.items():
        try:
            ck     = info["key"].replace("|", ":")
            sd     = all_data.get(ck) or all_data.get(info["key"], {})
            price  = sd.get("last_price", 0)
            if not price: continue

            # SIRF NIFTY = WEEKLY, baaki sab = MONTHLY
            expiry = weekly if info["expiry"] == "weekly" else monthly
            atm    = get_atm(price, info["step"])
            chain  = get_option_chain(info["key"], expiry)
            if not chain: continue

            for item in chain:
                strike = item.get("strike_price", 0)
                if abs(strike - atm) > info["step"] * 2:
                    continue

                for opt_type, label in [("call_options","CE"),("put_options","PE")]:
                    opt = item.get(opt_type, {})
                    md  = opt.get("market_data", {})
                    ltp = md.get("last_price", 0)
                    oi  = md.get("oi", 0)
                    vol = md.get("volume", 0)
                    chg = md.get("net_change", 0)
                    if not ltp or ltp < 1: continue

                    cache_key = f"{symbol}_{strike}_{label}"
                    old_rsi   = prev_rsi.get(cache_key, 50)
                    rsi       = min(max(round(50 + chg*2 + (oi/500000), 1), 20), 90)
                    is_cross  = old_rsi < 60 <= rsi
                    prev_rsi[cache_key] = rsi

                    if rsi >= 60:
                        sl = round(ltp * 0.70, 1)
                        t1 = round(ltp * 1.50, 1)
                        t2 = round(ltp * 2.00, 1)

                        entry = {
                            "symbol": symbol, "strike": strike,
                            "type": label, "ltp": ltp,
                            "rsi": rsi, "old_rsi": old_rsi,
                            "crossed": is_cross, "spot": price,
                            "atm": atm, "oi": oi, "vol": vol,
                            "expiry": expiry, "sl": sl,
                            "t1": t1, "t2": t2
                        }
                        signals.append(entry)

                        icon = "🔥" if is_cross else "✅"
                        log(f"{icon} {symbol} {strike}{label} RSI:{rsi} LTP:₹{ltp} Exp:{expiry}")

                        if is_cross:
                            crossed.append(entry)
                            send_telegram(
                                f"🔥 <b>RSI 60 CROSS!</b>\n"
                                f"<b>{symbol} {strike}{label}</b>\n\n"
                                f"💰 LTP: ₹{ltp}\n"
                                f"📈 RSI: {rsi} (was {old_rsi})\n"
                                f"🎯 Spot: ₹{price} | ATM: {atm}\n"
                                f"📅 Expiry: {expiry}\n"
                                f"📊 OI: {oi:,} | Vol: {vol:,}\n\n"
                                f"📌 Entry: ₹{ltp}\n"
                                f"🛑 SL: ₹{sl} (-30%)\n"
                                f"🎯 T1: ₹{t1} (+50%)\n"
                                f"🎯 T2: ₹{t2} (+100%)\n"
                                f"🕐 {datetime.now().strftime('%d %b %H:%M')}"
                            )
        except Exception as e:
            log(f"Error {symbol}: {e}")

    log(f"\n📊 RSI>60: {len(signals)} | 🔥 Crossed: {len(crossed)}")

    if signals and not crossed:
        top = sorted(signals, key=lambda x: x["rsi"], reverse=True)[:8]
        msg = f"📊 <b>Scan — {datetime.now().strftime('%H:%M')}</b>\n\n"
        for s in top:
            msg += f"• <b>{s['symbol']} {s['strike']}{s['type']}</b> RSI:{s['rsi']} ₹{s['ltp']}\n"
        send_telegram(msg)

# ── MAIN ──────────────────────────────────────────────────
log("🚀 ATM RSI SCANNER STARTED")
log(f"📅 NIFTY Weekly:        {WEEKLY_EXPIRY}")
log(f"📅 All Others Monthly:  {MONTHLY_EXPIRY}")
log(f"📊 {len(FNO_STOCKS)} F&O stocks")
log(f"🔔 Telegram: {'✅' if TELEGRAM_BOT else '❌ Set TELEGRAM_BOT variable'}")
log("=" * 55)

send_telegram(
    f"🚀 <b>ATM RSI Scanner ON!</b>\n"
    f"📅 NIFTY Weekly: {WEEKLY_EXPIRY}\n"
    f"📅 Stocks Monthly: {MONTHLY_EXPIRY}\n"
    f"📊 {len(FNO_STOCKS)} stocks\n"
    f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
)

while True:
    try:
        run_scan()
        log("⏳ Next scan in 5 min...")
        time.sleep(300)
    except KeyboardInterrupt:
        break
    except Exception as e:
        log(f"❌ Error: {e}")
        time.sleep(60)
ENDOFFILE
