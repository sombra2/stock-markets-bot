import yfinance as yf
import requests
import urllib.parse
import credentials
import datetime
from time import sleep

today = datetime.datetime.now()
months = {
    '1':'Enero',
    '2':'Febrero',
    '3':'Marzo',
    '4':'Abril',
    '5':'Mayo',
    '6':'Junio',
    '7':'Julio',
    '8':'Agosto',
    '9':'Septiembre',
    '10':'Octubre',
    '11':'Noviembre',
    '12':'Diciembre'
}
days_of_the_week = {
    '0':'Lunes',
    '1':'Martes',
    '2':'Miércoles',
    '3':'Jueves',
    '4':'Viernes',
    '5':'Sábado',
    '6':'Domingo'
}
date = '{}, {} de {} de {}'.format(days_of_the_week[str(today.weekday())],
                                   today.day,
                                   months[str(today.month)],
                                   today.year)

tickers = {'🇺🇸 S&P500': '^GSPC',
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

data = ''

def get_ticker_data(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Try getting data with a larger period to ensure we get recent data
            hist = yf.Ticker(ticker).history(period='5d')
            if len(hist) < 2:
                raise ValueError("Not enough data points")
            return hist
        except Exception as e:
            if attempt < max_retries - 1:
                sleep(2)  # Wait before retrying
                continue
            print(f"Failed to fetch data for {ticker} after {max_retries} attempts: {str(e)}")
            return None

for i in range(len(tickers)):
    company = str(list(tickers.keys())[i])
    ticker = str(list(tickers.values())[i])
    
    hist = get_ticker_data(ticker)
    if hist is None or len(hist) < 2:
        data += f'`{company:.<15} {"N/A":>8} | {"N/A":>8} | {"N/A":>6}% ❌`\n'
        continue
    
    try:
        name_today = float(hist['Close'].values[-1])
        name_yesterday = float(hist['Close'].values[-2])
        
        name_difference = "%.2f" % float(abs(name_today - name_yesterday))
        if (name_today - name_yesterday) > 0:
            name_difference = '+' + name_difference
            if ticker == '^VIX':
                name_difference_emoji = '🔴'
            else:
                name_difference_emoji = '🟢'
        elif (name_today - name_yesterday) < 0:
            name_difference = '-' + name_difference
            if ticker == '^VIX':
                name_difference_emoji = '🟢'
            else:
                name_difference_emoji = '🔴'
        else:
            name_difference = name_difference
            name_difference_emoji = '↔️'
            
        name_percentage = "%.2f" % float((name_today / name_yesterday) * 100 - 100)
        if float(name_percentage) > 0:
            name_percentage = '+' + name_percentage
        else:
            name_percentage = name_percentage
            
        data += '`{0:.<15} {1:>8.2f} | {2:>8} | {3:>6}% {4}`\n'.format(
            company, name_today, name_difference, name_percentage, name_difference_emoji)
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        data += f'`{company:.<15} {"ERROR":>8} | {"ERROR":>8} | {"ERROR":>6}% ❌`\n'

def telegram_bot_sendtext(bot_message):
    bot_token = credentials.bot_token
    bot_chatID = credentials.bot_chatID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=markdown&text=' + bot_message
    try:
        response = requests.get(send_text, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Failed to send Telegram message: {str(e)}")
        return None

telegram_bot_sendtext('*Resumen de mercados:*\n\n' + date + '\n\n' + urllib.parse.quote(data))
