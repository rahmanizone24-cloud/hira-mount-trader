import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel
import datetime

# ---------------------------------------------------------
# Page Configuration & Full Dark Grid UI Setup
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="expanded")

# Inject Custom CSS for Exact Boxed Grid Layout & Clickable Elements
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    
    /* Top Bar Styling */
    .top-header {
        background-color: #121824;
        padding: 10px 16px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #1f293d;
        margin-bottom: 20px;
    }
    .brand-title { font-size: 18px; font-weight: 900; color: #3b82f6; letter-spacing: 0.5px; }
    
    /* Header Clickable Index Link */
    .index-link {
        background: #1e293b;
        color: #94a3b8;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        margin-right: 6px;
        text-decoration: none;
        border: 1px solid #334155;
    }
    .index-link:hover { border-color: #38bdf8; color: #f8fafc; }
    .badge-green { color: #22c55e; font-weight: bold; }
    
    .status-open { background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    .btn-header { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; font-size: 11px; }

    /* Summary Stat Box Cards */
    .stat-box {
        background: #121824;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }
    .stat-title { font-size: 10px; color: #64748b; font-weight: bold; letter-spacing: 0.5px; }
    .stat-val-green { font-size: 16px; font-weight: bold; color: #22c55e; }
    .stat-val-red { font-size: 16px; font-weight: bold; color: #ef4444; }
    .stat-sub { font-size: 10px; color: #64748b; margin-top: 4px; }

    /* Market Movers Cards */
    .mover-card {
        background: #121824;
        border: 1px solid #1f293d;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
    }
    .stock-link { text-decoration: none; color: #38bdf8; font-weight: bold; font-size: 13px; }
    .stock-link:hover { text-decoration: underline; color: #60a5fa; }

    /* Boxed Grid Trading Setup Card */
    .setup-box {
        background-color: #121824;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .setup-cell {
        background-color: #1a2234;
        border: 1px solid #28354d;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 11px;
        text-align: center;
    }
    
    .tag-ready { background-color: #064e3b; color: #34d399; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    .tag-bearish-ready { background-color: #7f1d1d; color: #fca5a5; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🔐 Fyers Authentication")
access_token = st.sidebar.text_input("Enter Today's Access Token:", type="password")
client_id = st.sidebar.text_input("Client ID:", value="8L18MZNAIT-200")
scan_button = st.sidebar.button("🚀 Start Scan")

# ---------------------------------------------------------
# Real-time Navigation Header
# ---------------------------------------------------------
realtime_clock = datetime.datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

st.markdown(f"""
<div class="top-header">
    <div>
        <span class="brand-title">HIRA MOUNT TRADER</span>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-link">NIFTY 50: <b class="badge-green">24,199.60 (+0.85%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-link">BANK NIFTY: <b class="badge-green">57,096.50 (+0.02%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-link">SENSEX: <b class="badge-green">79,486.20 (+0.78%)</b></a>
    </div>
    <div>
        <span class="status-open">🟢 OPEN</span>
        <span class="index-link" style="margin-left:8px; color:#38bdf8;">🕒 {realtime_clock}</span>
        <button class="btn-header">☀️ Light</button>
        <button class="btn-header">🔄 Refresh</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Dataset with Real-time Breakout Timestamps and Direct TradingView Links
stocks_data = [
    {"symbol": "ASHIKA", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ASHIKA", "status": "READY", "time": "09:20:15 AM", "qty": 101, "price": 690.30, "change": 14.12, "type": "BULLISH"},
    {"symbol": "KNEW", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:KNEW", "status": "READY", "time": "09:20:42 AM", "qty": 33, "price": 2724.80, "change": 12.23, "type": "BULLISH"},
    {"symbol": "ARIHANT", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ARIHANT", "status": "READY", "time": "09:21:05 AM", "qty": 41, "price": 1206.90, "change": 11.61, "type": "BULLISH"},
    {"symbol": "NEWGEN", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:NEWGEN", "status": "READY", "time": "09:22:10 AM", "qty": 85, "price": 583.60, "change": 11.07, "type": "BULLISH"},
    {"symbol": "GALLANTT", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:GALLANTT", "status": "READY", "time": "09:23:00 AM", "qty": 82, "price": 603.30, "change": 10.24, "type": "BULLISH"},
    
    {"symbol": "AURIONPRO", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO", "status": "READY", "time": "09:20:10 AM", "qty": 67, "price": 739.95, "change": -11.56, "type": "BEARISH"},
    {"symbol": "EVERESTIND", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:EVERESTIND", "status": "READY", "time": "09:20:55 AM", "qty": 141, "price": 492.55, "change": -8.90, "type": "BEARISH"},
    {"symbol": "CLEANMAX", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:CLEANMAX", "status": "READY", "time": "09:21:30 AM", "qty": 37, "price": 1316.00, "change": -8.55, "type": "BEARISH"},
    {"symbol": "SUNCLAY", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:SUNCLAY", "status": "READY", "time": "09:22:15 AM", "qty": 38, "price": 1289.30, "change": -7.89, "type": "BEARISH"},
    {"symbol": "RAMCOSYS", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:RAMCOSYS", "status": "READY", "time": "09:24:00 AM", "qty": 84, "price": 394.30, "change": -7.03, "type": "BEARISH"},
]

df = pd.DataFrame(stocks_data)

# ---------------------------------------------------------
# Top Gainer / Loser Clickable Summary KPI Cards
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:ASHIKA" target="_blank" class="stock-link" style="font-size:16px;">ASHIKA</a>
            <span class="stat-val-green">+14.12%</span>
        </div>
        <div class="stat-sub">🕒 Trigger: 09:20:15 AM | Qty: 101</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO" target="_blank" class="stock-link" style="font-size:16px; color:#ef4444;">AURIONPRO</a>
            <span class="stat-val-red">-11.56%</span>
        </div>
        <div class="stat-sub">🕒 Trigger: 09:20:10 AM | Qty: 67</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:15px; font-weight:bold; color:#22c55e; margin-top:2px;">BULLISH 🟢</div>
        <div class="stat-sub">Bullish: 112 | Bearish: 96</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:15px; font-weight:bold; color:#38bdf8; margin-top:2px;">853 Stocks</div>
        <div class="stat-sub" style="color:#22c55e;">Active Trading Setups: 208</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Market Movers Cards
# ---------------------------------------------------------
st.markdown("<h4 style='color:#f8fafc; margin-top:10px;'>🔥 MARKET MOVERS</h4>", unsafe_allow_html=True)
m_cols = st.columns(8)

for idx, item in df.head(8).iterrows():
    with m_cols[idx]:
        clr = "#22c55e" if item['change'] > 0 else "#ef4444"
        sgn = "+" if item['change'] > 0 else ""
        st.markdown(f"""
        <div class="mover-card">
            <a href="{item['tv_url']}" target="_blank" class="stock-link">{item['symbol']}</a><br>
            <span style="font-size:11px; color:{clr}; font-weight:bold;">₹{item['price']}</span><br>
            <span style="font-size:10px; color:{clr};">({sgn}{item['change']}%)</span><br>
            <span style="font-size:9px; color:#64748b;">🕒 {item['time']}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Bullish & Bearish Setups (Clean Boxed Grid Structure)
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#22c55e;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    bullish_list = df[df['type'] == 'BULLISH']
    
    for _, row in bullish_list.iterrows():
        st.markdown(f"""
        <div class="setup-box">
            <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready">{row['status']}</span></div>
            <div style="width:22%;" class="setup-cell"><span style="color:#38bdf8;">🕒 {row['time']}</span></div>
            <div style="width:15%;" class="setup-cell"><span style="color:#94a3b8;">Qty: {row['qty']}</span></div>
            <div style="width:13%; font-size:12px; color:#e2e8f0; font-weight:bold;">₹{row['price']}</div>
            <div style="width:10%; font-size:12px; color:#22c55e; font-weight:bold;">+{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#ef4444;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    bearish_list = df[df['type'] == 'BEARISH']
    
    for _, row in bearish_list.iterrows():
        st.markdown(f"""
        <div class="setup-box">
            <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-bearish-ready">{row['status']}</span></div>
            <div style="width:22%;" class="setup-cell"><span style="color:#38bdf8;">🕒 {row['time']}</span></div>
            <div style="width:15%;" class="setup-cell"><span style="color:#94a3b8;">Qty: {row['qty']}</span></div>
            <div style="width:13%; font-size:12px; color:#e2e8f0; font-weight:bold;">₹{row['price']}</div>
            <div style="width:10%; font-size:12px; color:#ef4444; font-weight:bold;">{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
