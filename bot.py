import requests
import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = 'wss://stream.binance.com:9443/ws/ethusdt@kline_1m'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.003

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
      print("Sending Order")
      order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
      print(order)

      return True
    except Exception as e:
      return False
    
    return True

def on_open(ws):
  print('opened connection')

def on_close(ws):
  print('closed connection')

def on_message(ws, message):
  global closes
  #print('Recived message')
  json_message = json.loads(message)
  #pprint.pprint(json_message)

  candle = json_message['k']
  is_candle_closed = candle['x']
  close = candle['c']

  if is_candle_closed:
    print("Candle closed at {}".format(close))
    closes.append(float(close))
    print("Closes")
    print(closes)

    if len(closes) > RSI_PERIOD:
      np_closes= numpy.array(closes)
      rsi = talib.RSI(np_closes, RSI_PERIOD)
      print("All RSI's calculated so far")
      print(rsi)
      last_rsi = rsi[-1]
      print("The current RSI is {}".format(last_rsi))

      if last_rsi > RSI_OVERBOUGHT:
        if in_position:
          print("Overbought, Sell! Sell! Sell!")
          # put binance sell logic here
          order_suceeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
          if order_suceeded:
            in_position = False
        else:
          print("We dont own any nothing to do")

      if last_rsi < RSI_OVERSOLD:
        if in_position:
          print("Sold but you already own it, nohing to do")
        else:
          print("Overbought, Buy! Buy! Buy!")
          # put binance order logic here
          order_suceeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
          if order_suceeded:
            in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()