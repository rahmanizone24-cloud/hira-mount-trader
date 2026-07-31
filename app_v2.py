import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel
import datetime
import time

# ---------------------------------------------------------
# Page Configuration & Theme Logic
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="expanded")

# Auto-Refresh Logic (Every 30 Seconds = 30000 ms)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="datarefresh")
except ImportError:
    pass

# Theme Switcher Logic via Sidebar
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Dark'

theme_choice = st.sidebar.radio("🎨 Theme Mode:", ["Dark", "Light"], index=0 if st.session_state['theme'] == 'Dark' else 1)
st.session_state['theme'] = theme_choice

# Define CSS based on Theme
if st.session_state['theme'] == 'Dark':
    bg_color = "#0b0e14"
    card_bg = "#121824"
    border_color = "#1f293d"
    text_primary = "#f8fafc"
    text_secondary = "#94a3b8"
    cell_bg = "#1a2234"
else:
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    border_color = "#cbd5e1"
    text_primary = "#0f172a"
    text_secondary = "#475569"
    cell_bg = "#f1f5f9"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_primary}; font-family: 'Inter', sans-serif; }}
    
    /* Top Bar Styling */
    .top-header {{
        background-color: {card_bg};
        padding: 10px 20px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {border_color};
        margin-bottom: 20px;
    }}
    .brand-title {{ font-size: 20px; font-weight: 900; color: #3b82f6; letter-spacing: 0.5px; }}
    
    .indices-container {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0 auto;
    }}
    
    .index-link {{
        background: {cell_bg};
        color: {text_secondary};
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        text-decoration: none;
        border: 1px solid {border_color};
        font-weight: 600;
    }}
    .index-link:hover {{ border-color: #38bdf8; color: {text_primary}; }}
    .badge-green {{ color: #22c55e; font-weight: bold; }}
    
    .status-open {{ background: #064e3b; color: #34d399; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
    .status-closed {{ background: #7f1d1d; color: #fca5a5; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}

    /* KPI Cards */
    .stat-box {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 15px;
    }}
    .stat-title {{ font-size: 11px; color: {text_secondary}; font-weight: bold; letter-spacing: 0.5px; }}
    .stat-val-green {{ font-size: 18px; font-weight: bold; color: #22c55e; }}
    .stat-val-red {{ font-size: 18px; font-weight: bold; color: #ef4444; }}

    /* Stock Setup Card Boxed UI */
    .setup-box {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .stock-title {{ font-size: 15px; font-weight: bold; color: #38bdf8; text-decoration: none; }}
    .stock-title:hover {{ text-decoration: underline; color: #60a5fa; }}
    
    .qty-box {{
        background-color: {cell_bg};
        border: 1px solid {border_color};
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        color: #e2e8f0;
    }}
    
    .time-tag {{ font-size: 12px; color: {text_secondary}; font-weight: 600; }}
    .tag-ready {{ background-color: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
    .tag-bearish-ready {{ background-color: #7f1d1d; color: #fca5a5; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🔐 Fyers Authentication")
access_token = st.sidebar.text_input("Enter Today's Access Token:", type="password")
client_id = st.sidebar.text_input("Client ID:", value="8L18MZNAIT-200")

# Manual Refresh Button in Sidebar & Header
if st.sidebar.button("🔄 Manual Refresh"):
    st.rerun()

# ---------------------------------------------------------
# Real-time Market Status Calculation
# ---------------------------------------------------------
now = datetime.datetime.now()
market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now.weekday() < 5
is_market_hours = market_open_time <= now <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span class="status-open">🟢 OPEN</span>'
else:
    market_status_html = '<span class="status-closed">🔴 CLOSED</span>'

# Clean Time Format (Hour:Minute)
now_str = now.strftime("%d %b | %H:%M")

# ---------------------------------------------------------
# Centered Top Header Navigation
# ---------------------------------------------------------
st.markdown(f"""
<div class="top-header">
    <div style="flex:1;">
        <span class="brand-title">HIRA MOUNT TRADER</span>
    </div>
    <div class="indices-container">
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-link">NIFTY 50: <b class="badge-green">24,199.60 (+0.85%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-link">BANK NIFTY: <b class="badge-green">57,096.50 (+0.02%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-link">SENSEX: <b class="badge-green">79,486.20 (+0.78%)</b></a>
    </div>
    <div style="flex:1; text-align:right; display:flex; align-items:center; justify-content:flex-end; gap:8px;">
        {market_status_html}
        <span class="index-link" style="color:#38bdf8;">🕒 {now_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Bar Manual Refresh Button Layout
col_ref1, col_ref2 = st.columns([11, 1])
with col_ref2:
    if st.button("🔄 Refresh"):
        st.rerun()

# ---------------------------------------------------------
# Dataset with Cleaned Short Timestamp Format (HH:MM)
# ---------------------------------------------------------
stocks_data = [
    {"symbol": "ASHIKA", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ASHIKA", "status": "READY", "time": "09:20", "qty": 101, "price": 690.30, "change": 14.12, "type": "BULLISH"},
    {"symbol": "KNEW", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:KNEW", "status": "READY", "time": "09:20", "qty": 33, "price": 2724.80, "change": 12.23, "type": "BULLISH"},
    {"symbol": "ARIHANT", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ARIHANT", "status": "READY", "time": "09:21", "qty": 41, "price": 1206.90, "change": 11.61, "type": "BULLISH"},
    {"symbol": "NEWGEN", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:NEWGEN", "status": "READY", "time": "09:22", "qty": 85, "price": 583.60, "change": 11.07, "type": "BULLISH"},
    {"symbol": "GALLANTT", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:GALLANTT", "status": "READY", "time": "09:23", "qty": 82, "price": 603.30, "change": 10.24, "type": "BULLISH"},
    
    {"symbol": "AURIONPRO", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO", "status": "READY", "time": "09:20", "qty": 67, "price": 739.95, "change": -11.56, "type": "BEARISH"},
    {"symbol": "EVERESTIND", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:EVERESTIND", "status": "READY", "time": "09:20", "qty": 141, "price": 492.55, "change": -8.90, "type": "BEARISH"},
    {"symbol": "CLEANMAX", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:CLEANMAX", "status": "READY", "time": "09:21", "qty": 37, "price": 1316.00, "change": -8.55, "type": "BEARISH"},
    {"symbol": "SUNCLAY", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:SUNCLAY", "status": "READY", "time": "09:22", "qty": 38, "price": 1289.30, "change": -7.89, "type": "BEARISH"},
    {"symbol": "RAMCOSYS", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:RAMCOSYS", "status": "READY", "time": "09:24", "qty": 84, "price": 394.30, "change": -7.03, "type": "BEARISH"},
]

df = pd.DataFrame(stocks_data)

# ---------------------------------------------------------
# Top Gainer / Loser KPI Cards
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:ASHIKA" target="_blank" class="stock-title" style="font-size:18px;">ASHIKA</a>
            <span class="stat-val-green">+14.12%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span class="time-tag">🕒 09:20</span>
            <span class="qty-box">Vol: 101</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO" target="_blank" class="stock-title" style="font-size:18px; color:#ef4444;">AURIONPRO</a>
            <span class="stat-val-red">-11.56%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span class="time-tag">🕒 09:20</span>
            <span class="qty-box">Vol: 67</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:18px; font-weight:bold; color:#22c55e; margin-top:4px;">BULLISH 🟢</div>
        <div style="margin-top:8px;" class="time-tag">Bullish: 112 | Bearish: 96</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:18px; font-weight:bold; color:#38bdf8; margin-top:4px;">853 Stocks</div>
        <div style="margin-top:8px; color:#22c55e;" class="time-tag">Active Setups: 208</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Bullish & Bearish Setups
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#22c55e; margin-bottom:12px;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    bullish_list = df[df['type'] == 'BULLISH']
    
    for _, row in bullish_list.iterrows():
        st.markdown(f"""
        <div class="setup-box">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready">{row['status']}</span></div>
            <div style="width:20%;" class="time-tag">🕒 {row['time']}</div>
            <div style="width:17%;"><span class="qty-box">Vol: {row['qty']}</span></div>
            <div style="width:13%; font-size:14px; font-weight:bold; color:{text_primary};">₹{row['price']}</div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:#22c55e;">+{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#ef4444; margin-bottom:12px;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    bearish_list = df[df['type'] == 'BEARISH']
    
    for _, row in bearish_list.iterrows():
        st.markdown(f"""
        <div class="setup-box">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-bearish-ready">{row['status']}</span></div>
            <div style="width:20%;" class="time-tag">🕒 {row['time']}</div>
            <div style="width:17%;"><span class="qty-box">Vol: {row['qty']}</span></div>
            <div style="width:13%; font-size:14px; font-weight:bold; color:{text_primary};">₹{row['price']}</div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:#ef4444;">{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
