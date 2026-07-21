from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"

SECTOR_STOCKS = {
    "BANK": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","BANDHANBNK","FEDERALBNK","IDFCFIRSTB","INDUSINDBK","BANKBARODA","PNB","CANBK","UNIONBANK","INDIANB","RBLBANK","YESBANK","AUBANK","BANKINDIA"],
    "IT": ["TCS","INFY","HCLTECH","WIPRO","TECHM","MPHASIS","COFORGE","PERSISTENT","OFSS","KPITTECH"],
    "AUTO": ["MARUTI","BAJAJ-AUTO","TVSMOTOR","EICHERMOT","HEROMOTOCO","ASHOKLEY","MOTHERSON","BHARATFORG","BOSCHLTD","UNOMINDA","TIINDIA","HYUNDAI"],
    "PHARMA": ["SUNPHARMA","DRREDDY","CIPLA","LUPIN","AUROPHARMA","DIVISLAB","ALKEM","GLENMARK","LAURUSLABS","BIOCON","ZYDUSLIFE","MANKIND"],
    "FMCG": ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","MARICO","COLPAL","GODREJCP","TATACONSUM","VBL","PATANJALI"],
    "METAL": ["TATASTEEL","JSWSTEEL","HINDALCO","VEDL","SAIL","NMDC","NATIONALUM","HINDZINC","COALINDIA","APLAPOLLO"],
    "REALTY": ["DLF","GODREJPROP","OBEROIRLTY","PHOENIXLTD","LODHA","PRESTIGE"],
    "ENERGY": ["RELIANCE","ONGC","BPCL","IOC","HINDPETRO","GAIL","OIL","PETRONET","ADANIGREEN","TATAPOWER","ADANIPOWER","NTPC","POWERGRID","NHPC","ADANIENSOL","WAAREEENER","INOXWIND","SOLARINDS","POWERINDIA"],
    "FINSERV": ["BAJFINANCE","BAJAJFINSV","HDFCLIFE","SBILIFE","ICICIGI","ICICIPRULI","MUTHOOTFIN","CHOLAFIN","SHRIRAMFIN","MANAPPURAM","PNBHOUSING","LICHSGFIN","MFSL","HDFCAMC","ABCAPITAL","IRFC","RECLTD","PFC","IREDA","LTF","ANGELONE","MOTILALOFS","JIOFIN"],
    "PSUBANK": ["SBIN","BANKBARODA","PNB","CANBK","UNIONBANK","INDIANB","BANKINDIA","MAZDOCK","BDL","COCHINSHIP"]
}

FNO_SYMBOLS = list(set([s for stocks in SECTOR_STOCKS.values() for s in stocks] + [
    "ETERNAL","ADANIPORTS","INDUSTOWER","KAYNES","FORCEMOT","BHEL","BHARATFORG","PAYTM","BEL","TRENT","HAL",
    "HAVELLS","GODFRYPHLP","SONACOMS","KEI","POLYCAB","NAUKRI","CDSL","TITAN","RVNL","MAXHEALTH","APOLLOHOSP",
    "ABB","JSWENERGY","SBICARD","EXIDEIND","GRASIM","CUMMINSIND","ASTRAL","BLUESTARCO","KALYANKJIL","TATAELXSI",
    "AMBER","SUPREMEIND","JINDALSTEL","JUBLFOOD","CONCOR","PIIND","VOLTAS","INDHOTEL","GMRAIRPORT","PGEL","DMART",
    "IEX","LICI","UNITDSPR","VMM","DALBHARAT","SIEMENS","TORNTPHARM","PREMIERENE","AMBUJACEM","NBCC","CAMS","UPL",
    "FORTIS","DELHIVERY","TIINDIA","NYKAA","PAGEIND","KFINTECH","PIDILITIND","SHREECEM","BAJAJHLDNG","NUVAMA",
    "DIXON","SUZLON","ADANIENT","SWIGGY","SAMMAANCAP","TMPV","INDIGO","MCX","CROMPTON","SHRIRAMFIN","POLICYBZR",
    "CGPOWER","HINDPETRO","SOLARINDS","SRF","DIVISLAB","PNBHOUSING","MPHASIS","LTM","LICHSGFIN","INOXWIND",
    "TATACONSUM","ZYDUSLIFE","APLAPOLLO","COLPAL","PRESTIGE","MARICO","ICICIPRULI","GODREJCP","PATANJALI","DABUR",
    "MARUTI","COCHINSHIP","OFSS","VBL","NATIONALUM","HINDZINC","NESTLEIND","LODHA","ADANIENSOL","SAIL","TATAPOWER",
    "ULTRACEMCO","EICHERMOT","OIL","NMDC","NHPC","BDL","FEDERALBNK","COFORGE","MAXHEALTH","JSWENERGY","GODREJPROP",
    "DLF","ASIANPAINT","PETRONET","BAJAJFINSV","ANGELONE","IREDA","GMRAIRPORT","BANKINDIA","DALBHARAT","PHOENIXLTD",
    "NBCC","FORTIS","ICICIGI","MANKIND","ALKEM","NUVAMA","AMBUJACEM"
]))

YAHOO_SPECIAL = {"BAJAJ-AUTO":"BAJAJ-AUTO.NS","NAM-INDIA":"NAM-INDIA.NS","360ONE":"360ONE.NS","M&M":"M%26M.NS"}

SECTOR_LABELS = {
    "BANK":"ðŸ¦ Bank","IT":"ðŸ’» IT","AUTO":"ðŸš— Auto","PHARMA":"ðŸ’Š Pharma","FMCG":"ðŸ›’ FMCG",
    "METAL":"âš™ï¸ Metal","REALTY":"ðŸ¢ Realty","ENERGY":"âš¡ Energy","FINSERV":"ðŸ’° Fin Serv","PSUBANK":"ðŸ›ï¸ PSU Bank"
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
        hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, params=params, headers=hdrs, timeout=10)
        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return None, None
        timestamps = result[0].get("timestamp", [])
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        prev_close = result[0].get("meta", {}).get("chartPreviousClose", None)
        if not timestamps or not closes or prev_close is None:
            return None, None
        hour = time_obj.hour
        minute = time_obj.minute
        if hour == 9 and minute == 15:
            minute = 16
        target_seconds = hour * 3600 + minute * 60
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
        hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://www.nseindia.com", "Accept": "application/json"}
        session.get("https://www.nseindia.com", headers=hdrs, timeout=10)
        try:
            r = session.get("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O", headers=hdrs, timeout=10)
            stock_map = {s.get("symbol"): s for s in r.json().get("data", [])}
            for symbol in symbols:
                if symbol in stock_map:
                    s = stock_map[symbol]
                    all_stocks.append((symbol, s.get("lastPrice", 0), s.get("pChange", 0)))
        except Exception as e:
            print(f"Live API error: {e}")
    else:
        for symbol in symbols:
            ltp, chg = get_price_at_time_yahoo(symbol, date_obj, time_obj)
            if ltp is not None:
                all_stocks.append((symbol, ltp, chg))

    advances = sum(1 for _, _, c in all_stocks if c > 0)
    declines = sum(1 for _, _, c in all_stocks if c < 0)
    unchanged = len(all_stocks) - advances - declines
    all_g = sorted([s for s in all_stocks if s[2] > 0], key=lambda x: x[2], reverse=True)
    all_l = sorted([s for s in all_stocks if s[2] < 0], key=lambda x: x[2])
    gainers = sorted([s for s in all_stocks if 0 < s[2] < 3], key=lambda x: x[2], reverse=True)
    losers = sorted([s for s in all_stocks if -3 < s[2] < 0], key=lambda x: x[2])
    breadth = {"advances": advances, "declines": declines, "unchanged": unchanged, "total": len(all_stocks),
               "top_gainer": all_g[0] if all_g else None, "top_loser": all_l[0] if all_l else None}
    return gainers[:10], losers[:10], breadth


def get_nifty_change():
    try:
        session = requests.Session()
        hdrs = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com", "Accept": "application/json"}
        session.get("https://www.nseindia.com", headers=hdrs, timeout=10)
        r = session.get("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050", headers=hdrs, timeout=10)
        for s in r.json().get("data", []):
            if s.get("symbol") == "NIFTY 50":
                return s.get("pChange", 0)
    except Exception:
        pass
    return None


def get_all_sectors_snapshot():
    session = requests.Session()
    hdrs = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com", "Accept": "application/json"}
    session.get("https://www.nseindia.com", headers=hdrs, timeout=10)
    try:
        r = session.get("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O", headers=hdrs, timeout=10)
        stock_map = {s.get("symbol"): s for s in r.json().get("data", [])}
    except Exception:
        return []
    results = []
    for sector, symbols in SECTOR_STOCKS.items():
        advances = declines = unchanged = count = 0
        total_change = 0
        for symbol in symbols:
            if symbol in stock_map:
                chg = stock_map[symbol].get("pChange", 0)
                if chg > 0: advances += 1
                elif chg < 0: declines += 1
                else: unchanged += 1
                total_change += chg
                count += 1
        avg = total_change / count if count > 0 else 0
        results.append({"sector": sector, "advances": advances, "declines": declines, "unchanged": unchanged, "total": count, "avg_change": avg})
    results.sort(key=lambda x: x["avg_change"], reverse=True)
    return results


def get_verdict(advances, declines):
    total = advances + declines
    if total == 0: return "No data"
    ratio = advances / total * 100
    if ratio >= 70: return "STRONGLY BULLISH"
    elif ratio >= 55: return "BULLISH"
    elif ratio >= 45: return "NEUTRAL"
    elif ratio >= 30: return "BEARISH"
    else: return "STRONGLY BEARISH"


def build_sectors_snapshot(sectors_data, date_label):
    lines = ""
    for s in sectors_data:
        label = SECTOR_LABELS.get(s["sector"], s["sector"])
        avg = s["avg_change"]
        emoji = "ðŸŸ¢" if avg > 0 else "ðŸ”´"
        sign = "+" if avg > 0 else ""
        lines += f"{emoji} {label:<14}  A:{s['advances']}  D:{s['declines']}  {sign}{avg:.2f}%\n"
    return f"ðŸ“Š *Sector Snapshot*\nðŸ“… {date_label}\n\n{lines}\n_Tap /sector to drill into any sector_"


def build_message(gainers, losers, breadth, date_label, time_label=None, sector=None, nifty_change=None):
    time_str = f" at {time_label}" if time_label else ""
    sector_label = SECTOR_LABELS.get(sector, "All FnO") if sector else "All FnO"
    adv = breadth.get("advances", 0)
    dec = breadth.get("declines", 0)
    unc = breadth.get("unchanged", 0)
    total = breadth.get("total", 0)
    top_g = breadth.get("top_gainer")
    top_l = breadth.get("top_loser")
    verdict = get_verdict(adv, dec)
    nifty_line = ""
    if nifty_change is not None:
        sign = "+" if nifty_change > 0 else ""
        emoji = "ðŸŸ¢" if nifty_change > 0 else "ðŸ”´"
        nifty_line = f"{emoji} Nifty: {sign}{nifty_change:.2f}%\n"
    top_g_line = f"ðŸ† Top Gainer: {top_g[0]} +{top_g[2]:.2f}%\n" if top_g else ""
    top_l_line = f"ðŸ’€ Top Loser:  {top_l[0]} {top_l[2]:.2f}%\n" if top_l else ""
    breadth_section = (f"ðŸ“Š *{sector_label} Breadth* ({total} stocks)\n{nifty_line}"
                       f"ðŸ“ˆ Advances: {adv}   ðŸ“‰ Declines: {dec}   âž¡ï¸ {unc} Unchanged\n"
                       f"ðŸ“Š Ratio: {adv}:{dec}\n{top_g_line}{top_l_line}ðŸŽ¯ Verdict: *{verdict}*")

    def make_table(stocks, is_gainer):
        lines = "`#   SYMBOL         LTP        CHG%`\n`â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€`\n"
        for i, (s, l, c) in enumerate(stocks, 1):
            sign = "+" if is_gainer else ""
            lines += f"`{str(i).ljust(2)}  {s[:12].ljust(12)}  {'Rs'+str(l):<10}  {sign}{c:.2f}%`\n"
        return lines if stocks else "`  None`\n"

    return (f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\nðŸ“Š *{sector_label} â€” Top 10 Movers*\n"
            f"ðŸ“… {date_label}{time_str}\n_(0% to 3% move only)_\nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            f"{breadth_section}\n\nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\nâœ… *TOP 10 GAINERS* ðŸ“ˆ\n"
            f"{make_table(gainers, True)}\nðŸ”´ *TOP 10 LOSERS* ðŸ“‰\n"
            f"{make_table(losers, False)}\nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”")


def parse_input(text):
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    today = datetime.datetime.now(IST)
    date_obj = today
    time_obj = None
    parts = text.strip().split()
    if parts:
        for fmt in ["%d-%m-%Y", "%d-%b-%Y", "%d-%b", "%Y-%m-%d"]:
            try:
                dt = datetime.datetime.strptime(parts[0], fmt)
                if fmt == "%d-%b": dt = dt.replace(year=today.year)
                date_obj = dt
                break
            except Exception:
                continue
    if len(parts) >= 2:
        for fmt in ["%H:%M", "%I:%M"]:
            try:
                time_obj = datetime.datetime.strptime(parts[1], fmt).time()
                break
            except Exception:
                continue
    return date_obj, time_obj


def send_msg(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})


def send_buttons(chat_id, text, buttons):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown",
                        "reply_markup": {"inline_keyboard": buttons}})


def sector_menu(chat_id):
    buttons = [
        [{"text": "ðŸ¦ Bank", "callback_data": "sector_BANK"},
         {"text": "ðŸ’» IT", "callback_data": "sector_IT"},
         {"text": "ðŸš— Auto", "callback_data": "sector_AUTO"}],
        [{"text": "ðŸ’Š Pharma", "callback_data": "sector_PHARMA"},
         {"text": "ðŸ›’ FMCG", "callback_data": "sector_FMCG"},
         {"text": "âš™ï¸ Metal", "callback_data": "sector_METAL"}],
        [{"text": "ðŸ¢ Realty", "callback_data": "sector_REALTY"},
         {"text": "âš¡ Energy", "callback_data": "sector_ENERGY"},
         {"text": "ðŸ’° Fin Serv", "callback_data": "sector_FINSERV"}],
        [{"text": "ðŸ›ï¸ PSU Bank", "callback_data": "sector_PSUBANK"},
         {"text": "ðŸ“Š All FnO", "callback_data": "sector_ALL"}]
    ]
    send_buttons(chat_id, "ðŸ·ï¸ *Select a Sector:*\nTap any sector to get live top gainers and losers!", buttons)


def answer_callback(callback_id):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                  json={"callback_query_id": callback_id})


@app.route("/api/webhook", methods=["GET"])
def home():
    return "FnO Bot is running! âœ…", 200


@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    chat_id = None
    try:
        IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

        if "callback_query" in update:
            callback = update["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            data = callback.get("data", "")
            answer_callback(callback["id"])
            if data.startswith("sector_"):
                sector = data.replace("sector_", "")
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                symbols = FNO_SYMBOLS if sector == "ALL" else SECTOR_STOCKS.get(sector, [])
                label = "All FnO" if sector == "ALL" else SECTOR_LABELS.get(sector, sector)
                send_msg(chat_id, f"â³ Fetching {label} data...")
                gainers, losers, breadth = get_movers(symbols, live=True)
                send_msg(chat_id, build_message(gainers, losers, breadth, date_label=today,
                         sector=None if sector == "ALL" else sector, nifty_change=get_nifty_change()))
            return jsonify({"ok": True})

        msg = update.get("message", {})
        full_text = msg.get("text", "").strip()
        text_lower = full_text.lower()
        chat_id = msg.get("chat", {}).get("id")
        if not chat_id:
            return jsonify({"ok": True})

        if text_lower == "/sectors":
            send_msg(chat_id, "â³ Fetching all sectors snapshot...")
            today = datetime.datetime.now(IST).strftime("%d %b %Y")
            send_msg(chat_id, build_sectors_snapshot(get_all_sectors_snapshot(), today))

        elif text_lower == "/start":
            send_msg(chat_id,
                "ðŸ‘‹ *FnO Alert Bot*\n\n*Commands:*\n"
                "ðŸ“Š `/fno` - Today live top 10\n"
                "ðŸ“… `/fno 29-Apr 9:25` - Any date at time\n"
                "ðŸ“ˆ `/sectors` - All sectors snapshot\n"
                "ðŸ·ï¸ `/sector` - Browse by sector\n"
                "ðŸ·ï¸ `/sector bank 29-Apr 9:25` - Sector on any date\n\n"
                "â° Auto alert every weekday at 9:25 AM IST\n"
                "_Note: Use 9:16 for first candle data_"
            )

        elif text_lower.startswith("/sector"):
            parts = full_text.split(maxsplit=1)
            args = parts[1].strip() if len(parts) > 1 else ""
            if not args:
                sector_menu(chat_id)
            else:
                arg_parts = args.split(maxsplit=1)
                sector_key = arg_parts[0].upper()
                rest = arg_parts[1] if len(arg_parts) > 1 else ""
                if sector_key not in SECTOR_STOCKS:
                    send_msg(chat_id, "Invalid sector! Use: BANK, IT, AUTO, PHARMA, FMCG, METAL, REALTY, ENERGY, FINSERV, PSUBANK")
                    return jsonify({"ok": True})
                symbols = SECTOR_STOCKS[sector_key]
                label = SECTOR_LABELS.get(sector_key, sector_key)
                if not rest:
                    today = datetime.datetime.now(IST).strftime("%d %b %Y")
                    send_msg(chat_id, f"â³ Fetching {label} live data...")
                    gainers, losers, breadth = get_movers(symbols, live=True)
                    send_msg(chat_id, build_message(gainers, losers, breadth, date_label=today,
                             sector=sector_key, nifty_change=get_nifty_change()))
                else:
                    date_obj, time_obj = parse_input(rest)
                    date_label = date_obj.strftime("%d %b %Y")
                    time_obj = time_obj or datetime.time(15, 30)
                    time_label = time_obj.strftime("%I:%M %p")
                    send_msg(chat_id, f"â³ Fetching {label} for *{date_label}* at *{time_label}*...")
                    gainers, losers, breadth = get_movers(symbols, date_obj=date_obj, time_obj=time_obj)
                    send_msg(chat_id, build_message(gainers, losers, breadth, date_label=date_label,
                             time_label=time_label, sector=sector_key))

        elif text_lower.startswith("/fno"):
            parts = full_text.split(maxsplit=1)
            args = parts[1].strip() if len(parts) > 1 else ""
            if not args:
                send_msg(chat_id, "â³ Fetching live FnO data...")
                gainers, losers, breadth = get_movers(FNO_SYMBOLS, live=True)
                today = datetime.datetime.now(IST).strftime("%d %b %Y")
                send_msg(chat_id, build_message(gainers, losers, breadth, date_label=today,
                         nifty_change=get_nifty_change()))
            else:
                date_obj, time_obj = parse_input(args)
                date_label = date_obj.strftime("%d %b %Y")
                time_obj = time_obj or datetime.time(15, 30)
                time_label = time_obj.strftime("%I:%M %p")
                send_msg(chat_id, f"â³ Fetching *{date_label}* at *{time_label}*...\n_May take 2-3 mins_")
                gainers, losers, breadth = get_movers(FNO_SYMBOLS, date_obj=date_obj, time_obj=time_obj)
                send_msg(chat_id, build_message(gainers, losers, breadth, date_label=date_label,
                         time_label=time_label))

    except Exception as e:
        print(f"Error: {e}")
        if chat_id:
            send_msg(chat_id, f"Error: {str(e)}")

    return jsonify({"ok": True})
