'''
This little script allows to send a message with the tickers requested in the dictionary
to a bot and a channel in telegram.

It uses the Yahoo Finance API
'''


import yfinance as yf
import requests
import urllib.parse #this library URL encondes the final message for the bot to publish
import credentials
import datetime

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
    '2':'Miรฉrcoles',
    '3':'Jueves',
    '4':'Viernes',
    '5':'Sรกbado',
    '6':'Domingo'
}
date = '{}, {} de {} de {}'.format(days_of_the_week[str(today.weekday())],
                                   today.day,
                                   months[str(today.month)],
                                   today.year)


'''
The keys in the dictionary below (words on the left) are the numbers that the bot will present, the values
(the words on the right) are the tickers. The tickers are the ones in Yahoo Finance
'''
tickers = {'๐บ๐ธ S&P500': '^GSPC',
           '๐บ๐ธ VIX': '^VIX',
           '๐บ๐ธ Dow Jones': '^DJI',
           '๐บ๐ธ NASDAQ': '^IXIC',
           '๐บ๐ธ Russell 2000': '^RUT',
           '๐ฌ๐ง FTSE 100': '^FTSE',
           '๐ช๐บ Euro Stoxx': '^STOXX50E',
           '๐ฉ๐ช DAX 30': '^GDAXI',
           '๐ซ๐ท CAC 40': '^FCHI',
           '๐ช๐ธ IBEX 35': '^IBEX',
           '๐ฏ๐ต Nikkei 225': '^N225',
           '๐จ๐ณ SSE': '000001.SS',
           '๐ญ๐ฐ Hang Seng': '^HSI',
           '๐ฎ๐ณ Nifty 50': '^NSEI'
            }


data = '' #this string will append the information generated below

# the below extracts the closing values of the tickers and creates the data string

for i in range(0, len(tickers)):
    company = str(list(tickers.keys())[i])
    ticker = str(list(tickers.values())[i])
    name = yf.Ticker(ticker)
    name_today = float(name.history()['Close'].values[-1])
    name_yesterday = float(name.history()['Close'].values[-2])
    name_difference: str = "%.2f" % float(abs(name_today - name_yesterday))
    if (name_today - name_yesterday) > 0:
        name_difference = '+' + name_difference
        if ticker == '^VIX': #for the VIX index, going high is bad and viceversa
            name_difference_emoji = '๐ด'
        else:
            name_difference_emoji = '๐ข'
    elif (name_today - name_yesterday) < 0:
        name_difference = '-' + name_difference
        if ticker == '^VIX':
            name_difference_emoji = '๐ข'
        else:
            name_difference_emoji = '๐ด'
    else:
        name_difference = name_difference
        name_difference_emoji = 'โ๏ธ'
    name_percentage = "%.2f" % float((name_today / name_yesterday) * 100 - 100)
    if float(name_percentage) > 0:
        name_percentage = '+' + name_percentage
    else:
        name_percentage = name_percentage
    data += '`{0:.<15} {1:>8.2f} | {2:>8} | {3:>6}% {4}`\n'.format(company,
                                                           name_today,
                                                           name_difference,
                                                           name_percentage,
                                                           name_difference_emoji)


#print(data)


# the function below sends the message through telegram.

def telegram_bot_sendtext(bot_message):
  bot_token =  credentials.bot_token
  bot_chatID = credentials.bot_chatID
  send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=markdown&text=' + bot_message
  response = requests.get(send_text)
  return response.json()


telegram_bot_sendtext('*Resumen automรกtico de mercados:*\n\n' + date + '\n\n' + urllib.parse.quote(data)) #urllib.parse.quote URL encodes the message
