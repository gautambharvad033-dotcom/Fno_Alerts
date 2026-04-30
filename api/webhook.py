from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"

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

def get_fno_movers():
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
            except:
                continue
    except Exception as e:
        print(f"API error: {e}")
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])
    return gainers[:10], losers[:10]

def build_message(gainers, losers):
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p")

    def make_table(stocks, is_gainer):
        lines = "`#   SYMBOL         LTP        CHG%`\n"
        lines += "`────────────────────────────────`\n"
        for i, (s, l, c) in enumerate(stocks, 1):
            num = str(i).ljust(2)
            symbol = s[:12].ljust(12)
            price = f"₹{l}".ljust(10)
            sign = "+" if is_gainer else ""
            chg = f"{sign}{c:.2f}%"
            lines += f"`{num}  {symbol}  {price}  {chg}`\n"
        return lines if stocks else "`  None`\n"

    g_table = make_table(gainers, True)
    l_table = make_table(losers, False)

    return (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *FnO Top 10 Movers*\n"
        f"🕐 {now} IST\n"
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

    try:
        msg = update.get("message", {})
        text = msg.get("text", "").strip().lower()
        chat_id = msg.get("chat", {}).get("id")

        if not chat_id:
            return jsonify({"ok": True})

        if text == "/start":
            send_message(chat_id,
                "👋 *FnO Alert Bot*\n\n"
                "Commands:\n"
                "📊 /fno — Get top 10 FnO gainers & losers instantly\n"
                "⏰ Auto alert every weekday at 9:25 AM IST"
            )
        elif text == "/fno":
            send_message(chat_id, "⏳ Fetching FnO data, please wait...")
            gainers, losers = get_fno_movers()
            send_message(chat_id, build_message(gainers, losers))

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"ok": True})
