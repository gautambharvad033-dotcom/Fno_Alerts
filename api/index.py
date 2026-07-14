from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"

SECTOR_STOCKS = {
    "BANK": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BANDHANBNK",
        "FEDERALBNK", "IDFCFIRSTB", "INDUSINDBK", "BANKBARODA", "PNB", "CANBK",
        "UNIONBANK", "INDIANB", "RBLBANK", "YESBANK", "AUBANK", "BANKINDIA"
    ],
    "IT": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "MPHASIS", "COFORGE",
        "PERSISTENT", "OFSS", "KPITTECH"
    ],
    "AUTO": [
        "MARUTI", "BAJAJ-AUTO", "TVSMOTOR", "EICHERMOT", "HEROMOTOCO",
        "ASHOKLEY", "MOTHERSON", "BHARATFORG", "BOSCHLTD", "UNOMINDA",
        "TIINDIA", "HYUNDAI"
    ],
    "PHARMA": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "AUROPHARMA", "DIVISLAB",
        "ALKEM", "GLENMARK", "LAURUSLABS", "BIOCON", "ZYDUSLIFE", "MANKIND"
    ],
    "FMCG": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO",
        "COLPAL", "GODREJCP", "TATACONSUM", "VBL", "PATANJALI"
    ],
    "METAL": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "NMDC",
        "NATIONALUM", "HINDZINC", "COALINDIA", "APLAPOLLO"
    ],
    "REALTY": [
        "DLF", "GODREJPROP", "OBEROIRLTY", "PHOENIXLTD", "LODHA",
        "PRESTIGE"
    ],
    "ENERGY": [
        "RELIANCE", "ONGC", "BPCL", "IOC", "HINDPETRO", "GAIL",
        "OIL", "PETRONET", "ADANIGREEN", "TATAPOWER", "ADANIPOWER",
        "NTPC", "POWERGRID", "NHPC", "ADANIENSOL", "WAAREEENER",
        "INOXWIND", "SOLARINDS", "POWERINDIA"
    ],
    "FINSERV": [
        "BAJFINANCE", "BAJAJFINSV", "HDFCLIFE", "SBILIFE", "ICICIGI",
        "ICICIPRULI", "MUTHOOTFIN", "CHOLAFIN", "SHRIRAMFIN", "MANAPPURAM",
        "PNBHOUSING", "LICHSGFIN", "MFSL", "HDFCAMC", "ABCAPITAL",
        "IRFC", "RECLTD", "PFC", "IREDA", "LTF", "ANGELONE",
        "MOTILALOFS", "JIOFIN"
    ],
    "PSUBANK": [
        "SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK",
        "INDIANB", "BANKINDIA", "MAZDOCK", "BDL", "COCHINSHIP"
    ]
}

FNO_SYMBOLS = list(set([s for stocks in SECTOR_STOCKS.values() for s in stocks] + [
    "ETERNAL", "ADANIPORTS", "INDUSTOWER", "TECHM", "KAYNES",
    "FORCEMOT", "PERSISTENT", "BHEL", "BHARATFORG", "TVSMOTOR",
    "PAYTM", "BEL", "TRENT", "HAL", "ABCAPITAL", "HAVELLS",
    "JSWSTEEL", "GODFRYPHLP", "NTPC", "SONACOMS", "KEI", "POLYCAB",
    "NAUKRI", "POWERGRID", "CDSL", "TITAN", "RVNL", "MAXHEALTH",
    "APOLLOHOSP", "ABB", "JSWENERGY", "SBICARD", "EXIDEIND",
    "GRASIM", "CUMMINSIND", "ASTRAL", "BLUESTARCO", "KALYANKJIL",
    "TATAELXSI", "AMBER", "KPITTECH", "SUPREMEIND", "JINDALSTEL",
    "AUBANK", "JUBLFOOD", "CONCOR", "PIIND", "VOLTAS", "INDHOTEL",
    "GMRAIRPORT", "PGEL", "CHOLAFIN", "DMART", "LICHSGFIN", "IEX",
    "LICI", "UNITDSPR", "VMM", "DALBHARAT", "SIEMENS", "TORNTPHARM",
    "PREMIERENE", "AMBUJACEM", "NBCC", "CAMS", "UPL", "FORTIS",
    "DELHIVERY", "TIINDIA", "NYKAA", "PAGEIND", "KFINTECH",
    "PIDILITIND", "SHREECEM", "BAJAJHLDNG", "NUVAMA", "DIXON",
    "SUZLON", "ADANIENT", "VBL", "SWIGGY", "SAMMAANCAP", "TMPV",
    "INDIGO", "EICHERMOT", "OIL", "WIPRO", "GODFRYPHLP", "ASHOKLEY",
    "AUROPHARMA", "HDFCLIFE", "BRITANNIA", "MOTHERSON", "GLENMARK",
    "POLICYBZR", "CGPOWER", "HYUNDAI", "GRASIM", "TATAELXSI",
    "HINDPETRO", "SOLARINDS", "SRF", "DIVISLAB", "MOTILALOFS",
    "BOSCHLTD", "PNBHOUSING", "MANAPPURAM", "CIPLA", "MPHASIS",
    "LTM", "GAIL", "GMRAIRPORT", "LTF", "INOXWIND", "TATACONSUM",
    "ZYDUSLIFE", "AMBUJACEM", "BIOCON", "APLAPOLLO", "OBEROIRLTY",
    "MFSL", "COLPAL", "PRESTIGE", "MARICO", "ICICIPRULI", "GODREJCP",
    "PATANJALI", "DABUR", "BAJAJHLDNG", "MARUTI", "COCHINSHIP",
    "MAZDOCK", "MCX", "RECLTD", "DIXON", "RBLBANK", "JIOFIN",
    "OFSS", "CROMPTON", "SHRIRAMFIN", "ADANIGREEN", "POWERINDIA",
    "NATIONALUM", "HINDZINC", "NESTLEIND", "INDUSINDBK", "LODHA",
    "ADANIENSOL", "SAMMAANCAP", "SAIL", "TATAPOWER", "HINDALCO",
    "ULTRACEMCO", "CANBK", "NMDC", "HAVELLS", "NHPC", "BDL",
    "SONACOMS", "KEI", "FEDERALBNK", "COFORGE", "IDFCFIRSTB",
    "MAXHEALTH", "INDIANB", "POLICYBZR", "JSWENERGY", "CGPOWER",
    "SBICARD", "GODREJPROP", "EXIDEIND", "DLF", "CUMMINSIND",
    "KALYANKJIL", "SBILIFE", "BANKBARODA", "AMBER", "SUPREMEIND",
    "ASIANPAINT", "PETRONET", "JINDALSTEL", "BAJAJFINSV", "ANGELONE",
    "JUBLFOOD", "IREDA", "CONCOR", "PIIND", "VOLTAS", "INDHOTEL",
    "PGEL", "DMART", "BANKINDIA", "IEX", "LICI", "UNITDSPR",
    "DALBHARAT", "PHOENIXLTD", "TORNTPHARM", "PREMIERENE", "NBCC",
    "UPL", "FORTIS", "DELHIVERY", "ICICIGI", "NYKAA", "PAGEIND",
    "MANKIND", "PIDILITIND", "ALKEM", "SHREECEM", "NUVAMA"
]))

YAHOO_SPECIAL = {
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "NAM-INDIA": "NAM-INDIA.NS",
    "360ONE": "360ONE.NS",
    "M&M": "M%26M.NS",
}

SECTOR_LABELS = {
    "BANK": "🏦 Bank",
    "IT": "💻 IT",
    "AUTO": "🚗 Auto",
    "PHARMA": "💊 Pharma",
    "FMCG": "🛒 FMCG",
    "METAL": "⚙️ Metal",
    "REALTY": "🏢 Realty",
    "ENERGY": "⚡ Energy",
    "FINSERV": "💰 Fin Serv",
    "PSUBANK": "🏛️ PSU Bank"
}


def get_yahoo_symbol(symbol):
    return YAHOO_SPECIAL.get(symbol, f"{symbol}.NS")


def get_price_at_time_yahoo(symbol, date_obj, time_obj):
    try:
        yahoo_symbol = get_yahoo_symbol(symbol)
        date_ts = int(datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0).timestamp())
        end_ts = date_ts + 86400
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        params = {"period1": date_ts, "period2": end_ts, "interval": "1m", "includePrePost": "false"}
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


def get_movers(symbols, date_obj=None, time_obj=None, live=False):
    all_stocks = []
    if live:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://www.nseindia.com",
            "Accept": "application/json"
        }
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        try:
            url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            r = session.get(url, headers=headers, timeout=10)
            data = r.json()
            stocks = data.get("data", [])
            stock_map = {s.get("symbol"): s for s in stocks}
            for symbol in symbols:
                if symbol in stock_map:
                    s = stock_map[symbol]
                    ltp = s.get("lastPrice", 0)
                    change_pct = s.get("pChange", 0)
                    all_stocks.append((symbol, ltp, change_pct))
        except Exception as e:
            print(f"Live API error: {e}")
    else:
        for symbol in symbols:
            ltp, change_pct = get_price_at_time_yahoo(symbol, date_obj, time_obj)
            if ltp is None:
                continue
            all_stocks.append((symbol, ltp, change_pct))

    advances = sum(1 for _, _, c in all_stocks if c > 0)
    declines = sum(1 for _, _, c in all_stocks if c < 0)
    unchanged = len(all_stocks) - advances - declines
    all_sorted_gainers = sorted([s for s in all_stocks if s[2] > 0], key=lambda x: x[2], reverse=True)
    all_sorted_losers = sorted([s for s in all_stocks if s[2] < 0], key=lambda x: x[2])
    gainers = sorted([s for s in all_stocks if 0 < s[2] < 3], key=lambda x: x[2], reverse=True)
    losers = sorted([s for s in all_stocks if -3 < s[2] < 0], key=lambda x: x[2])
    breadth = {
        "advances": advances,
        "declines": declines,
        "unchanged": unchanged,
        "total": len(all_stocks),
        "top_gainer": all_sorted_gainers[0] if all_sorted_gainers else None,
        "top_loser": all_sorted_losers[0] if all_sorted_losers else None,
    }
    return gainers[:10], losers[:10], breadth


def get_nifty_change():
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com",
            "Accept": "application/json"
        }
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        r = session.get(url, headers=headers, timeout=10)
        data = r.json()
        for s in data.get("data", []):
            if s.get("symbol") == "NIFTY 50":
                return s.get("pChange", 0)
    except Exception:
        pass
    return None


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


def build_message(gainers, losers, breadth, date_label, time_label=None, sector=None, nifty_change=None):
    time_str = f" at {time_label}" if time_label else ""
    sector_label = SECTOR_LABELS.get(sector, "All FnO") if sector else "All FnO"
    adv = breadth.get("advances", 0)
    dec = breadth.get("declines", 0)
    unc = breadth.get("unchanged", 0)
    total = breadth.get("total", 0)
    top_gainer = breadth.get("top_gainer")
    top_loser = breadth.get("top_loser")
    verdict = get_verdict(adv, dec)

    nifty_line = ""
    if nifty_change is not None:
        sign = "+" if nifty_change > 0 else ""
        emoji = "🟢" if nifty_change > 0 else "🔴"
        nifty_line = f"{emoji} Nifty: {sign}{nifty_change:.2f}%\n"

    top_g_line = f"🏆 Top Gainer: {top_gainer[0]} +{top_gainer[2]:.2f}%\n" if top_gainer else ""
    top_l_line = f"💀 Top Loser:  {top_loser[0]} {top_loser[2]:.2f}%\n" if top_loser else ""

    breadth_section = (
        f"📊 *{sector_label} Breadth* ({total} stocks)\n"
        f"{nifty_line}"
        f"📈 Advances: {adv}   📉 Declines: {dec}   ➡️ {unc} Unchanged\n"
        f"📊 Ratio: {adv}:{dec}\n"
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
        f"📊 *{sector_label} — Top 10 Movers*\n"
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


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})


def send_message_with_buttons(chat_id, text, buttons):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": buttons}
    })


def send_sector_menu(chat_id):
    buttons = [
        [
            {"text": "🏦 Bank", "callback_data": "sector_BANK"},
            {"text": "💻 IT", "callback_data": "sector_IT"},
            {"text": "🚗 Auto", "callback_data": "sector_AUTO"},
        ],
        [
            {"text": "💊 Pharma", "callback_data": "sector_PHARMA"},
            {"text": "🛒 FMCG", "callback_data": "sector_FMCG"},
            {"text": "⚙️ Metal", "callback_data": "sector_METAL"},
        ],
        [
            {"text": "🏢 Realty", "callback_data": "sector_REALTY"},
            {"text": "⚡ Energy", "callback_data": "sector_ENERGY"},
            {"text": "💰 Fin Serv", "callback_data": "sector_FINSERV"},
        ],
        [
            {"text": "🏛️ PSU Bank", "callback_data": "sector_PSUBANK"},
            {"text": "📊 All FnO", "callback_data": "sector_ALL"},
        ]
    ]
    send_message_with_buttons(chat_id,
        "🏷️ *Select a Sector:*\nTap any sector to get live top gainers and losers!",
        buttons
    )


def answer_callback(callback_query_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_query_id})


@app.route("/webhook", methods=["GET"])
def home():
    return "FnO Bot is running! ✅", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    chat_id = None
    try:
        IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

        if "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            chat_id = callback["message"]["chat"]["id"]
            data = callback.get("data", "")
            answer_callback(callback_id)

            if data.startswith("sector_"):
                sector = data.replace("sector_", "")
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                symbols = FNO_SYMBOLS if sector == "ALL" else SECTOR_STOCKS.get(sector, [])
                label = "All FnO" if sector == "ALL" else SECTOR_LABELS.get(sector, sector)
                send_message(chat_id, f"⏳ Fetching {label} data...")
                nifty_change = get_nifty_change()
                gainers, losers, breadth = get_movers(symbols, live=True)
                send_message(chat_id, build_message(
                    gainers, losers, breadth,
                    date_label=today,
                    sector=None if sector == "ALL" else sector,
                    nifty_change=nifty_change
                ))
            return jsonify({"ok": True})

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
                "📅 `/fno 29-Apr 9:25` - Any date at time\n"
                "🏷️ `/sector` - Browse by sector (live)\n"
                "🏷️ `/sector bank 29-Apr 9:25` - Sector on any date\n\n"
                "⏰ Auto alert every weekday at 9:25 AM IST"
            )

        elif text_lower.startswith("/sector"):
            parts = full_text.split(maxsplit=1)
            args = parts[1].strip() if len(parts) > 1 else ""

            if not args:
                send_sector_menu(chat_id)
            else:
                arg_parts = args.split(maxsplit=1)
                sector_key = arg_parts[0].upper()
                rest = arg_parts[1] if len(arg_parts) > 1 else ""

                if sector_key not in SECTOR_STOCKS:
                    send_message(chat_id, "❌ Invalid sector! Use: BANK, IT, AUTO, PHARMA, FMCG, METAL, REALTY, ENERGY, FINSERV, PSUBANK")
                    return jsonify({"ok": True})

                symbols = SECTOR_STOCKS[sector_key]
                label = SECTOR_LABELS.get(sector_key, sector_key)

                if not rest:
                    today = datetime.datetime.now(IST).strftime("%d %b %Y")
                    send_message(chat_id, f"⏳ Fetching {label} live data...")
                    nifty_change = get_nifty_change()
                    gainers, losers, breadth = get_movers(symbols, live=True)
                    send_message(chat_id, build_message(gainers, losers, breadth, date_label=today, sector=sector_key, nifty_change=nifty_change))
                else:
                    date_obj, time_obj = parse_input(rest)
                    date_label = date_obj.strftime("%d %b %Y")
                    time_obj = time_obj or datetime.time(15, 30)
                    time_label = time_obj.strftime("%I:%M %p")
                    send_message(chat_id, f"⏳ Fetching {label} for *{date_label}* at *{time_label}*...\n_May take 1-2 mins_")
                    gainers, losers, breadth = get_movers(symbols, date_obj=date_obj, time_obj=time_obj)
                    send_message(chat_id, build_message(gainers, losers, breadth, date_label=date_label, time_label=time_label, sector=sector_key))

 elif text_lower.startswith("/fno"):
            parts = full_text.split(maxsplit=1)
            args = parts[1].strip() if len(parts) > 1 else ""
            if not args:
                send_message(chat_id, "⏳ Fetching live FnO data...")
                nifty_change = get_nifty_change()
                gainers, losers, breadth = get_movers(FNO_SYMBOLS, live=True)
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                send_message(chat_id, build_message(gainers, losers, breadth, date_label=today, nifty_change=nifty_change))
            else:
                date_obj, time_obj = parse_input(args)
                date_label = date_obj.strftime("%d %b %Y")
                time_obj = time_obj or datetime.time(15, 30)
                time_label = time_obj.strftime("%I:%M %p")
                send_message(chat_id, f"⏳ Fetching *{date_label}* at *{time_label}*...\n_May take 2-3 mins_")
                gainers, losers, breadth = get_movers(FNO_SYMBOLS, date_obj=date_obj, time_obj=time_obj)
                send_message(chat_id, build_message(gainers, losers, breadth, date_label=date_label, time_label=time_label))

    except Exception as e:
        print(f"Error: {e}")
        if chat_id:
            send_message(chat_id, f"Error: {str(e)}")
            
    return jsonify({"ok": True})
                
