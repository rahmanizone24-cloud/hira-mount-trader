import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel
import datetime
import pytz

# ---------------------------------------------------------
# Page Configuration & Full Width Setup
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed")

# Smooth Auto-Refresh Logic (Every 30 Seconds)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="fyers_dashboard_refresh")
except ImportError:
    pass

# Theme State Management
if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Dark'

# Custom CSS for Full Screen Spread & Vibrant Premium Colors
st.markdown("""
<style>
    /* Maximize container width & remove side gaps */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.8rem !important;
    }
    
    .stApp { background-color: #06090e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Top Header Bar Single Line Layout */
    .top-bar-container {
        background-color: #0f172a;
        padding: 8px 16px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #1e293b;
        margin-bottom: 15px;
        gap: 8px;
    }
    
    .brand-title { font-size: 20px; font-weight: 900; color: #00e5ff; letter-spacing: 0.5px; white-space: nowrap; }
    
    .index-badge {
        background: #1e293b;
        color: #cbd5e1;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 12px;
        text-decoration: none;
        border: 1px solid #334155;
        font-weight: 700;
        white-space: nowrap;
    }
    .index-badge:hover { border-color: #00e5ff; color: #ffffff; }
    .neon-green { color: #10b981; font-weight: bold; }
    .neon-red { color: #f43f5e; font-weight: bold; }
    
    /* Smooth Subtle Pulse Status Animation */
    @keyframes smoothPulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .status-open { background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; animation: smoothPulse 2s infinite; }
    .status-closed { background: #881337; color: #fecdd3; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; animation: smoothPulse 2.5s infinite; }

    /* Top Summary Stat Box */
    .stat-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }
    .stat-title { font-size: 11px; color: #94a3b8; font-weight: bold; letter-spacing: 0.5px; }
    .stat-val-green { font-size: 20px; font-weight: 900; color: #10b981; }
    .stat-val-red { font-size: 20px; font-weight: 900; color: #f43f5e; }

    /* Market Movers Highlighted Cards */
    .mover-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .mover-symbol { font-size: 15px; font-weight: 900; color: #38bdf8; text-decoration: none; }
    .mover-symbol:hover { text-decoration: underline; color: #7dd3fc; }

    /* Table Column Header */
    .table-header-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: 800;
        color: #64748b;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    /* Boxed Grid Trading Setups */
    .setup-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .stock-title-link { font-size: 17px; font-weight: 800; color: #38bdf8; text-decoration: none; }
    .stock-title-link:hover { text-decoration: underline; color: #7dd3fc; }
    
    .number-badge {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        color: #f1f5f9;
        text-align: center;
    }
    
    .tag-ready-bull { background-color: #065f46; color: #34d399; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }
    .tag-ready-bear { background-color: #9f1239; color: #fecdd3; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🔐 Fyers Authentication")
access_token = st.sidebar.text_input("Enter Today's Access Token:", type="password")
client_id = st.sidebar.text_input("Client ID:", value="8L18MZNAIT-200")

# ---------------------------------------------------------
# Indian Real-Time Clock & Market Status
# ---------------------------------------------------------
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(ist)

market_open_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_ist.weekday() < 5
is_market_hours = market_open_time <= now_ist <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span class="status-open">🟢 OPEN</span>'
else:
    market_status_html = '<span class="status-closed">🔴 CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")

# Theme Switcher Button Event
def toggle_theme():
    if st.session_state['theme_mode'] == 'Dark':
        st.session_state['theme_mode'] = 'Light'
    else:
        st.session_state['theme_mode'] = 'Dark'

theme_icon = "☀️ Light" if st.session_state['theme_mode'] == 'Dark' else "🌙 Dark"

# ---------------------------------------------------------
# SINGLE LINE TOP HEADER (With Theme & Refresh Controls)
# ---------------------------------------------------------
col_top1, col_top_theme, col_top_ref = st.columns([10, 1, 1])

with col_top1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge">NIFTY 50: <b class="neon-green">24,199.60 (+0.85%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge">BANK NIFTY: <b class="neon-green">57,096.50 (+0.02%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge">SENSEX: <b class="neon-green">79,486.20 (+0.78%)</b></a>
        {market_status_html}
        <span class="index-badge" style="color:#38bdf8;">🕒 {time_str}</span>
    </div>
    """, unsafe_allow_html=True)

with col_top_theme:
    if st.button(theme_icon, use_container_width=True):
        toggle_theme()

with col_top_ref:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------
# Dataset
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
# Top Summary Cards (4 Columns)
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:ASHIKA" target="_blank" class="stock-title-link" style="font-size:20px;">ASHIKA</a>
            <span class="stat-val-green">+14.12%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#cbd5e1;">🕒 09:20</span>
            <span class="number-badge">101</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO" target="_blank" class="stock-title-link" style="font-size:20px; color:#f43f5e;">AURIONPRO</a>
            <span class="stat-val-red">-11.56%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#cbd5e1;">🕒 09:20</span>
            <span class="number-badge">67</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:20px; font-weight:900; color:#10b981; margin-top:4px;">BULLISH 🟢</div>
        <div style="margin-top:8px; font-size:12px; color:#cbd5e1;">Bullish: 112 | Bearish: 96</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:20px; font-weight:900; color:#00e5ff; margin-top:4px;">853 Stocks</div>
        <div style="margin-top:8px; font-size:12px; color:#10b981; font-weight:700;">Active Trading Setups: 208</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔥 CENTERED MARKET MOVERS SECTION
# ---------------------------------------------------------
st.markdown("<h3 style='color:#f8fafc; text-align:center; margin-top:10px; margin-bottom:15px; font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)
m_cols = st.columns(8)

for idx, item in df.head(8).iterrows():
    with m_cols[idx]:
        clr = "#10b981" if item['change'] > 0 else "#f43f5e"
        sgn = "+" if item['change'] > 0 else ""
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="mover-symbol">{item['symbol']}</a><br>
            <div style="font-size:14px; color:{clr}; font-weight:bold; margin-top:4px;">₹{item['price']}</div>
            <div style="font-size:12px; color:{clr}; font-weight:bold;">({sgn}{item['change']}%)</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:2px;">{item['qty']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Bullish & Bearish Setups with QTY Column Header
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#10b981; margin-bottom:10px; font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    
    # Table Header Row with QTY
    st.markdown("""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    bullish_list = df[df['type'] == 'BULLISH']
    for _, row in bullish_list.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bull">{row['status']}</span></div>
            <div style="width:18%; font-size:13px; color:#cbd5e1; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="number-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:16px; font-weight:bold; color:#f8fafc;">₹{row['price']}</div>
            <div style="width:14%; font-size:16px; font-weight:bold; color:#10b981;">+{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#f43f5e; margin-bottom:10px; font-weight:800;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    
    # Table Header Row with QTY
    st.markdown("""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    bearish_list = df[df['type'] == 'BEARISH']
    for _, row in bearish_list.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bear">{row['status']}</span></div>
            <div style="width:18%; font-size:13px; color:#cbd5e1; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="number-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:16px; font-weight:bold; color:#f8fafc;">₹{row['price']}</div>
            <div style="width:14%; font-size:16px; font-weight:bold; color:#f43f5e;">{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
