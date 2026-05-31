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
    """Next Thursday (NIFTY/BANKNIFTY weekly expiry)"""
    today = datetime.now()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead)
    return next_thursday.strftime("%Y-%m-%d")

def get_monthly_expiry():
    """Last Thursday of current month (stock monthly expiry)"""
    today = datetime.now()
    # Find last Thursday of month
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    last_day = next_month - timedelta(days=1)
    days_back = (last_day.weekday() - 3) % 7
    last_thursday = last_day - timedelta(days=days_back)
    return last_thursday.strftime("%Y-%m-%d")

WEEKLY_EXPIRY  = get_weekly_expiry()
MONTHLY_EXPIRY = get_monthly_expiry()

# ── STOCKS WITH EXPIRY TYPE ────────────────────────────────
FNO_STOCKS = {
    # INDICES — Weekly Expiry
    "NIFTY":       {"key": "NSE_INDEX|Nifty 50",           "step": 50,  "expiry": WEEKLY_EXPIRY},
    "BANKNIFTY":   {"key": "NSE_INDEX|Nifty Bank",          "step": 100, "expiry": WEEKLY_EXPIRY},
    "FINNIFTY":    {"key": "NSE_INDEX|Nifty Fin Service",   "step": 50,  "expiry": WEEKLY_EXPIRY},
    "MIDCPNIFTY":  {"key": "NSE_INDEX|Nifty Midcap Select", "step": 25,  "expiry": WEEKLY_EXPIRY},
    # BANKING — Monthly
    "HDFCBANK":    {"key": "NSE_EQ|INE040A01034", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "ICICIBANK":   {"key": "NSE_EQ|INE090A01021", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "SBIN":        {"key": "NSE_EQ|INE062A01020", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "AXISBANK":    {"key": "NSE_EQ|INE238A01034", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "KOTAKBANK":   {"key": "NSE_EQ|INE237A01028", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "INDUSINDBK":  {"key": "NSE_EQ|INE095A01012", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "BANKBARODA":  {"key": "NSE_EQ|INE028A01039", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "PNB":         {"key": "NSE_EQ|INE160A01022", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "CANBK":       {"key": "NSE_EQ|INE476A01014", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "FEDERALBNK":  {"key": "NSE_EQ|INE171A01029", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "IDFCFIRSTB":  {"key": "NSE_EQ|INE092T01019", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "AUBANK":      {"key": "NSE_EQ|INE949L01017", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "BANDHANBNK":  {"key": "NSE_EQ|INE545U01014", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "RBLBANK":     {"key": "NSE_EQ|INE976G01028", "step": 2,   "expiry": MONTHLY_EXPIRY},
    # IT
    "TCS":         {"key": "NSE_EQ|INE467B01029", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "INFY":        {"key": "NSE_EQ|INE009A01021", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "WIPRO":       {"key": "NSE_EQ|INE075A01022", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "HCLTECH":     {"key": "NSE_EQ|INE860A01027", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "TECHM":       {"key": "NSE_EQ|INE669C01036", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "LTIM":        {"key": "NSE_EQ|INE212H01026", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "MPHASIS":     {"key": "NSE_EQ|INE356A01018", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "PERSISTENT":  {"key": "NSE_EQ|INE262H01021", "step": 100, "expiry": MONTHLY_EXPIRY},
    "COFORGE":     {"key": "NSE_EQ|INE591G01017", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "OFSS":        {"key": "NSE_EQ|INE881D01027", "step": 100, "expiry": MONTHLY_EXPIRY},
    # AUTO
    "TATAMOTORS":  {"key": "NSE_EQ|INE155A01022", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "MARUTI":      {"key": "NSE_EQ|INE585B01010", "step": 100, "expiry": MONTHLY_EXPIRY},
    "BAJAJ-AUTO":  {"key": "NSE_EQ|INE917I01010", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "HEROMOTOCO":  {"key": "NSE_EQ|INE158A01026", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "EICHERMOT":   {"key": "NSE_EQ|INE066A01021", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "M&M":         {"key": "NSE_EQ|INE101A01026", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "ASHOKLEY":    {"key": "NSE_EQ|INE208A01029", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "TVSMOTOR":    {"key": "NSE_EQ|INE494B01023", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "BAJAJFINSV":  {"key": "NSE_EQ|INE918I01026", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "MOTHERSON":   {"key": "NSE_EQ|INE775A01035", "step": 2,   "expiry": MONTHLY_EXPIRY},
    # ENERGY
    "RELIANCE":    {"key": "NSE_EQ|INE002A01018", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "ONGC":        {"key": "NSE_EQ|INE213A01029", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "IOC":         {"key": "NSE_EQ|INE242A01010", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "BPCL":        {"key": "NSE_EQ|INE029A01011", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "GAIL":        {"key": "NSE_EQ|INE129A01019", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "ADANIENT":    {"key": "NSE_EQ|INE423A01024", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "ADANIPORTS":  {"key": "NSE_EQ|INE742F01042", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "NTPC":        {"key": "NSE_EQ|INE733E01010", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "POWERGRID":   {"key": "NSE_EQ|INE752E01010", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "TATAPOWER":   {"key": "NSE_EQ|INE245A01021", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "HINDPETRO":   {"key": "NSE_EQ|INE094A01015", "step": 5,   "expiry": MONTHLY_EXPIRY},
    # METALS
    "TATASTEEL":   {"key": "NSE_EQ|INE081A01020", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "JSWSTEEL":    {"key": "NSE_EQ|INE019A01038", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "HINDALCO":    {"key": "NSE_EQ|INE038A01020", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "VEDL":        {"key": "NSE_EQ|INE205A01025", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "SAIL":        {"key": "NSE_EQ|INE114A01011", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "NMDC":        {"key": "NSE_EQ|INE584A01023", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "COALINDIA":   {"key": "NSE_EQ|INE522F01014", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "JINDALSTEL":  {"key": "NSE_EQ|INE749A01030", "step": 10,  "expiry": MONTHLY_EXPIRY},
    # PHARMA
    "SUNPHARMA":   {"key": "NSE_EQ|INE044A01036", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "DRREDDY":     {"key": "NSE_EQ|INE089A01023", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "CIPLA":       {"key": "NSE_EQ|INE059A01026", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "DIVISLAB":    {"key": "NSE_EQ|INE361B01024", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "AUROPHARMA":  {"key": "NSE_EQ|INE406A01037", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "LUPIN":       {"key": "NSE_EQ|INE326A01037", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "BIOCON":      {"key": "NSE_EQ|INE376G01013", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "ALKEM":       {"key": "NSE_EQ|INE540L01014", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "TORNTPHARM":  {"key": "NSE_EQ|INE685A01028", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "IPCALAB":     {"key": "NSE_EQ|INE571A01020", "step": 20,  "expiry": MONTHLY_EXPIRY},
    # NBFC & FINANCE
    "BAJFINANCE":  {"key": "NSE_EQ|INE296A01024", "step": 100, "expiry": MONTHLY_EXPIRY},
    "CHOLAFIN":    {"key": "NSE_EQ|INE121A01024", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "MUTHOOTFIN":  {"key": "NSE_EQ|INE414G01012", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "RECLTD":      {"key": "NSE_EQ|INE020B01018", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "PFC":         {"key": "NSE_EQ|INE134E01011", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "HDFCLIFE":    {"key": "NSE_EQ|INE795G01014", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "SBILIFE":     {"key": "NSE_EQ|INE123W01016", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "ICICIGI":     {"key": "NSE_EQ|INE765G01017", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "SBICARD":     {"key": "NSE_EQ|INE018E01016", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "SHRIRAMFIN":  {"key": "NSE_EQ|INE721A01013", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "MANAPPURAM":  {"key": "NSE_EQ|INE522D01027", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "M&MFIN":      {"key": "NSE_EQ|INE774D01024", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "LICHSGFIN":   {"key": "NSE_EQ|INE115A01026", "step": 10,  "expiry": MONTHLY_EXPIRY},
    # INFRA
    "LT":          {"key": "NSE_EQ|INE018A01030", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "LTTS":        {"key": "NSE_EQ|INE010V01017", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "ABB":         {"key": "NSE_EQ|INE117A01022", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "SIEMENS":     {"key": "NSE_EQ|INE003A01024", "step": 100, "expiry": MONTHLY_EXPIRY},
    "HAVELLS":     {"key": "NSE_EQ|INE176B01034", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "BHEL":        {"key": "NSE_EQ|INE257A01026", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "IRFC":        {"key": "NSE_EQ|INE053F01010", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "HAL":         {"key": "NSE_EQ|INE066F01020", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "BEL":         {"key": "NSE_EQ|INE263A01024", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "CONCOR":      {"key": "NSE_EQ|INE111A01025", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "GMRINFRA":    {"key": "NSE_EQ|INE776C01039", "step": 2,   "expiry": MONTHLY_EXPIRY},
    # FMCG
    "HINDUNILVR":  {"key": "NSE_EQ|INE030A01027", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "ITC":         {"key": "NSE_EQ|INE154A01025", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "NESTLEIND":   {"key": "NSE_EQ|INE239A01016", "step": 100, "expiry": MONTHLY_EXPIRY},
    "BRITANNIA":   {"key": "NSE_EQ|INE216A01030", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "GODREJCP":    {"key": "NSE_EQ|INE102D01028", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "DABUR":       {"key": "NSE_EQ|INE016A01026", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "MARICO":      {"key": "NSE_EQ|INE196A01026", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "TATACONSUM":  {"key": "NSE_EQ|INE192A01025", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "COLPAL":      {"key": "NSE_EQ|INE259A01022", "step": 20,  "expiry": MONTHLY_EXPIRY},
    # CEMENT
    "ULTRACEMCO":  {"key": "NSE_EQ|INE481G01011", "step": 100, "expiry": MONTHLY_EXPIRY},
    "SHREECEM":    {"key": "NSE_EQ|INE070A01015", "step": 200, "expiry": MONTHLY_EXPIRY},
    "AMBUJACEM":   {"key": "NSE_EQ|INE079A01024", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "ACCLTD":      {"key": "NSE_EQ|INE012A01025", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "JKCEMENT":    {"key": "NSE_EQ|INE823G01014", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "RAMCOCEM":    {"key": "NSE_EQ|INE331A01037", "step": 10,  "expiry": MONTHLY_EXPIRY},
    # TELECOM
    "BHARTIARTL":  {"key": "NSE_EQ|INE397D01024", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "IDEA":        {"key": "NSE_EQ|INE669E01016", "step": 1,   "expiry": MONTHLY_EXPIRY},
    # OTHERS
    "ASIANPAINT":  {"key": "NSE_EQ|INE021A01026", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "TITAN":       {"key": "NSE_EQ|INE280A01028", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "INDIGO":      {"key": "NSE_EQ|INE646L01027", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "IRCTC":       {"key": "NSE_EQ|INE335Y01020", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "DLF":         {"key": "NSE_EQ|INE271C01023", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "GRASIM":      {"key": "NSE_EQ|INE047A01021", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "APOLLOHOSP":  {"key": "NSE_EQ|INE437A01024", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "ZOMATO":      {"key": "NSE_EQ|INE758T01015", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "DMART":       {"key": "NSE_EQ|INE192R01011", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "TRENT":       {"key": "NSE_EQ|INE849A01020", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "PIDILITIND":  {"key": "NSE_EQ|INE318A01026", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "UPL":         {"key": "NSE_EQ|INE628A01036", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "SRF":         {"key": "NSE_EQ|INE647A01010", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "GODREJPROP":  {"key": "NSE_EQ|INE484J01027", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "OBEROIRLTY":  {"key": "NSE_EQ|INE093I01010", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "MAXHEALTH":   {"key": "NSE_EQ|INE027H01010", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "FORTIS":      {"key": "NSE_EQ|INE061F01013", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "BOSCHLTD":    {"key": "NSE_EQ|INE323A01026", "step": 200, "expiry": MONTHLY_EXPIRY},
    "APOLLOTYRE":  {"key": "NSE_EQ|INE438A01022", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "MRF":         {"key": "NSE_EQ|INE883A01011", "step": 500, "expiry": MONTHLY_EXPIRY},
    "TATACHEM":    {"key": "NSE_EQ|INE092A01019", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "DEEPAKNTR":   {"key": "NSE_EQ|INE288B01029", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "NAUKRI":      {"key": "NSE_EQ|INE663F01024", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "HDFCAMC":     {"key": "NSE_EQ|INE127D01025", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "MCDOWELL-N":  {"key": "NSE_EQ|INE854D01024", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "VOLTAS":      {"key": "NSE_EQ|INE226A01021", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "JUBLFOOD":    {"key": "NSE_EQ|INE797F01020", "step": 20,  "expiry": MONTHLY_EXPIRY},
    "BALKRISIND":  {"key": "NSE_EQ|INE787D01026", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "CUMMINSIND":  {"key": "NSE_EQ|INE298A01020", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "NAVINFLUOR":  {"key": "NSE_EQ|INE048G01026", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "AARTIIND":    {"key": "NSE_EQ|INE769A01020", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "PRESTIGE":    {"key": "NSE_EQ|INE811K01011", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "LALPATHLAB":  {"key": "NSE_EQ|INE600L01024", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "NYKAA":       {"key": "NSE_EQ|INE388Y01029", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "PAYTM":       {"key": "NSE_EQ|INE982J01020", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "EMAMILTD":    {"key": "NSE_EQ|INE548C01032", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "CESC":        {"key": "NSE_EQ|INE486A01013", "step": 5,   "expiry": MONTHLY_EXPIRY},
    "GNFC":        {"key": "NSE_EQ|INE113B01010", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "JKCEMENT":    {"key": "NSE_EQ|INE823G01014", "step": 50,  "expiry": MONTHLY_EXPIRY},
    "IRB":         {"key": "NSE_EQ|INE821I01022", "step": 2,   "expiry": MONTHLY_EXPIRY},
    "LTFH":        {"key": "NSE_EQ|INE916DA01010","step": 5,   "expiry": MONTHLY_EXPIRY},
    "NIPPONLIFE":  {"key": "NSE_EQ|INE298J01013", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "ICICIPRU":    {"key": "NSE_EQ|INE726G01019", "step": 10,  "expiry": MONTHLY_EXPIRY},
    "SUNDARMFIN":  {"key": "NSE_EQ|INE660A01013", "step": 100, "expiry": MONTHLY_EXPIRY},
    "MFSL":        {"key": "NSE_EQ|INE247C01011", "step": 10,  "expiry": MONTHLY_EXPIRY},
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
    # Refresh expiry dates on each scan
    weekly  = get_weekly_expiry()
    monthly = get_monthly_expiry()

    log("=" * 55)
    log(f"🔍 Scanning {len(FNO_STOCKS)} stocks")
    log(f"📅 Weekly:  {weekly}  (NIFTY/BANKNIFTY/FINNIFTY)")
    log(f"📅 Monthly: {monthly} (All stocks)")
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

            # Use correct expiry per symbol
            expiry = weekly if symbol in ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"] else monthly
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
                            "expiry": expiry,
                            "sl": sl, "t1": t1, "t2": t2
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
            msg += f"• <b>{s['symbol']} {s['strike']}{s['type']}</b> RSI:{s['rsi']} ₹{s['ltp']} Exp:{s['expiry']}\n"
        send_telegram(msg)

# ── MAIN ──────────────────────────────────────────────────
log("🚀 ATM RSI SCANNER — AUTO EXPIRY")
log(f"📅 Weekly Expiry:  {WEEKLY_EXPIRY}  (NIFTY/BANKNIFTY)")
log(f"📅 Monthly Expiry: {MONTHLY_EXPIRY} (Stocks)")
log(f"📊 {len(FNO_STOCKS)} F&O stocks")
log(f"🔔 Telegram: {'✅' if TELEGRAM_BOT else '❌ Set TELEGRAM_BOT variable'}")
log("=" * 55)

send_telegram(
    f"🚀 <b>ATM RSI Scanner ON!</b>\n"
    f"📅 Weekly: {WEEKLY_EXPIRY} (NIFTY/BANKNIFTY)\n"
    f"📅 Monthly: {MONTHLY_EXPIRY} (Stocks)\n"
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
