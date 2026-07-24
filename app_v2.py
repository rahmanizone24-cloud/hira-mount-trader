import concurrent.futures
from datetime import datetime
import os
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hira Mount Trader Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- THEME STATE MANAGEMENT (PERSISTENT FIX) ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# --- THEME CSS DEFINITIONS ---
DARK_THEME_CSS = """
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; }
    .stSelectbox>div>div { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; }
    .stTextInput>div>div>input { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; }
    [data-testid="stHeader"] { background-color: rgba(13, 17, 23, 0.8); }
    [data-testid="stSidebar"] { background-color: #161b22; }
    .dataframe { background-color: #161b22; color: #c9d1d9; }
</style>
"""

LIGHT_THEME_CSS = """
<style>
    .stApp { background-color: #ffffff; color: #24292e; }
    .stButton>button { background-color: #f6f8fa; color: #24292e; border: 1px solid #d1d5da; }
    .stSelectbox>div>div { background-color: #ffffff; color: #24292e; border: 1px solid #d1d5da; }
    .stTextInput>div>div>input { background-color: #ffffff; color: #24292e; border: 1px solid #d1d5da; }
    .metric-card { background-color: #f6f8fa; border: 1px solid #e1e4e8; padding: 15px; border-radius: 8px; }
    [data-testid="stHeader"] { background-color: rgba(255, 255, 255, 0.8); }
    [data-testid="stSidebar"] { background-color: #f6f8fa; }
    .dataframe { background-color: #ffffff; color: #24292e; }
</style>
"""

# Apply Theme
if st.session_state.theme == "dark":
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)

# --- MARKET STATUS LOGIC (IST TIMEZONE) ---
now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
current_time = now_ist.time()
weekday = now_ist.weekday()  # 0=Monday, 6=Sunday

market_open_time = datetime.strptime("09:15", "%H:%M").time()
market_close_time = datetime.strptime("15:30", "%H:%M").time()

is_market_open = (
    weekday < 5
    and market_open_time <= current_time <= market_close_time
)

# --- TOP BAR & CONTROLS ---
col_title, col_status, col_theme = st.columns([3, 2, 1])

with col_title:
    st.title("🦅 HIRA MOUNT TRADER")

with col_status:
    if is_market_open:
        st.markdown(
            "### Status: <span style='color:#2ea44f;'>🟢 MARKET OPEN</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "### Status: <span style='color:#cb2431;'>🔴 MARKET CLOSED</span>",
            unsafe_allow_html=True,
        )

with col_theme:
    theme_btn_label = (
        "☀️ Light Mode"
        if st.session_state.theme == "dark"
        else "🌙 Dark Mode"
    )
    if st.button(theme_btn_label, key="theme_toggle_btn"):
        st.session_state.theme = (
            "light" if st.session_state.theme == "dark" else "dark"
        )
        st.rerun()

st.divider()

# --- DATA LOADING & PROCESSING ---
@st.cache_data(ttl=60)
def load_stock_list():
    # Check multiple possible paths for Hira Stocks.csv
    possible_paths = ["Hira Stocks.csv", "./Hira Stocks.csv", "../Hira Stocks.csv"]
    csv_file = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            break

    if csv_file:
        try:
            df = pd.read_csv(csv_file)
            # Find symbol column regardless of case
            col_match = [c for c in df.columns if c.strip().lower() in ["symbol", "ticker", "stock", "stocks"]]
            if col_match:
                symbols = df[col_match[0]].dropna().astype(str).str.strip().tolist()
                # Ensure .NS suffix for yfinance
                formatted_symbols = [s if s.endswith(".NS") or s.endswith(".BO") else f"{s}.NS" for s in symbols]
                return list(set(formatted_symbols))
        except Exception:
            pass

    return [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", 
        "ICICIBANK.NS", "TATAMOTORS.NS", "SBIN.NS", "BHARTIARTL.NS"
    ]


def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="5m")
        if df.empty or len(df) < 2:
            return None

        # EMA calculations
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

        # VWAP calculation
        df["VWAP"] = (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        return {
            "Symbol": symbol.replace(".NS", "").replace(".BO", ""),
            "LTP": round(last_row["Close"], 2),
            "Change %": round(
                ((last_row["Close"] - prev_row["Close"]) / prev_row["Close"]) * 100,
                2,
            ),
            "Volume": int(last_row["Volume"]),
            "EMA 20": round(last_row["EMA20"], 2),
            "EMA 200": round(last_row["EMA200"], 2),
            "VWAP": round(last_row["VWAP"], 2),
        }
    except Exception:
        return None


# --- MAIN INTERFACE ---
symbols = load_stock_list()

col_search, col_scan = st.columns([3, 1])
with col_search:
    search_query = st.text_input(
        "🔍 Search Stock Symbol", "", placeholder="Type stock name..."
    )

with col_scan:
    st.write("")
    st.write("")
    scan_btn = st.button("🔄 Refresh Data", use_container_width=True)

# Fetch data using multithreading for speed
results = []
with st.spinner("Fetching market data..."):
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_stock_data, sym) for sym in symbols]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

if results:
    df_results = pd.DataFrame(results)

    # Filter by search
    if search_query:
        df_results = df_results[
            df_results["Symbol"].str.contains(search_query.upper(), case=False)
        ]

    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No data available at the moment. Please try refreshing.")
