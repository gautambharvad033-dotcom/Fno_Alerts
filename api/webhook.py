from flask import Flask, request, jsonify
import requests
import datetime

YAHOO_SPECIAL = {
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "NAM-INDIA": "NAM-INDIA.NS",
    "360ONE": "360ONE.NS",
}

def get_yahoo_symbol(symbol):
    return YAHOO_SPECIAL.get(symbol, f"{symbol}.NS")

def get_price_at_time_yahoo(symbol, date_obj, time_obj):
    try:
        yahoo_symbol = get_yahoo_symbol(symbol)
        date_ts = int(datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0).timestamp())
        end_ts = date_ts + 86400
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        params = {
            "period1": date_ts,
            "period2": end_ts,
            "interval": "1m",
            "includePrePost": "false"
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return None, None
        timestamps = result[0].get("timestamp", [])
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        prev_close = result[0].get("meta", {}).get("chartPreviousClose", None)
        if not timestamps or not closes or prev_close is None:
            return None, None
        target_seconds = time_obj.hour * 3600 + time_obj.minute * 60
        best_idx = None
        best_diff = float("inf")
        for i, ts in enumerate(timestamps):
            ist_dt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=5, minutes=30)
            candle_seconds = ist_dt.hour * 3600 + ist_dt.minute * 60
            diff = abs(candle_seconds - target_seconds)
            if diff < best_diff and i < len(closes) and closes[i] is not None:
                best_diff = diff
                best_idx = i
        if best_idx is None:
            return None, None
        ltp = closes[best_idx]
        change_pct = ((ltp - prev_close) / prev_close) * 100
        return round(ltp, 2), round(change_pct, 2)
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None, None

def get_movers_at_time(date_obj, time_obj):
    gainers, losers = [], []
    for symbol in FNO_SYMBOLS:
        ltp, change_pct = get_price_at_time_yahoo(symbol, date_obj, time_obj)
        if ltp is None:
            continue
        if 0 < change_pct < 3:
            gainers.append((symbol, ltp, change_pct))
        elif -3 < change_pct < 0:
            losers.append((symbol, ltp, change_pct))
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])
    return gainers[:10], losers[:10]

FNO_SYMBOLS = [
    "ETERNAL", "RELIANCE", "BANDHANBNK", "MAZDOCK", "VEDL", "HDFCBANK",
    "SUNPHARMA", "COCHINSHIP", "MARUTI", "M&M", "BSE", "ADANIPOWER",
    "ONGC", "COALINDIA", "SBIN", "ICICIBANK", "BHARTIARTL", "INFY",
    "IDEA", "MCX", "RECLTD", "ITC", "DIXON", "SUZLON", "ADANIENT",
    "TATASTEEL", "AXISBANK", "RBLBANK", "LT", "DRREDDY", "JIOFIN",
    "WAAREEENER", "HCLTECH", "OFSS", "CROMPTON", "SHRIRAMFIN", "TCS",
    "PFC", "TMPV", "INDIGO", "BAJFINANCE", "ADANIGREEN", "VBL",
    "POWERINDIA", "SWIGGY", "ADANIPORTS", "INDUSTOWER", "TECHM", "KAYNES",
    "NATIONALUM", "HINDZINC", "FORCEMOT", "PERSISTENT", "NESTLEIND",
    "BPCL", "BHEL", "INDUSINDBK", "BHARATFORG", "LODHA", "TVSMOTOR",
    "BAJAJ-AUTO", "ADANIENSOL", "SAMMAANCAP", "SAIL", "TATAPOWER",
    "HINDALCO", "ULTRACEMCO", "EICHERMOT", "PAYTM", "BEL", "CANBK",
    "OIL", "TRENT", "NMDC", "HAL", "ABCAPITAL", "WIPRO", "HAVELLS",
    "NHPC", "JSWSTEEL", "GODFRYPHLP", "HINDUNILVR", "ASHOKLEY",
    "UNIONBANK", "NTPC", "BDL", "SONACOMS", "KEI", "POLYCAB",
    "AUROPHARMA", "HDFCLIFE", "NAUKRI", "POWERGRID", "HEROMOTOCO",
    "CDSL", "FEDERALBNK", "TITAN", "COFORGE", "IDFCFIRSTB", "KOTAKBANK",
    "RVNL", "BRITANNIA", "MAXHEALTH", "APOLLOHOSP", "ABB", "MOTHERSON",
    "YESBANK", "INDIANB", "GLENMARK", "POLICYBZR", "LAURUSLABS",
    "JSWENERGY", "PNB", "CGPOWER", "SBICARD", "GODREJPROP", "HYUNDAI",
    "EXIDEIND", "DLF", "GRASIM", "CUMMINSIND", "ASTRAL", "HDFCAMC",
    "MUTHOOTFIN", "BLUESTARCO", "KALYANKJIL", "TATAELXSI", "SBILIFE",
    "BANKBARODA", "AMBER", "HINDPETRO", "KPITTECH", "SUPREMEIND", "IOC",
    "ASIANPAINT", "PETRONET", "JINDALSTEL", "SOLARINDS", "LUPIN", "SRF",
    "DIVISLAB", "BAJAJFINSV", "ANGELONE", "NAM-INDIA", "UNOMINDA",
    "AUBANK", "MOTILALOFS", "JUBLFOOD", "BOSCHLTD", "PNBHOUSING", "IRFC",
    "MANAPPURAM", "IREDA", "CONCOR", "CIPLA", "MPHASIS", "LTM", "PIIND",
    "VOLTAS", "GAIL", "INDHOTEL", "GMRAIRPORT", "PGEL", "CHOLAFIN",
    "DMART", "LTF", "BANKINDIA", "LICHSGFIN", "IEX", "INOXWIND", "LICI",
    "UNITDSPR", "TATACONSUM", "VMM", "DALBHARAT", "PHOENIXLTD", "SIEMENS",
    "TORNTPHARM", "ZYDUSLIFE", "PREMIERENE", "AMBUJACEM", "NBCC", "BIOCON",
    "CAMS", "UPL", "APLAPOLLO", "FORTIS", "OBEROIRLTY", "DELHIVERY",
    "MFSL", "ICICIGI", "TIINDIA", "COLPAL", "NYKAA", "PAGEIND", "KFINTECH",
    "PRESTIGE", "360ONE", "MANKIND", "MARICO", "PIDILITIND", "ICICIPRULI",
    "GODREJCP", "ALKEM", "PATANJALI", "DABUR", "SHREECEM", "BAJAJHLDNG",
    "NUVAMA"
]

_security_id_cache = {}


def get_security_ids():
    global _security_id_cache
    if _security_id_cache:
        return _security_id_cache
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        r = requests.get(url, timeout=15)
        content = r.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            try:
                symbol = row.get("SEM_TRADING_SYMBOL", "").strip()
                seg = row.get("SEM_EXM_EXCH_ID", "").strip()
                sec_id = row.get("SEM_SMST_SECURITY_ID", "").strip()
                inst = row.get("SEM_INSTRUMENT_NAME", "").strip()
                if seg == "NSE" and inst == "EQUITY" and symbol and sec_id:
                    _security_id_cache[symbol] = sec_id
            except Exception:
                continue
        print(f"Loaded {len(_security_id_cache)} security IDs")
    except Exception as e:
        print(f"Error loading security master: {e}")
    return _security_id_cache


def parse_input(text):
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    today = datetime.datetime.now(IST)
    date_obj = today
    time_obj = None
    parts = text.strip().split()
    if len(parts) >= 1:
        date_str = parts[0]
        for fmt in ["%d-%m-%Y", "%d-%b-%Y", "%d-%b", "%Y-%m-%d"]:
            try:
                dt = datetime.datetime.strptime(date_str, fmt)
                if fmt == "%d-%b":
                    dt = dt.replace(year=today.year)
                date_obj = dt
                break
            except Exception:
                continue
    if len(parts) >= 2:
        time_str = parts[1]
        for fmt in ["%H:%M", "%I:%M"]:
            try:
                t = datetime.datetime.strptime(time_str, fmt)
                time_obj = t.time()
                break
            except Exception:
                continue
    return date_obj, time_obj


def test_dhan_api(sec_id, date_obj):
    try:
        date_str = date_obj.strftime("%Y-%m-%d")
        url = "https://api.dhan.co/v2/charts/intraday"
        payload = {
            "securityId": sec_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": "1",
            "fromDate": date_str,
            "toDate": date_str
        }
        r = requests.post(url, json=payload, headers=DHAN_HEADERS, timeout=10)
        return r.status_code, str(r.text)[:500]
    except Exception as e:
        return None, str(e)


def get_price_at_time(symbol, sec_id, date_obj, time_obj):
    try:
        date_str = date_obj.strftime("%Y-%m-%d")
        url = "https://api.dhan.co/v2/charts/intraday"
        payload = {
            "securityId": sec_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": "1",
            "fromDate": date_str,
            "toDate": date_str
        }
        r = requests.post(url, json=payload, headers=DHAN_HEADERS, timeout=10)
        data = r.json()
        timestamps = data.get("data", {}).get("timestamp", [])
        closes = data.get("data", {}).get("close", [])
        opens_list = data.get("data", {}).get("open", [])
        if not timestamps or not closes:
            return None, None
        target_seconds = time_obj.hour * 3600 + time_obj.minute * 60
        best_idx = 0
        best_diff = float("inf")
        for i, ts in enumerate(timestamps):
            dt = datetime.datetime.fromtimestamp(ts)
            candle_seconds = dt.hour * 3600 + dt.minute * 60
            diff = abs(candle_seconds - target_seconds)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        prev_url = "https://api.dhan.co/v2/charts/historical"
        prev_date = (date_obj - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        prev_payload = {
            "securityId": sec_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "expiryCode": 0,
            "oi": False,
            "fromDate": prev_date,
            "toDate": date_str,
            "interval": "1d"
        }
        pr = requests.post(prev_url, json=prev_payload, headers=DHAN_HEADERS, timeout=10)
        prev_data = pr.json()
        prev_closes = prev_data.get("data", {}).get("close", [])
        prev_close = prev_closes[-2] if len(prev_closes) >= 2 else (opens_list[0] if opens_list else closes[best_idx])
        ltp = closes[best_idx]
        change_pct = ((ltp - prev_close) / prev_close) * 100
        return ltp, change_pct
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None, None


def get_movers_at_time(date_obj, time_obj):
    security_ids = get_security_ids()
    gainers, losers = [], []
    for symbol in FNO_SYMBOLS:
        sec_id = security_ids.get(symbol)
        if not sec_id:
            continue
        ltp, change_pct = get_price_at_time(symbol, sec_id, date_obj, time_obj)
        if ltp is None:
            continue
        if 0 < change_pct < 3:
            gainers.append((symbol, ltp, change_pct))
        elif -3 < change_pct < 0:
            losers.append((symbol, ltp, change_pct))
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])
    return gainers[:10], losers[:10]


def get_live_movers():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.nseindia.com",
        "Accept": "application/json"
    }
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    gainers, losers = [], []
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        r = session.get(url, headers=headers, timeout=10)
        data = r.json()
        stocks = data.get("data", [])
        for stock in stocks:
            try:
                symbol = stock.get("symbol", "")
                ltp = stock.get("lastPrice", 0)
                change_pct = stock.get("pChange", 0)
                if symbol and symbol in FNO_SYMBOLS:
                    if 0 < change_pct < 3:
                        gainers.append((symbol, ltp, change_pct))
                    elif -3 < change_pct < 0:
                        losers.append((symbol, ltp, change_pct))
            except Exception:
                continue
    except Exception as e:
        print(f"API error: {e}")
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])
    return gainers[:10], losers[:10]


def build_message(gainers, losers, date_label, time_label=None):
    time_str = f" at {time_label}" if time_label else ""

    def make_table(stocks, is_gainer):
        lines = "`#   SYMBOL         LTP        CHG%`\n"
        lines += "`────────────────────────────────`\n"
        for i, (s, l, c) in enumerate(stocks, 1):
            num = str(i).ljust(2)
            symbol = s[:12].ljust(12)
            price = f"Rs{l}".ljust(10)
            sign = "+" if is_gainer else ""
            chg = f"{sign}{c:.2f}%"
            lines += f"`{num}  {symbol}  {price}  {chg}`\n"
        return lines if stocks else "`  None`\n"

    g_table = make_table(gainers, True)
    l_table = make_table(losers, False)

    return (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *FnO Top 10 Movers*\n"
        f"📅 {date_label}{time_str}\n"
        f"_(0% to 3% move only)_\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ *TOP 10 GAINERS* 📈\n"
        f"{g_table}\n"
        f"🔴 *TOP 10 LOSERS* 📉\n"
        f"{l_table}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })


@app.route("/webhook", methods=["GET"])
def home():
    return "FnO Bot is running! ✅", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    chat_id = None
    try:
        msg = update.get("message", {})
        full_text = msg.get("text", "").strip()
        text_lower = full_text.lower()
        chat_id = msg.get("chat", {}).get("id")

        if not chat_id:
            return jsonify({"ok": True})
if text_lower == "/test":
            date_obj = datetime.datetime(2026, 4, 29)
            time_obj = datetime.time(9, 25)
            ltp, chg = get_price_at_time_yahoo("RELIANCE", date_obj, time_obj)
            send_message(chat_id, f"Yahoo Test:\nRELIANCE 29-Apr 9:25AM\nLTP: `{ltp}`\nChange: `{chg}%`")
            if reliance_id != "NOT FOUND":
                date_obj = datetime.datetime(2026, 4, 29)
                status, response = test_dhan_api(reliance_id, date_obj)
                send_message(chat_id, f"Dhan API Status: `{status}`\nResponse: `{response}`")

        elif text_lower == "/start":
            send_message(chat_id,
                "👋 *FnO Alert Bot*\n\n"
                "*Commands:*\n"
                "📊 `/fno` - Today live top 10\n"
                "📅 `/fno 29-Apr` - Any date EOD\n"
                "⏰ `/fno 29-Apr 9:25` - Any date at time\n"
                "⏰ `/fno 15-04-2026 14:30` - Full date and time\n\n"
                "⏰ Auto alert every weekday at 9:25 AM IST"
            )

        elif text_lower.startswith("/fno"):
            parts = full_text.split(maxsplit=1)
            args = parts[1].strip() if len(parts) > 1 else ""

            if not args:
                send_message(chat_id, "⏳ Fetching live FnO data...")
                gainers, losers = get_live_movers()
                IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                send_message(chat_id, build_message(gainers, losers, date_label=today))
            else:
                date_obj, time_obj = parse_input(args)
                date_label = date_obj.strftime("%d %b %Y")
                time_obj = time_obj or datetime.time(15, 30)
                time_label = time_obj.strftime("%I:%M %p")
                send_message(chat_id, f"⏳ Fetching *{date_label}* at *{time_label}*...\n_May take 1-2 mins_")
                gainers, losers = get_movers_at_time(date_obj, time_obj)
                send_message(chat_id, build_message(gainers, losers, date_label=date_label, time_label=time_label))

    except Exception as e:
        print(f"Error: {e}")
        if chat_id:
            send_message(chat_id, f"Error: {str(e)}")

    return jsonify({"ok": True})
