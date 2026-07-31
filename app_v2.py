import streamlit as st
import pandas as pd
import datetime
import pytz
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------
# 1. Page Configuration & Theme Initialization
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed")

# Auto-Refresh Logic (Every 30 Seconds)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_mount_refresh_key")
except ImportError:
    pass

if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Dark'

def toggle_theme():
    st.session_state['theme_mode'] = 'Light' if st.session_state['theme_mode'] == 'Dark' else 'Dark'

# Dynamic Themes Styling
if st.session_state['theme_mode'] == 'Dark':
    bg_app = "#06090e"
    bg_card = "#0f172a"
    border_clr = "#1e293b"
    txt_main = "#f8fafc"
    txt_muted = "#94a3b8"
    badge_bg = "#1e293b"
    btn_bg = "#1e293b"
    btn_txt = "#f8fafc"
else:
    bg_app = "#f1f5f9"
    bg_card = "#ffffff"
    border_clr = "#cbd5e1"
    txt_main = "#0f172a"
    txt_muted = "#64748b"
    badge_bg = "#e2e8f0"
    btn_bg = "#e2e8f0"
    btn_txt = "#0f172a"

st.markdown(f"""
<style>
    .main .block-container {{
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.8rem !important;
    }}
    
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    
    /* STREAMLIT BUTTON STYLING */
    div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: 1px solid {border_clr} !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }}
    div.stButton > button:hover {{
        border-color: #00e5ff !important;
        color: #00e5ff !important;
    }}

    /* Top Header Bar */
    .top-bar-container {{
        background-color: {bg_card};
        padding: 8px 16px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {border_clr};
        margin-bottom: 15px;
    }}
    
    .brand-title {{ font-size: 20px; font-weight: 900; color: #00e5ff; letter-spacing: 0.5px; white-space: nowrap; }}
    
    /* VIBRANT HIGH CONTRAST INDEX BADGES */
    .index-badge {{
        background: {badge_bg};
        color: #38bdf8;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        text-decoration: none;
        border: 1px solid {border_clr};
        font-weight: 800;
        white-space: nowrap;
    }}
    .index-badge:hover {{ border-color: #00e5ff; color: #ffffff; }}
    .neon-green-text {{ color: #00ff87 !important; font-weight: 900; }}
    
    /* Soft Dot Only Blink Animation */
    @keyframes dotGlow {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.3; transform: scale(0.9); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .dot-green {{ display: inline-block; width: 8px; height: 8px; background-color: #00ff87; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}
    .dot-red {{ display: inline-block; width: 8px; height: 8px; background-color: #f43f5e; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}

    /* KPI Stat Boxes */
    .stat-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }}
    .stat-title {{ font-size: 11px; color: {txt_muted}; font-weight: bold; letter-spacing: 0.5px; }}
    
    /* Market Movers Card Box */
    .mover-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }}
    
    .stock-title-link {{ font-size: 16px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: #7dd3fc; }}
    
    /* Table Headers & Setup Cards */
    .table-header-row {{
        display: flex;
        justify-content: space-between;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: 800;
        color: {txt_muted};
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }}

    .setup-card {{
        background-color: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .qty-badge {{
        background-color: {badge_bg};
        border: 1px solid {border_clr};
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        color: {txt_main};
        display: inline-block;
    }}
    
    .tag-ready-bull {{ background-color: #065f46; color: #34d399; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }}
    .tag-ready-bear {{ background-color: #9f1239; color: #fecdd3; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Time & Market Status
# ---------------------------------------------------------
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(ist)

market_open_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_ist.weekday() < 5
is_market_hours = market_open_time <= now_ist <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span style="background:#064e3b; color:#34d399; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-green"></span>OPEN</span>'
else:
    market_status_html = '<span style="background:#881337; color:#fecdd3; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-red"></span>CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")

# ---------------------------------------------------------
# 3. Top Header Bar Layout
# ---------------------------------------------------------
col_top1, col_top_theme, col_top_ref = st.columns([10, 1, 1])

with col_top1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge">NIFTY 50</a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge">BANK NIFTY</a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge">SENSEX</a>
        {market_status_html}
        <span class="index-badge" style="color:#00e5ff;">🕒 {time_str}</span>
    </div>
    """, unsafe_allow_html=True)

with col_top_theme:
    theme_label = "☀️ Light" if st.session_state['theme_mode'] == 'Dark' else "🌙 Dark"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

with col_top_ref:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------
# 4. Core Filtration Engine & Fyers Integration
# ---------------------------------------------------------
@st.cache_resource
def init_fyers():
    from fyers_apiv3 import fyersModel
    client_id = os.environ.get("FYERS_CLIENT_ID", "YOUR_CLIENT_ID")
    access_token = os.environ.get("FYERS_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
    return fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

fyers = None
try:
    fyers = init_fyers()
except Exception:
    pass

def calculate_ema(df, length):
    return df['close'].ewm(span=length, adjust=False).mean()

def check_5min_pause_candle_setup(symbol, fyers_obj):
    if fyers_obj is None:
        return None
    try:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        data = {
            "symbol": f"NSE:{symbol}-EQ",
            "resolution": "5",
            "date_format": "1",
            "range_from": today_str,
            "range_to": today_str,
            "cont_flag": "1"
        }
        
        time.sleep(0.03)
        res = fyers_obj.history(data=data)
        
        if res.get("s") != "ok" or not res.get("candles"):
            return None

        df = pd.DataFrame(res["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')

        if len(df) < 3:
            return None

        df['EMA_20'] = calculate_ema(df, 20)
        df['EMA_200'] = calculate_ema(df, 200)
        df['Vol_MA_20'] = df['volume'].rolling(window=20, min_periods=1).mean()

        # RULE 1: STRICT C1 CANDLE VALIDATION (09:15 AM)
        c1 = df.iloc[0]
        if c1['timestamp'].strftime("%H:%M") != "09:15":
            return None

        c1_range_pct = ((c1['high'] - c1['low']) / c1['open']) * 100
        if c1_range_pct > 1.5:
            return None

        c1_above_ema = (c1['close'] > c1['EMA_20']) and (c1['close'] > c1['EMA_200'])
        c1_below_ema = (c1['close'] < c1['EMA_20']) and (c1['close'] < c1['EMA_200'])

        if not (c1_above_ema or c1_below_ema):
            return None

        # RULE 2: STRICT C2 INSIDE CANDLE VALIDATION (09:20 AM)
        c2 = df.iloc[1]
        if c2['timestamp'].strftime("%H:%M") != "09:20":
            return None

        is_strict_inside = (c2['high'] <= c1['high']) and (c2['low'] >= c1['low'])
        if not is_strict_inside:
            return None

        # RULE 3: C3+ BREAKOUT VALIDATION
        for i in range(2, len(df)):
            curr = df.iloc[i]
            
            # BULLISH BREAKOUT
            if c1_above_ema and (curr['close'] > c1['high']) and (curr['volume'] > curr['Vol_MA_20']):
                chg = round(((curr['close'] - c1['open']) / c1['open']) * 100, 2)
                return {
                    "symbol": symbol,
                    "type": "BULLISH",
                    "time": curr['timestamp'].strftime("%H:%M"),
                    "price": curr['close'],
                    "change": chg,
                    "qty": curr['volume'],
                    "tv_url": f"https://in.tradingview.com/chart/?symbol=NSE:{symbol}"
                }
            
            # BEARISH BREAKOUT
            elif c1_below_ema and (curr['close'] < c1['low']) and (curr['volume'] > curr['Vol_MA_20']):
                chg = round(((curr['close'] - c1['open']) / c1['open']) * 100, 2)
                return {
                    "symbol": symbol,
                    "type": "BEARISH",
                    "time": curr['timestamp'].strftime("%H:%M"),
                    "price": curr['close'],
                    "change": chg,
                    "qty": curr['volume'],
                    "tv_url": f"https://in.tradingview.com/chart/?symbol=NSE:{symbol}"
                }

    except Exception:
        return None

    return None

@st.cache_data
def load_watchlist():
    csv_path = "hira_stocks.csv"
    if os.path.exists(csv_path):
        df_csv = pd.read_csv(csv_path)
        col = df_csv.columns[0]
        return df_csv[col].dropna().astype(str).tolist()
    return []

watchlist = load_watchlist()

def execute_scan(stocks):
    results = []
    if not stocks or fyers is None:
        return pd.DataFrame()

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(check_5min_pause_candle_setup, sym, fyers): sym for sym in stocks}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    return pd.DataFrame(results)

df_verified = execute_scan(watchlist)

if not df_verified.empty:
    bullish_df = df_verified[df_verified['type'] == 'BULLISH'].sort_values(by='change', ascending=False)
    bearish_df = df_verified[df_verified['type'] == 'BEARISH'].sort_values(by='change', ascending=True)
else:
    bullish_df = pd.DataFrame()
    bearish_df = pd.DataFrame()

# ---------------------------------------------------------
# 5. Top 4 KPI Summary Cards
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    if not bullish_df.empty:
        top_g = bullish_df.iloc[0]
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">TOP GAINER ⚡</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                <a href="{top_g['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px;">{top_g['symbol']}</a>
                <span style="font-size:18px; font-weight:900; color:#00ff87;">+{top_g['change']}%</span>
            </div>
            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; color:{txt_muted};">🕒 {top_g['time']}</span>
                <span class="qty-badge">{top_g['qty']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stat-box"><div class="stat-title">TOP GAINER ⚡</div><div style="font-size:14px; color:{txt_muted}; margin-top:8px;">No Setup Found</div></div>', unsafe_allow_html=True)

with c2:
    if not bearish_df.empty:
        top_l = bearish_df.iloc[0]
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">TOP LOSER 📉</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                <a href="{top_l['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px; color:#f43f5e;">{top_l['symbol']}</a>
                <span style="font-size:18px; font-weight:900; color:#f43f5e;">{top_l['change']}%</span>
            </div>
            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; color:{txt_muted};">🕒 {top_l['time']}</span>
                <span class="qty-badge">{top_l['qty']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stat-box"><div class="stat-title">TOP LOSER 📉</div><div style="font-size:14px; color:{txt_muted}; margin-top:8px;">No Setup Found</div></div>', unsafe_allow_html=True)

with c3:
    total_bull = len(bullish_df)
    total_bear = len(bearish_df)
    is_bull = total_bull >= total_bear
    s_txt = "BULLISH" if is_bull else "BEARISH"
    s_clr = "#00ff87" if is_bull else "#f43f5e"
    d_class = "dot-green" if is_bull else "dot-red"
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:18px; font-weight:900; color:{s_clr}; margin-top:4px;">
            <span class="{d_class}"></span>{s_txt}
        </div>
        <div style="margin-top:8px; font-size:12px; color:{txt_muted};">Bullish: {total_bull} | Bearish: {total_bear}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:18px; font-weight:900; color:#00e5ff; margin-top:4px;">{len(watchlist)} Stocks</div>
        <div style="margin-top:8px; font-size:12px; color:#00ff87; font-weight:700;">Active Setups: {total_bull + total_bear}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 🔥 MARKET MOVERS
# ---------------------------------------------------------
st.markdown("<h3 style='text-align:center; margin-top:10px; margin-bottom:15px; font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)

movers_4_bull = bullish_df.head(4)
movers_4_bear = bearish_df.head(4)

m_cols = st.columns(8)

for idx, (_, item) in enumerate(movers_4_bull.iterrows()):
    if idx < 4:
        with m_cols[idx]:
            st.markdown(f"""
            <div class="mover-box">
                <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="font-size:14px;">{item['symbol']}</a><br>
                <div style="font-size:13px; color:#00ff87; font-weight:bold; margin-top:2px;">₹{item['price']}</div>
                <div style="font-size:11px; color:#00ff87; font-weight:bold;">(+{item['change']}%)</div>
                <div style="margin-top:4px; display:flex; justify-content:center; gap:4px; align-items:center;">
                    <span class="qty-badge">{item['qty']}</span>
                    <span style="font-size:10px; color:{txt_muted};">🕒 {item['time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

for idx, (_, item) in enumerate(movers_4_bear.iterrows()):
    if idx < 4:
        with m_cols[idx + 4]:
            st.markdown(f"""
            <div class="mover-box">
                <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="font-size:14px; color:#f43f5e;">{item['symbol']}</a><br>
                <div style="font-size:13px; color:#f43f5e; font-weight:bold; margin-top:2px;">₹{item['price']}</div>
                <div style="font-size:11px; color:#f43f5e; font-weight:bold;">({item['change']}%)</div>
                <div style="margin-top:4px; display:flex; justify-content:center; gap:4px; align-items:center;">
                    <span class="qty-badge">{item['qty']}</span>
                    <span style="font-size:10px; color:{txt_muted};">🕒 {item['time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. Setup Tables
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#00ff87; margin-bottom:10px; font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    for _, row in bullish_df.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bull">READY</span></div>
            <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:#00ff87;">+{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#f43f5e; margin-bottom:10px; font-weight:800;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    for _, row in bearish_df.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bear">READY</span></div>
            <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:#f43f5e;">{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
