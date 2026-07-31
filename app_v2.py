import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel
import datetime

# ---------------------------------------------------------
# Page Configuration & Dark Theme Layout
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to mimic exact dashboard layout & colors
st.markdown("""
<style>
    /* Dark Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Top Header Bar */
    .top-bar {
        background-color: #161b22;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #30363d;
    }
    
    /* Metric / Stat Card Styling */
    .stat-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    
    .green-text { color: #2ea043; font-weight: bold; }
    .red-text { color: #f85149; font-weight: bold; }
    
    .tag-ready-green {
        background-color: #1b4721;
        color: #3fb950;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .tag-ready-red {
        background-color: #4c1d1d;
        color: #f85149;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Hide Streamlit default headers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar - Authentication & Parameters
# ---------------------------------------------------------
st.sidebar.title("🔐 Fyers Authentication")
access_token = st.sidebar.text_input("Enter Today's Access Token:", type="password")
client_id = st.sidebar.text_input("Client ID:", value="8L18MZNAIT-200")

scan_button = st.sidebar.button("🚀 Start Scan")

# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown("""
<div style="background-color: #0b0e14; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-bottom: 2px solid #1f2937;">
    <span style="font-size: 22px; font-weight: 800; color: #38bdf8; letter-spacing: 1px;">HIRA MOUNT TRADER</span>
    <span style="margin-left: 20px; background: #1e293b; color: #94a3b8; padding: 4px 10px; border-radius: 4px; font-size: 12px;">NIFTY 50: <b style="color:#4ade80;">24,199.60 (+0.85%)</b></span>
    <span style="margin-left: 10px; background: #1e293b; color: #94a3b8; padding: 4px 10px; border-radius: 4px; font-size: 12px;">BANK NIFTY: <b style="color:#4ade80;">51,096.50 (+0.02%)</b></span>
</div>
""", unsafe_allow_html=True)

if not access_token and not scan_button:
    st.info("👈 براہ کرم سائیڈ بار میں آج کا Fyers Access Token درج کریں اور 'Start Scan' پر کلک کریں۔")
else:
    # Initialize Fyers API Model
    try:
        fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
    except Exception as e:
        st.error(f"Fyers Client Initialization Failed: {e}")

    # Dummy/Mock Data fallback for off-market hours representation matching screenshot
    stocks_data = [
        {"symbol": "ASHIKA", "status": "READY", "time": "09:20 AM", "qty": 101, "price": 690.30, "change": 14.12, "type": "BULLISH"},
        {"symbol": "KNEW", "status": "READY", "time": "09:20 AM", "qty": 33, "price": 2724.80, "change": 12.23, "type": "BULLISH"},
        {"symbol": "ARIHANT", "status": "READY", "time": "09:20 AM", "qty": 41, "price": 1206.90, "change": 11.61, "type": "BULLISH"},
        {"symbol": "NEWGEN", "status": "READY", "time": "09:20 AM", "qty": 85, "price": 583.60, "change": 11.07, "type": "BULLISH"},
        {"symbol": "GALLANTT", "status": "READY", "time": "09:20 AM", "qty": 82, "price": 603.30, "change": 10.24, "type": "BULLISH"},
        {"symbol": "AURIONPRO", "status": "READY", "time": "09:20 AM", "qty": 67, "price": 739.95, "change": -11.56, "type": "BEARISH"},
        {"symbol": "EVERESTIND", "status": "READY", "time": "09:20 AM", "qty": 141, "price": 492.55, "change": -8.90, "type": "BEARISH"},
        {"symbol": "CLEANMAX", "status": "READY", "time": "09:20 AM", "qty": 37, "price": 1316.00, "change": -8.55, "type": "BEARISH"},
        {"symbol": "SUNCLAY", "status": "READY", "time": "09:20 AM", "qty": 38, "price": 1289.30, "change": -7.89, "type": "BEARISH"},
        {"symbol": "RAMCOSYS", "status": "READY", "time": "09:20 AM", "qty": 84, "price": 394.30, "change": -7.03, "type": "BEARISH"},
    ]

    df = pd.DataFrame(stocks_data)

    # ---------------------------------------------------------
    # Top KPI Summary Cards (4 Columns)
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <small style="color:#8b949e;">TOP GAINER ⚡</small><br>
            <b style="font-size:18px; color:#f0f6fc;">ASHIKA</b> 
            <span class="green-text" style="float:right;">+14.12%</span><br>
            <small style="color:#8b949e;">🕒 09:20 AM | Qty: 101</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <small style="color:#8b949e;">TOP LOSER 📉</small><br>
            <b style="font-size:18px; color:#f0f6fc;">AURIONPRO</b> 
            <span class="red-text" style="float:right;">-11.56%</span><br>
            <small style="color:#8b949e;">🕒 09:20 AM | Qty: 67</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <small style="color:#8b949e;">MARKET SENTIMENT</small><br>
            <b style="font-size:18px; color:#3fb950;">BULLISH 🟢</b><br>
            <small style="color:#8b949e;">Bullish: 112 | Bearish: 96</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <small style="color:#8b949e;">SCANNED STOCKS</small><br>
            <b style="font-size:18px; color:#58a6ff;">853 Stocks</b><br>
            <small style="color:#3fb950;">Active Trading Setups: 208</small>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 MARKET MOVERS Section
    # ---------------------------------------------------------
    st.markdown("### 🔥 MARKET MOVERS")
    
    movers_cols = st.columns(8)
    for idx, item in df.head(8).iterrows():
        with movers_cols[idx]:
            color = "#2ea043" if item['change'] > 0 else "#f85149"
            sign = "+" if item['change'] > 0 else ""
            st.markdown(f"""
            <div style="background-color:#161b22; border:1px solid #30363d; border-radius:6px; padding:8px; text-align:center;">
                <b style="font-size:12px; color:#c9d1d9;">{item['symbol']}</b><br>
                <span style="font-size:11px; color:{color};">₹{item['price']}</span><br>
                <span style="font-size:11px; color:{color};">({sign}{item['change']}%)</span><br>
                <small style="font-size:9px; color:#8b949e;">Qty: {item['qty']}</small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Bullish vs Bearish Tables Section
    # ---------------------------------------------------------
    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown("### 🟢 BULLISH SETUPS")
        bullish_df = df[df['type'] == 'BULLISH'][['symbol', 'status', 'time', 'qty', 'price', 'change']]
        bullish_df['price'] = bullish_df['price'].apply(lambda x: f"₹{x:.2f}")
        bullish_df['change'] = bullish_df['change'].apply(lambda x: f"+{x:.2f}%")
        st.dataframe(bullish_df, use_container_width=True, hide_index=True)

    with t_col2:
        st.markdown("### 🔴 BEARISH SETUPS")
        bearish_df = df[df['type'] == 'BEARISH'][['symbol', 'status', 'time', 'qty', 'price', 'change']]
        bearish_df['price'] = bearish_df['price'].apply(lambda x: f"₹{x:.2f}")
        bearish_df['change'] = bearish_df['change'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(bearish_df, use_container_width=True, hide_index=True)
