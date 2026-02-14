import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

st.title("🚀 Crypto Live Dashboard")

# =========================
# 🔎 SINGLE COIN SEARCH
# =========================
coin = st.text_input("Enter coin (example: BTCUSDT)", "")

col1, col2 = st.columns(2)

if col1.button("Live Price"):
    if coin:
        res = requests.get(f"{API}/live-price/{coin}")
        data = res.json()

        if "error" in data:
            st.error(data["error"])
        else:
            st.success(f"{data['symbol']} Price: {data['live_price']}")

if col2.button("Full Info"):
    if coin:
        res = requests.get(f"{API}/coin/{coin}")
        data = res.json()

        if "error" in data:
            st.error(data["error"])
        else:
            st.subheader(f"{data['symbol']} Details")

            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Price", data["live_price"])
            c2.metric("📈 24h Change %", data["24h_change_percent"])
            c3.metric("📊 Volume", data["24h_volume"])

            st.write("🔼 High:", data["24h_high"])
            st.write("🔽 Low:", data["24h_low"])

st.markdown("---")

# =========================
# 🔥 ALL USDT COINS LIVE
# =========================
st.subheader("💰 All USDT Coins Live Price")

if st.button("Show All USDT Coins"):

    with st.spinner("Loading live prices..."):

        res = requests.get(f"{API}/all-live-prices")
        data = res.json()

        prices = data["data"]

        df = pd.DataFrame(prices)
        df.columns = ["Symbol", "Price"]

        # 🔥 only USDT coins filter
        df = df[df["Symbol"].str.endswith("USDT")]

        st.success(f"Total USDT Coins: {len(df)}")

        # search
        search = st.text_input("🔎 Search coin")

        if search:
            df = df[df["Symbol"].str.contains(search.upper())]

        # sort
        sort = st.selectbox("Sort by price", ["None", "High to Low", "Low to High"])

        df["Price"] = df["Price"].astype(float)

        if sort == "High to Low":
            df = df.sort_values(by="Price", ascending=False)
        elif sort == "Low to High":
            df = df.sort_values(by="Price", ascending=True)

        st.dataframe(df, height=500, use_container_width=True)
