import yfinance as yf
import requests
import credentials
import datetime
from time import sleep

# -----------------------------
# DATE FORMATTING (SPANISH)
# -----------------------------
today = datetime.datetime.now()

months = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

days_of_the_week = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

date_str = f"{days_of_the_week[today.weekday()]}, {today.day} de {months[today.month]} de {today.year}"

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

# -----------------------------
# DATA FETCHING (ROBUST)
# -----------------------------
def get_last_two_closes(ticker):
    try:
        hist = yf.Ticker(ticker).history(period='10d')
        hist = hist.dropna(subset=['Close'])

        if len(hist) < 2:
            return None

        last = hist.iloc[-1]
        prev = hist.iloc[-2]

        return {
            "last_close": float(last['Close']),
            "prev_close": float(prev['Close']),
            "last_date": last.name.date()
        }

    except Exception:
        return None

# -----------------------------
# BUILD MESSAGE
# -----------------------------
lines = []

for name, ticker in tickers.items():
    info = get_last_two_closes(ticker)

    if not info:
        lines.append(f"{name:.<18} {'N/A':>8} | {'N/A':>8} | {'N/A':>6}% ❌")
        continue

    last_close = info["last_close"]
    prev_close = info["prev_close"]
    last_date = info["last_date"]

    delta = last_close - prev_close
    pct = (delta / prev_close) * 100

    delta_str = f"{delta:+.2f}"
    pct_str = f"{pct:+.2f}"

    if delta > 0:
        emoji = '🔴' if ticker == '^VIX' else '🟢'
    elif delta < 0:
        emoji = '🟢' if ticker == '^VIX' else '🔴'
    else:
        emoji = '↔️'

    days_ago = (today.date() - last_date).days
    session_tag = f"D-{days_ago}"

    lines.append(
        f"{name:.<18} {last_close:>8.2f} | {delta_str:>8} | {pct_str:>6}% {emoji} {session_tag}"
    )

data_block = "\n".join(lines)

# -----------------------------
# TELEGRAM (HTML, NO DRAMA)
# -----------------------------
def telegram_bot_sendtext(message):
    url = f"https://api.telegram.org/bot{credentials.bot_token}/sendMessage"
    payload = {
        "chat_id": credentials.bot_chatID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# -----------------------------
# SEND
# -----------------------------
final_message = (
    f"<b>Resumen de mercados</b>\n\n"
    f"{date_str}\n\n"
    f"<pre>{data_block}</pre>"
)

telegram_bot_sendtext(final_message)
