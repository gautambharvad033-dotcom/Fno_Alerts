import requests
import datetime

BOT_TOKEN = "8613392574:AAF83_86w1TGHdYuZF5ZXjwQPJQD8ss7fCM"
CHAT_ID = "7084342720"

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
        "Referer": "https://www.nseindia.com"
    }
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    gainers, losers = [], []
    for symbol in FNO_SYMBOLS:
        try:
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            r = session.get(url, headers={**headers, "Accept": "application/json"}, timeout=10)
            data = r.json()
            ltp = data["priceInfo"]["lastPrice"]
            change_pct = data["priceInfo"]["pChange"]
            if 0 < change_pct < 3:
                gainers.append((symbol, ltp, change_pct))
            elif -3 < change_pct < 0:
                losers.append((symbol, ltp, change_pct))
        except:
            continue
    gainers.sort(key=lambda x: x[2], reverse=True)
    losers.sort(key=lambda x: x[2])
    return gainers[:5], losers[:5]

def build_message(gainers, losers):
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p")
    g_lines = "\n".join([f"  {s}: ₹{l} (+{c:.2f}%)" for s, l, c in gainers]) or "  None"
    l_lines = "\n".join([f"  {s}: ₹{l} ({c:.2f}%)" for s, l, c in losers]) or "  None"
    return (
        f"📊 *FnO Top 5 Movers — {now} IST*\n"
        f"_(Stocks with 0–3% move only)_\n\n"
        f"✅ *Top 5 Gainers:*\n{g_lines}\n\n"
        f"🔴 *Top 5 Losers:*\n{l_lines}"
    )

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    if datetime.datetime.today().weekday() < 5:
        gainers, losers = get_fno_movers()
        send_message(CHAT_ID, build_message(gainers, losers))
        print("Done!")
    else:
        print("Weekend — skipping.")
