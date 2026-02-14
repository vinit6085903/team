from fastapi import FastAPI
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

api = os.getenv("BINANCE_API_KEY")
secret = os.getenv("BINANCE_SECRET_KEY")

client = Client(api, secret)

app = FastAPI(title=" Crypto Pro API")

# exchange symbols
exchange_info = client.get_exchange_info()
symbols = exchange_info['symbols']


@app.get("/")
def home():
    return {"message": "Crypto Search API Running "}


# all coins
@app.get("/all-coins")
def all_coins():
    coin_list = [s['symbol'] for s in symbols]
    return {
        "total_coins": len(coin_list),
        "coins": coin_list
    }


#  search coin
@app.get("/search/{coin_name}")
def search_coin(coin_name: str):
    coin_name = coin_name.upper()
    result = [s['symbol'] for s in symbols if coin_name in s['symbol']]

    if not result:
        return {"message": "Coin not found "}

    return {
        "total_found": len(result),
        "results": result
    }


#  FULL INFO of coin
@app.get("/coin/{symbol}")
def coin_full_info(symbol: str):
    symbol = symbol.upper()

    try:
        # live price
        price = client.get_symbol_ticker(symbol=symbol)

        # correct 24hr stats function
        stats = client.get_ticker(symbol=symbol)

        return {
            "symbol": symbol,
            "live_price": price["price"],
            "24h_change_percent": stats["priceChangePercent"],
            "24h_high": stats["highPrice"],
            "24h_low": stats["lowPrice"],
            "24h_volume": stats["volume"],
            "open_price": stats["openPrice"],
            "last_price": stats["lastPrice"]
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/live-price/{symbol}")
def live_price(symbol: str):
    symbol = symbol.upper()
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {
            "symbol": symbol,
            "live_price": ticker["price"]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/all-live-prices")
def all_live_prices():
    try:
        prices = client.get_all_tickers()
        return {
            "total": len(prices),
            "data": prices
        }
    except Exception as e:
        return {"error": str(e)}

import numpy as np


@app.get("/signal/{symbol}")
def trading_signal(symbol: str):
    symbol = symbol.upper()

    try:
        # last 50 candle data
        klines = client.get_klines(symbol=symbol, interval="1m", limit=50)

        closes = [float(k[4]) for k in klines]

        # moving averages
        short_ma = np.mean(closes[-5:])
        long_ma = np.mean(closes[-20:])

        # RSI calculation
        gains = []
        losses = []

        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))

        avg_gain = np.mean(gains) if gains else 0
        avg_loss = np.mean(losses) if losses else 1

        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))

        # decision logic
        if short_ma > long_ma and rsi < 70:
            signal = "BUY "
        elif short_ma < long_ma and rsi > 30:
            signal = "SELL "
        else:
            signal = "HOLD "

        return {
            "symbol": symbol,
            "signal": signal,
            "RSI": round(rsi, 2),
            "short_MA": round(short_ma, 4),
            "long_MA": round(long_ma, 4),
            "last_price": closes[-1]
        }

    except Exception as e:
        return {"error": str(e)}
