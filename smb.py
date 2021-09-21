'''
This little script allows to send a message with the tickers requested in the dictionary
to a bot and a channel in telegram.

It uses the Yahoo Finance API
'''


import yfinance as yf
import requests
import urllib.parse #this library URL encondes the final message for the bot to publish
import credentials

'''
The keys in the dictionary below (words on the left) are the numbers that the bot will present, the values
(the words on the right) are the tickers. The tickers are the ones in Yahoo Finance
'''
tickers = {'S&P500': '^GSPC',
           'Dow Jones': '^DJI',
           'NASDAQ': '^IXIC',
           'FTSE 100': '^FTSE',
           'DAX 30': '^GDAXI',
           'CAC 40': '^FCHI',
           'IBEX 35': '^IBEX',
           'Nikkei 225': '^N225'}


data = '' #this string will append the information generated below

# the below extracts the closing values of the tickers and creates the data string

for i in range(0, len(tickers)):
    company = str(list(tickers.keys())[i])
    ticker = str(list(tickers.values())[i])
    name = yf.Ticker(ticker)
    name_today = round(float(name.history(period="2d")['Close'].values[-1]),2)
    name_yesterday = round(float(name.history(period="2d")['Close'].values[-2]),2)
    name_difference = "%.2f" % float(name_today - name_yesterday)
    if (name_today - name_yesterday) > 0:
      name_difference = '+' + name_difference
    else:
      name_difference = name_difference
    name_percentage = "%.2f" % float((name_today / name_yesterday) * 100 - 100)
    if float(name_percentage) > 0:
      name_percentage = '+' + name_percentage
    else:
      name_percentage = name_percentage
    data += '*{}* {} | {} | {}%\n'.format(company, name_today, name_difference, name_percentage)
    # print('{} {} | {} | {}%'.format(company, name_today,name_difference,name_percentage))

#print(data)


# the function below sends the message through telegram.

def telegram_bot_sendtext(bot_message):
  bot_token =  credentials.bot_token
  bot_chatID = credentials.bot_chatID
  send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=markdown&text=' + bot_message
  response = requests.get(send_text)
  return response.json()


telegram_bot_sendtext('Resumen automático de mercados:\n\n' + urllib.parse.quote(data)) #urllib.parse.quote URL encodes the message
