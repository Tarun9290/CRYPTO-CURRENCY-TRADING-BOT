#CRYPTOCURRENCY TRADING BOT CODE IN PYTHON

# Imports 
import requests
import json
import pandas as pd
import numpy as np
import talib

# Authenticate with the API 
API_KEY = 'Your API Key'
# Set URL for API calls
BASE_URL = 'https://api.cryptowat.ch/'

# Get historical data from exchange
def get_historical_data(exchange, pair, period):
  # Make the request
  req_url = BASE_URL + 'markets/{}/{}/ohlc'.format(exchange, pair)
  params = {'periods': period}
  response = requests.get(req_url, params=params, headers={'Content-Type': 'application/json', 'X-API-Key': API_KEY})
  
  # Parse the response
  response_json = json.loads(response.text)
  data = response_json['result'][str(period)]
  df = pd.DataFrame(data, columns = ['CloseTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'Volume', 'NA'])
  
  # Convert the Unix timestamps to datetime objects
  df['CloseTime'] = pd.to_datetime(df['CloseTime'], unit='s')
  
  # Set the datetime column as the index
  df.set_index('CloseTime', inplace=True)
  df.drop('NA', axis=1, inplace=True)
  
  return df
  
# Get current price of the pair
def get_current_price(exchange, pair):
  # Make the request
  req_url = BASE_URL + 'markets/{}/{}/price'.format(exchange, pair)
  response = requests.get(req_url, headers={'Content-Type': 'application/json', 'X-API-Key': API_KEY})
  
  # Parse the response
  response_json = json.loads(response.text)
  current_price = response_json['result']['price']
  
  return current_price

# Compute technical indicators
def compute_technical_indicators(df):
  # Compute the exponential moving average
  df['EMA_5'] = talib.EMA(df['ClosePrice'], timeperiod=5)
  
  # Compute the moving average convergence/divergence
  df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(df['ClosePrice'], fastperiod=12, slowperiod=26, signalperiod=9)
  
  # Compute the relative strength index
  df['RSI'] = talib.RSI(df['ClosePrice'], timeperiod=14)
  
  # Compute the stochastic oscillator
  df['SlowK'], df['SlowD'] = talib.STOCH(df['HighPrice'], df['LowPrice'], df['ClosePrice'], fastk_period=5, slowk_period=3, slowd_period=3)
  
  return df

# Make a decision to buy/sell
def make_decision(df):
  # Get the most recent values for the technical indicators
  current_rsi = df['RSI'].iloc[-1]
  current_macd = df['MACD'].iloc[-1]
  current_macd_hist = df['MACD_Hist'].iloc[-1]
  current_slowk = df['SlowK'].iloc[-1]
  current_slowd = df['SlowD'].iloc[-1]
  current_ema_5 = df['EMA_5'].iloc[-1]
  
  # Buy Logic
  if (current_rsi < 30) and (current_macd > 0) and (current_macd_hist > 0) and (current_slowk > current_slowd) and (current_ema_5 > df['ClosePrice'].iloc[-1]):
    return 'Buy'
  
  # Sell Logic
  elif (current_rsi > 70) and (current_macd < 0) and (current_macd_hist < 0) and (current_slowk < current_slowd) and (current_ema_5 < df['ClosePrice'].iloc[-1]):
    return 'Sell'
  
  # Do nothing
  else:
    return 'Do Nothing'

# Main function to run the trading bot
def run_trading_bot(exchange, pair, period):
  # Get the historical data
  df = get_historical_data(exchange, pair, period)
  
  # Compute the technical indicators
  df = compute_technical_indicators(df)
  
  # Make a decision
  decision = make_decision(df)
  
  # Get the current price
  current_price = get_current_price(exchange, pair)
  
  # Print the results
  print('Current Price: {}'.format(current_price))
  print('Decision: {}'.format(decision))

# Run the trading bot
run_trading_bot('kraken', 'ethusd', '14400')