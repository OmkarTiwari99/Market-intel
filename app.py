import streamlit as st
import pandas as pd
import requests
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Market Intelligence System", layout="wide")
st.title("📊 Market Intelligence & Reporting System")

def fetch_market_data(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    response = requests.get(url)
    data = response.json()["quoteResponse"]["result"][0]
    return {
        "symbol": symbol,
        "price": data["regularMarketPrice"],
        "change": data["regularMarketChangePercent"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

conn = sqlite3.connect("market.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS market (
    symbol TEXT,
    price REAL,
    change REAL,
    time TEXT
)
""")
conn.commit()

symbol = st.text_input("Enter stock symbol", "AAPL")

if st.button("Fetch Data"):
    row = fetch_market_data(symbol)
    cursor.execute(
        "INSERT INTO market VALUES (?,?,?,?)",
        (row["symbol"], row["price"], row["change"], row["time"])
    )
    conn.commit()
    st.success("Data fetched and saved!")

df = pd.read_sql("SELECT * FROM market ORDER BY time DESC", conn)
st.dataframe(df)

if not df.empty:
    st.line_chart(df.set_index("time")["price"])

conn.close()
