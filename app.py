import streamlit as st
import pandas as pd
import time
import json
import os
from tradingview_ta import TA_Handler, Interval

# File to store portfolio data
PORTFOLIO_FILE = "portfolio.json"


# Function to fetch live price from TradingView
def get_live_price(symbol):
    try:
        analysis = TA_Handler(
            symbol=symbol.upper(),
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_DAY
        ).get_analysis()
        return analysis.indicators["close"]
    except Exception:
        return None


# Function to load portfolio from file
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return []


# Function to save portfolio to file
def save_portfolio():
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(st.session_state.portfolio, f, indent=4, default=str)


# Initialize session state portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# Streamlit app layout
st.set_page_config(page_title="Crypto Portfolio Tracker", layout="wide")
st.title("📈 Crypto Portfolio Tracker")
st.write("Monitor your portfolio with real-time prices and track profits.")

# User input form
col1, col2, col3 = st.columns([3, 1, 3])
with col1:
    date = st.date_input("📅 Select Date")
with col2:
    coin_name = st.text_input("🔹 Enter Coin Name (e.g., BTC, ETH)").upper()
with col3:
    entry_price = st.number_input("💰 Entry Price ($)", min_value=0.0, format="%.2f")

col4, col5 = st.columns([3, 1])
with col4:
    quantity = st.number_input("📊 Quantity Bought", min_value=0.0, format="%.8f")
with col5:
    if st.button("➕ Add to Portfolio"):
        if coin_name and entry_price > 0 and quantity > 0:
            live_price = get_live_price(coin_name + "USDT")
            if live_price:
                st.session_state.portfolio.append({
                    "Date": str(date),
                    "Coin": coin_name,
                    "Entry Price ($)": entry_price,
                    "Qty": quantity,
                    "Current Price ($)": live_price,
                    "Current Change (%)": ((live_price - entry_price) / entry_price) * 100,
                    "Profit ($)": (live_price - entry_price) * quantity
                })
                save_portfolio()
                st.success(f"✅ {coin_name} added successfully!")
            else:
                st.error("⚠️ Unable to fetch live price for the coin.")
        else:
            st.warning("⚠️ Please enter valid values!")

# Display portfolio
st.markdown("### 🏦 Your Portfolio")
if st.session_state.portfolio:
    updated_portfolio = []
    for index, coin in enumerate(st.session_state.portfolio):
        updated_price = get_live_price(coin["Coin"] + "USDT")
        if updated_price:
            coin["Current Price ($)"] = updated_price
            coin["Profit ($)"] = (updated_price - coin["Entry Price ($)"]) * coin["Qty"]
            coin["Current Change (%)"] = ((updated_price - coin["Entry Price ($)"]) / coin["Entry Price ($)"]) * 100
        updated_portfolio.append(coin)
    
    save_portfolio()
    df = pd.DataFrame(updated_portfolio)
    st.dataframe(df)
    
    # Add delete functionality
    for index, coin in enumerate(updated_portfolio):
        if st.button(f"❌ Remove {coin['Coin']}", key=f"delete_{index}"):
            st.session_state.portfolio.pop(index)
            save_portfolio()
            st.rerun()

# Auto-refresh every 10 seconds
time.sleep(10)
st.rerun()
