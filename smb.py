import yfinance as yf
import requests
import credentials
import datetime
import json
import os

# -----------------------------
# FORCE BROWSER-LIKE SESSION
# -----------------------------
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
})
yf.utils.get_yf_r_session = lambda: session

# -----------------------------
# DATE (SPANISH)
# -----------------------------
now = datetime.datetime.now()

months = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

days = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

date_str = f"{days[now.weekday()]}, {now.day} de {months[now.month]} de {now.year}"

# -----------------------------
# TICKERS
# -----------------------------
tickers = {
    '🇺🇸 S&P500': '^GSPC',
    '🇺🇸 VIX': '^VIX',
    '🇺🇸 Dow Jones': '^DJI',
    '🇺🇸 NASDAQ': '^IXIC',
    '🇺🇸 Russell 2000': '^RUT',
    '🇬🇧 FTSE 100': '^FTSE',
    '🇪🇺 Euro Stoxx': '^STOXX50E',
    '🇩🇪 DAX 30': '^GDAXI',
    '🇫🇷 CAC 40': '^FCHI',
    '🇪🇸 IBEX 35': '^IBEX',
    '🇯🇵 Nikkei 225': '^N225',
    '🇨🇳 SSE': '000001.SS',
    '🇭🇰 Hang Seng': '^HSI',
    '🇮🇳 Nifty 50': '^NSEI'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "cache.json")

# -----------------------------
# BULK FETCH
# -----------------------------
def fetch_market_data():
    symbols = list(tickers.values())

    try:
        raw = yf.download(
            tickers=" ".join(symbols),
            period="10d",
            group_by="ticker",
            threads=False,
            progress=False
        )
    except Exception:
        return None

    results = {}

    for name, ticker in tickers.items():
        try:
            df = raw[ticker].dropna(subset=['Close'])
            if len(df) < 2:
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]

            results[name] = {
                "ticker": ticker,
                "last_close": float(last["Close"]),
                "prev_close": float(prev["Close"]),
                "last_date": last.name.strftime("%Y-%m-%d")
            }
        except Exception:
            continue

    return results if results else None

# -----------------------------
# LOAD / SAVE CACHE
# -----------------------------
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def save_cache(data):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

# -----------------------------
# GET DATA (LIVE OR CACHE)
# -----------------------------
market_data = fetch_market_data()
cached = False

if market_data:
    save_cache(market_data)
else:
    market_data = load_cache()
    cached = True

# -----------------------------
# BUILD OUTPUT
# -----------------------------
lines = []

for name, ticker in tickers.items():
    info = market_data.get(name) if market_data else None

    if not info:
        lines.append(f"{name:.<18} {'N/A':>8} | {'N/A':>8} | {'N/A':>6}% ❌")
        continue

    last_close = info["last_close"]
    prev_close = info["prev_close"]
    last_date = datetime.datetime.strptime(info["last_date"], "%Y-%m-%d").date()

    delta = last_close - prev_close
    pct = (delta / prev_close) * 100

    delta_str = f"{delta:+.2f}"
    pct_str = f"{pct:+.2f}"

    if delta > 0:
        emoji = '🔴' if info["ticker"] == '^VIX' else '🟢'
    elif delta < 0:
        emoji = '🟢' if info["ticker"] == '^VIX' else '🔴'
    else:
        emoji = '↔️'

    days_ago = (now.date() - last_date).days
    session_tag = f"D-{days_ago}"

    lines.append(
        f"{name:.<18} {last_close:>8.2f} | {delta_str:>8} | {pct_str:>6}% {emoji} {session_tag}"
    )

data_block = "\n".join(lines)

# -----------------------------
# TELEGRAM SEND (HTML)
# -----------------------------
def telegram_send(msg):
    url = f"https://api.telegram.org/bot{credentials.bot_token}/sendMessage"
    payload = {
        "chat_id": credentials.bot_chatID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload, timeout=10)

header = "<b>Resumen de mercados</b>"
if cached:
    header += " ⚠️ <i>(datos en caché)</i>"

code_lines = "\n".join(f"<code>{line}</code>" for line in lines)

final_message = (
    f"{header}\n\n"
    f"{date_str}\n\n"
    f"{code_lines}"
)

telegram_send(final_message)
