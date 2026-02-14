from fastapi import FastAPI
from binance.client import Client
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

api = os.getenv("BINANCE_API_KEY")
secret = os.getenv("BINANCE_SECRET_KEY")

app = FastAPI(title=" Crypto Pro API")

# 🟢 safe client function (important)
def get_client():
    try:
        return Client(api, secret)
    except:
        return None


# ================= HOME =================
@app.get("/")
def home():
    return {"message": "Crypto API Running "}


# ================= ALL COINS =================
@app.get("/all-coins")
def all_coins():
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    try:
        exchange_info = client.get_exchange_info()
        symbols = exchange_info['symbols']
        coin_list = [s['symbol'] for s in symbols]

        return {
            "total_coins": len(coin_list),
            "coins": coin_list[:500]   # limit for speed
        }
    except Exception as e:
        return {"error": str(e)}


# ================= SEARCH =================
@app.get("/search/{coin}")
def search_coin(coin: str):
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    try:
        exchange_info = client.get_exchange_info()
        symbols = exchange_info['symbols']

        result = [s['symbol'] for s in symbols if coin.upper() in s['symbol']]

        return {"results": result[:50]}
    except Exception as e:
        return {"error": str(e)}


# ================= FULL INFO =================
@app.get("/coin/{symbol}")
def coin_full(symbol: str):
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    symbol = symbol.upper()

    try:
        price = client.get_symbol_ticker(symbol=symbol)
        stats = client.get_ticker(symbol=symbol)

        return {
            "symbol": symbol,
            "price": price["price"],
            "change_24h": stats["priceChangePercent"],
            "high_24h": stats["highPrice"],
            "low_24h": stats["lowPrice"],
            "volume": stats["volume"]
        }
    except Exception as e:
        return {"error": str(e)}


# ================= LIVE PRICE =================
@app.get("/live/{symbol}")
def live_price(symbol: str):
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    try:
        ticker = client.get_symbol_ticker(symbol=symbol.upper())
        return ticker
    except Exception as e:
        return {"error": str(e)}


# ================= ALL LIVE =================
@app.get("/all-live")
def all_live():
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    try:
        prices = client.get_all_tickers()
        return {"data": prices[:300]}
    except Exception as e:
        return {"error": str(e)}


# ================= AI SIGNAL =================
@app.get("/signal/{symbol}")
def signal(symbol: str):
    client = get_client()
    if not client:
        return {"error": "Binance blocked on server"}

    symbol = symbol.upper()

    try:
        klines = client.get_klines(symbol=symbol, interval="1m", limit=50)
        closes = [float(k[4]) for k in klines]

        short_ma = np.mean(closes[-5:])
        long_ma = np.mean(closes[-20:])

        gains, losses = [], []

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

        if short_ma > long_ma and rsi < 70:
            s = "BUY "
        elif short_ma < long_ma and rsi > 30:
            s = "SELL "
        else:
            s = "HOLD "

        return {
            "symbol": symbol,
            "signal": s,
            "RSI": round(rsi,2),
            "price": closes[-1]
        }

    except Exception as e:
        return {"error": str(e)}
