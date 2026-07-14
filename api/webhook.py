from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"

FNO_SYMBOLS = [
    "ETERNAL", "RELIANCE", "BANDHANBNK", "MAZDOCK", "VEDL", "HDFCBANK",
    "SUNPHARMA", "COCHINSHIP", "MARUTI", "BSE", "ADANIPOWER",
    "ONGC", "COALINDIA", "SBIN", "ICICIBANK", "BHARTIARTL", "INFY",
    "IDEA", "MCX", "RECLTD", "ITC", "DIXON", "SUZLON", "ADANIENT",
    "TATASTEEL", "AXISBANK", "RBLBANK", "LT", "DRREDDY", "JIOFIN",
    "WAAREEENER", "HCLTECH", "OFSS", "CROMPTON", "SHRIRAMFIN", "TCS",
    "PFC", "TMPV", "INDIGO", "BAJFINANCE", "ADANIGREEN", "VBL",
    "POWERINDIA", "SWIGGY", "ADANIPORTS", "INDUSTOWER", "TECHM", "KAYNES",
    "NATIONALUM", "HINDZINC", "FORCEMOT", "PERSISTENT", "NESTLEIND",
    "BPCL", "BHEL", "INDUSINDBK", "BHARATFORG", "LODHA", "TVSMOTOR",
    "ADANIENSOL", "SAMMAANCAP", "SAIL", "TATAPOWER", "BAJAJ-AUTO",
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
    "DIVISLAB", "BAJAJFINSV", "ANGELONE", "UNOMINDA",
    "AUBANK", "MOTILALOFS", "JUBLFOOD", "BOSCHLTD", "PNBHOUSING", "IRFC",
    "MANAPPURAM", "IREDA", "CONCOR", "CIPLA", "MPHASIS", "LTM", "PIIND",
    "VOLTAS", "GAIL", "INDHOTEL", "GMRAIRPORT", "PGEL", "CHOLAFIN",
    "DMART", "LTF", "BANKINDIA", "LICHSGFIN", "IEX", "INOXWIND", "LICI",
    "UNITDSPR", "TATACONSUM", "VMM", "DALBHARAT", "PHOENIXLTD", "SIEMENS",
    "TORNTPHARM", "ZYDUSLIFE", "PREMIERENE", "AMBUJACEM", "NBCC", "BIOCON",
    "CAMS", "UPL", "APLAPOLLO", "FORTIS", "OBEROIRLTY", "DELHIVERY",
    "MFSL", "ICICIGI", "TIINDIA", "COLPAL", "NYKAA", "PAGEIND", "KFINTECH",
    "PRESTIGE", "MANKIND", "MARICO", "PIDILITIND", "ICICIPRULI",
    "GODREJCP", "ALKEM", "PATANJALI", "DABUR", "SHREECEM", "BAJAJHLDNG",
    "NUVAMA"
]

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
    all_stocks = []
    for symbol in FNO_SYMBOLS:
        ltp, change_pct = get_price_at_time_yahoo(symbol, date_obj, time_obj)
        if ltp is None:
            continue
        all_stocks.append((symbol, ltp, change_pct))

    # Advances/Declines from all fetched stocks
    advances = sum(1 for _, _, c in all_stocks if c > 0)
    declines = sum(1 for _, _, c in all_stocks if c < 0)
    unchanged = sum(1 for _, _, c in all_stocks if c == 0)
    total = advances + declines + unchanged

    # Top gainers and losers (no % filter) for breadth
    all_sorted_gainers = sorted([s for s in all_stocks if s[2] > 0], key=lambda x: x[2], reverse=True)
    all_sorted_losers = sorted([s for s in all_stocks if s[2] < 0], key=lambda x: x[2])

    # 0-3% filtered movers
    gainers = [s for s in all_stocks if 0 < s[2] < 3]
    losers = [s for s in all_stocks if -3 < s[2] < 0]
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])

    breadth = {
        "advances": advances,
        "declines": declines,
        "unchanged": unchanged,
        "total": total,
        "top_gainer": all_sorted_gainers[0] if all_sorted_gainers else None,
        "top_loser": all_sorted_losers[0] if all_sorted_losers else None,
    }

    return gainers[:10], losers[:10], breadth

def get_live_movers():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.nseindia.com",
        "Accept": "application/json"
    }
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    all_stocks = []
    nifty_change = 0

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
                    all_stocks.append((symbol, ltp, change_pct))
            except Exception:
                continue

        # Get Nifty change
        nifty_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        nr = session.get(nifty_url, headers=headers, timeout=10)
        nifty_data = nr.json()
        for s in nifty_data.get("data", []):
            if s.get("symbol") == "NIFTY 50":
                nifty_change = s.get("pChange", 0)
                break

    except Exception as e:
        print(f"API error: {e}")

    advances = sum(1 for _, _, c in all_stocks if c > 0)
    declines = sum(1 for _, _, c in all_stocks if c < 0)
    unchanged = sum(1 for _, _, c in all_stocks if c == 0)
    total = advances + declines + unchanged

    all_sorted_gainers = sorted([s for s in all_stocks if s[2] > 0], key=lambda x: x[2], reverse=True)
    all_sorted_losers = sorted([s for s in all_stocks if s[2] < 0], key=lambda x: x[2])

    gainers = [s for s in all_stocks if 0 < s[2] < 3]
    losers = [s for s in all_stocks if -3 < s[2] < 0]
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])

    breadth = {
        "advances": advances,
        "declines": declines,
        "unchanged": unchanged,
        "total": total,
        "nifty_change": nifty_change,
        "top_gainer": all_sorted_gainers[0] if all_sorted_gainers else None,
        "top_loser": all_sorted_losers[0] if all_sorted_losers else None,
    }

    return gainers[:10], losers[:10], breadth

def get_verdict(advances, declines):
    total = advances + declines
    if total == 0:
        return "No data"
    ratio = advances / total * 100
    if ratio >= 70:
        return "STRONGLY BULLISH 🟢"
    elif ratio >= 55:
        return "BULLISH 🟢"
    elif ratio >= 45:
        return "NEUTRAL ⚪"
    elif ratio >= 30:
        return "BEARISH 🔴"
    else:
        return "STRONGLY BEARISH 🔴"

def build_message(gainers, losers, breadth, date_label, time_label=None):
    time_str = f" at {time_label}" if time_label else ""

    # Breadth section
    adv = breadth.get("advances", 0)
    dec = breadth.get("declines", 0)
    unc = breadth.get("unchanged", 0)
    total = breadth.get("total", 0)
    nifty_change = breadth.get("nifty_change", None)
    top_gainer = breadth.get("top_gainer")
    top_loser = breadth.get("top_loser")
    verdict = get_verdict(adv, dec)
    ratio = f"{adv}:{dec}"

    nifty_line = ""
    if nifty_change is not None:
        sign = "+" if nifty_change > 0 else ""
        emoji = "🟢" if nifty_change > 0 else "🔴"
        nifty_line = f"{emoji} Nifty: {sign}{nifty_change:.2f}%\n"

    top_g_line = ""
    top_l_line = ""
    if top_gainer:
        top_g_line = f"🏆 Top Gainer: {top_gainer[0]} +{top_gainer[2]:.2f}%\n"
    if top_loser:
        top_l_line = f"💀 Top Loser:  {top_loser[0]} {top_loser[2]:.2f}%\n"

    breadth_section = (
        f"📊 *FnO Market Breadth* ({total} stocks)\n"
        f"{nifty_line}"
        f"📈 Advances: {adv}   📉 Declines: {dec}   ➡️ {unc} Unchanged\n"
        f"📊 Ratio: {ratio}\n"
        f"{top_g_line}"
        f"{top_l_line}"
        f"🎯 Verdict: *{verdict}*"
    )

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
        f"{breadth_section}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ *TOP 10 GAINERS* 📈\n"
        f"{g_table}\n"
        f"🔴 *TOP 10 LOSERS* 📉\n"
        f"{l_table}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

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

        if text_lower == "/start":
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
                gainers, losers, breadth = get_live_movers()
                IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                send_message(chat_id, build_message(gainers, losers, breadth, date_label=today))
            else:
                date_obj, time_obj = parse_input(args)
                date_label = date_obj.strftime("%d %b %Y")
                time_obj = time_obj or datetime.time(15, 30)
                time_label = time_obj.strftime("%I:%M %p")
                send_message(chat_id, f"⏳ Fetching *{date_label}* at *{time_label}*...\n_May take 2-3 mins_")
                gainers, losers, breadth = get_movers_at_time(date_obj, time_obj)
                send_message(chat_id, build_message(gainers, losers, breadth, date_label=date_label, time_label=time_label))

except Exception as e:
        print(f"Error: {e}")
        if chat_id:
            send_message(chat_id, f"Error: {str(e)}")
                return jsonify({"ok": True})
