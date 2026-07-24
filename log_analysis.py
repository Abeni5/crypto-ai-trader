import os
import csv
from datetime import datetime
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_market_data():
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=50)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)
    latest = df.iloc[-1]

    fng = requests.get('https://api.alternative.me/fng/?limit=1').json()['data'][0]

    return latest['close'], latest['rsi'], latest['MACD_12_26_9'], int(fng['value']), fng['value_classification']

def analyze(rsi, macd, fng_value, fng_label):
    prompt = f"""BTC data: RSI={rsi:.1f}, MACD={macd:.1f}, Fear&Greed={fng_value} ({fng_label})

In 2-3 short sentences, plain language: what's the overall lean — bullish or bearish? Pick one, don't hedge. Then one sentence why."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content

def log_entry():
    price, rsi, macd, fng_value, fng_label = get_market_data()
    analysis = analyze(rsi, macd, fng_value, fng_label)
    lean = "bullish" if "bullish" in analysis.lower() else "bearish" if "bearish" in analysis.lower() else "unclear"

    row = [datetime.now().isoformat(), price, rsi, macd, fng_value, fng_label, lean, analysis.replace('\n', ' ')]

    file_exists = os.path.isfile('analysis_log.csv')
    with open('analysis_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'price', 'rsi', 'macd', 'fng_value', 'fng_label', 'ai_lean', 'full_analysis'])
        writer.writerow(row)

    print(f"Logged: {lean} at price {price}")

log_entry()