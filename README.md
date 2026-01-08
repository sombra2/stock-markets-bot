# Stock Markets Telegram Bot

A lightweight Python script that generates a daily global market summary and sends it to Telegram.

Designed to run unattended every weekday morning (07:00).  
The bot reports the **last completed trading session** for major global indices and is resilient to weekends, holidays, and data-source instability.

---

## Features

- 🌍 Covers major global indices (US, Europe, Asia)
- ⏰ Designed for **07:00 morning runs**
- 📉 Compares the **last two completed trading sessions**
- 🧠 Automatically handles weekends and market holidays
- 🛡️ Hardened against Yahoo Finance outages and throttling
- 💾 Uses local caching to avoid empty or broken reports
- 📲 Sends formatted output to Telegram
- 🎯 Clean monospace formatting without Telegram block quotes

---

## Example Output

```text
🇺🇸 S&P500......... 6920.93 | -23.89 | -0.34% 🔴 (D-1)
🇺🇸 VIX............   15.76 |  +0.38 | +2.47% 🔴 (D-0)
🇯🇵 Nikkei 225..... 51117.26 | -844.72 | -1.63% 🔴 (D-0)
```

`(D-0, D-1, etc. indicate how many days ago the last trading session occurred)`

---

## How It Works

1. Fetches historical market data in bulk using `yfinance`
2. Drops incomplete or invalid sessions
3. Compares the last two valid closing prices
4. Calculates absolute and percentage changes
5. Applies market-aware emoji indicators (including inverted logic for VIX)
6. Falls back to cached data if live data is unavailable
7. Sends a formatted summary to Telegram

---

## Requirements

- Python 3.9+
- A Telegram Bot Token
- Internet access

Python dependencies:

```text
yfinance
requests
```

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/stock-markets-telegram-bot.git
cd stock-markets-telegram-bot
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install yfinance requests
```

---

## Configuration

Create a `credentials.py` file in the project root:

```python
bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
bot_chatID = "YOUR_CHAT_ID"
```

---

## Running Manually

```bash
python3 smb.py
```

On the first successful run, a `cache.json` file will be created automatically.

---

## Cron Setup (Recommended)

Run every weekday at 07:00:

```text
0 7 * * 1-5 /usr/bin/python3 /path/to/smb.py
```

This timing ensures the report reflects the **most recent completed trading session** for each market.

---

## Caching Behavior

- If Yahoo Finance is unreachable or throttles requests, the bot uses cached data
- Cached reports are clearly marked in Telegram
- Prevents empty or misleading reports

---

## Known Limitations

- Relies on Yahoo Finance (unofficial, best-effort data source)
- Not intended for trading or financial decision-making
- Accuracy depends on data availability per market

---

## License

MIT License.  
Use it, modify it, break it, improve it. Just don’t blame the bot.

---

## Disclaimer

This project is for informational purposes only.  
It is **not** financial advice.
