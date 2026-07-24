import ccxt
import pandas as pd
import pandas_ta as ta
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=500)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.to_csv('btc_1h.csv', index=False)
print(df.tail())


df['rsi'] = ta.rsi(df['close'], length=14)
macd = ta.macd(df['close'])
df = pd.concat([df, macd], axis=1)

df.to_csv('btc_1h.csv', index=False)
print(df[['timestamp', 'close', 'rsi', 'MACD_12_26_9']].tail())