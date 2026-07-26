import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import os
import pytz

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hira Mount Trader Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- THEME STATE MANAGEMENT ---
query_params = st.query_params

if 'theme' not in st.session_state:
    st.session_state.theme = query_params.get('theme', 'dark')

st.query_params['theme'] = st.session_state.theme

if st.session_state.theme == 'dark':
    bg_color = "#0b0e14"
    card_bg = "#161b22"
    sub_card_bg = "#0d1117"
    border_color = "#30363d"
    text_main = "#f0f6fc"
    text_sub = "#8b949e"
    accent_blue = "#58a6ff"
    btn_bg = "#21262d"
else:
    bg_color = "#f6f8fa"
    card_bg = "#ffffff"
    sub_card_bg = "#f3f4f6"
    border_color = "#d0d7de"
    text_main = "#1f2328"
    text_sub = "#656d76"
    accent_blue = "#0969da"
    btn_bg = "#eaeef2"

st.markdown(f"""
    <style>
        header {{visibility: hidden !important; height: 0px !important;}}
        footer {{visibility: hidden !important; display: none !important;}}
        #MainMenu {{visibility: hidden !important;}}
        
        div[data-testid="stStatusWidget"], 
        div[data-testid="stDecoration"], 
        div[class*="viewerBadge"], 
        div[data-testid="stToolbar"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        .block-container {{
            padding-top: 0.3rem !important;
            padding-bottom: 0.1rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            max-width: 100% !important;
        }}
        
        body, .stApp {{
            background-color: {bg_color} !important;
            color: {text_main} !important;
            font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
        }}

        div[data-testid="stSpinner"], .stSpinner {{
            display: none !important;
        }}

        .stButton>button {{
            background-color: {btn_bg} !important;
            color: {accent_blue} !important;
            border: 1px solid {border_color} !important;
            border-radius: 6px !important;
            font-weight: 800 !important;
            font-size: 12px !important;
            padding: 4px 8px !important;
            height: 38px !important;
            width: 100% !important;
        }}

        .nav-title-clean {{
            font-size: 17px;
            font-weight: 900;
            color: {accent_blue} !important;
            letter-spacing: 0.8px;
            font-family: 'Trebuchet MS', sans-serif;
            text-transform: uppercase;
            line-height: 38px;
        }}

        .setup-header-bull {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-bottom: 10px; }}
        .setup-header-bear {{ font-size: 15px; font-weight: 900; color: #f85149; margin-bottom: 10px; }}

        .stock-row-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: {sub_card_bg};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 10px;
            margin-bottom: 6px;
            text-decoration: none !important;
        }}

        .sym-btn-box {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 5px;
            padding: 4px 10px;
            color: {accent_blue};
            font-weight: 800;
            font-size: 12px;
        }}

        .status-watch {{
            background-color: #C0C0C0;
            color: #000000;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
        }}

        .status-ready-bull {{
            background-color: #006400;
            color: #FFFFFF;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
        }}

        .status-ready-bear {{
            background-color: #8B0000;
            color: #FFFFFF;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
        }}

        .vol-box {{
            background-color: rgba(210, 153, 34, 0.15);
            color: #d29922;
            border: 1px solid rgba(210, 153, 34, 0.4);
            border-radius: 4px;
            padding: 1px 5px;
            font-weight: 900;
            font-size: 10px;
        }}

        .qty-box {{
            background-color: rgba(88, 166, 255, 0.15);
            color: {accent_blue};
            border: 1px solid rgba(88, 166, 255, 0.4);
            border-radius: 4px;
            padding: 1px 5px;
            font-weight: 900;
            font-size: 10px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- BAN ETFs ---
ETF_KEYWORDS = ["BEES", "ETF", "GOLD", "SILVER", "LIQUID", "IWIN", "SETF", "GILT"]

# --- DYNAMIC CSV LOADER ---
@st.cache_data(ttl=3600)
def load_hira_stocks():
    csv_candidates = ["Hira Stocks (2).csv", "Hira Stocks (1).csv", "Hira Stocks.csv"]
    for file_candidate in csv_candidates:
        if os.path.exists(file_candidate):
            try:
                df = pd.read_csv(file_candidate)
                col = 'symbol' if 'symbol' in df.columns else df.columns[0]
                syms = df[col].dropna().astype(str).str.strip().unique().tolist()
                filtered = [f"{s}.NS" if not s.endswith(".NS") else s for s in syms if not any(kw in s.upper() for kw in ETF_KEYWORDS)]
                if len(filtered) > 0:
                    return filtered
            except Exception:
                pass
    return ['NAUKRI.NS', 'RAMCOSYS.NS', 'MOTILALOFS.NS', 'POWERINDIA.NS', 'RELIANCE.NS', 'SBIN.NS']

ALL_HIRA_SYMBOLS = load_hira_stocks()

def calculate_vwap(df):
    """VWAP کی درست انٹرا ڈے گنتی"""
    v = df['Volume']
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * v).cumsum() / v.cumsum()

# --- DUAL TIMEFRAME SCANNER LOGIC ---
def analyze_hira_dual_timeframe_setup(df_1d, df_5m):
    if len(df_1d) < 3:
        return None, "NO_SIGNAL", "09:20", 1.0
    
    prev_day = df_1d.iloc[-2]       
    prev_prev_day = df_1d.iloc[-3]  

    # 1. DAILY CONSOLIDATION CHECK
    prev_day_range_pct = ((prev_day['High'] - prev_day['Low']) / prev_day['Close']) * 100
    is_daily_inside_bar = (prev_day['High'] <= prev_prev_day['High']) and (prev_day['Low'] >= prev_prev_day['Low'])
    is_daily_tight_range = prev_day_range_pct <= 2.0  

    if not (is_daily_inside_bar or is_daily_tight_range):
        return None, "NO_SIGNAL", "09:20", 1.0

    # 2. 5-MINUTE INTRADAY CHECK
    latest_date = df_5m.index[-1].date()
    today_df = df_5m[df_5m.index.date == latest_date].copy()

    if len(today_df) < 2:
        return None, "NO_SIGNAL", "09:20", 1.0

    today_df['VWAP'] = calculate_vwap(today_df)
    today_df['EMA20'] = today_df['Close'].ewm(span=20, adjust=False).mean()
    today_df['EMA200'] = today_df['Close'].ewm(span=200, adjust=False).mean() if len(today_df) >= 200 else today_df['Close'].ewm(span=50, adjust=False).mean()

    c1 = today_df.iloc[0]  
    c2 = today_df.iloc[1]  

    is_5m_inside_bar = (c2['High'] <= c1['High']) and (c2['Low'] >= c1['Low'])
    if not is_5m_inside_bar:
        return None, "NO_SIGNAL", "09:20", 1.0

    # 🟢 BULLISH SETUP LOGIC
    is_bullish_support = (c1['Close'] > c1['EMA20']) and (c1['Close'] > c1['EMA200']) and (c1['Close'] > c1['VWAP'])

    if is_bullish_support:
        sig_time = "09:20"
        vol_mult = 1.0
        status = "WATCH"

        if len(today_df) >= 3:
            for i in range(2, len(today_df)):
                c_curr = today_df.iloc[i]
                
                total_range = c_curr['High'] - c_curr['Low']
                body_size = abs(c_curr['Close'] - c_curr['Open'])
                upper_wick = c_curr['High'] - max(c_curr['Open'], c_curr['Close'])
                
                is_strong_green = (c_curr['Close'] > c_curr['Open']) and \
                                  (total_range > 0) and \
                                  (body_size / total_range >= 0.65) and \
                                  (upper_wick / total_range <= 0.15)
                
                base_vol = max(c1['Volume'], c2['Volume'])
                has_vol_spike = c_curr['Volume'] >= (base_vol * 1.25)
                is_breakout = (c_curr['High'] > max(c1['High'], c2['High'])) and (c_curr['Close'] > prev_day['High'])

                if is_breakout and is_strong_green and has_vol_spike:
                    status = "READY"
                    sig_time = c_curr.name.strftime("%H:%M")
                    vol_mult = round(c_curr['Volume'] / base_vol, 2) if base_vol > 0 else 1.25
                    break

        return "BULLISH", status, sig_time, vol_mult

    # 🔴 BEARISH SETUP LOGIC
    is_bearish_resistance = (c1['Close'] < c1['EMA20']) and (c1['Close'] < c1['EMA200']) and (c1['Close'] < c1['VWAP'])

    if is_bearish_resistance:
        sig_time = "09:20"
        vol_mult = 1.0
        status = "WATCH"

        if len(today_df) >= 3:
            for i in range(2, len(today_df)):
                c_curr = today_df.iloc[i]
                
                total_range = c_curr['High'] - c_curr['Low']
                body_size = abs(c_curr['Close'] - c_curr['Open'])
                lower_wick = min(c_curr['Open'], c_curr['Close']) - c_curr['Low']
                
                is_strong_red = (c_curr['Close'] < c_curr['Open']) and \
                                (total_range > 0) and \
                                (body_size / total_range >= 0.65) and \
                                (lower_wick / total_range <= 0.15)
                
                base_vol = max(c1['Volume'], c2['Volume'])
                has_vol_spike = c_curr['Volume'] >= (base_vol * 1.25)
                is_breakdown = (c_curr['Low'] < min(c1['Low'], c2['Low'])) and (c_curr['Close'] < prev_day['Low'])

                if is_breakdown and is_strong_red and has_vol_spike:
                    status = "READY"
                    sig_time = c_curr.name.strftime("%H:%M")
                    vol_mult = round(c_curr['Volume'] / base_vol, 2) if base_vol > 0 else 1.25
                    break

        return "BEARISH", status, sig_time, vol_mult

    return None, "NO_SIGNAL", "09:20", 1.0

# --- BATCH EXECUTION RUNNER ---
@st.cache_data(ttl=15)
def run_combined_scanner():
    bullish_list, bearish_list = [], []

    try:
        bulk_5m = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="5m", progress=False, group_by="ticker", threads=True)
        bulk_1d = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="1d", progress=False, group_by="ticker", threads=True)
    except:
        return [], []

    for symbol in ALL_HIRA_SYMBOLS:
        try:
            clean_sym = symbol.replace(".NS", "").upper()
            df_5m = bulk_5m[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_5m.dropna()
            df_1d = bulk_1d[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_1d.dropna()

            direction, status, sig_time, vol_mult = analyze_hira_dual_timeframe_setup(df_1d, df_5m)

            if direction is None or status == "NO_SIGNAL":
                continue

            curr_price = df_5m['Close'].iloc[-1]
            prev_close = df_1d['Close'].iloc[-2]
            day_pct = ((curr_price - prev_close) / prev_close) * 100
            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_sym}"
            qty = int(50000 / curr_price) if curr_price > 0 else 0

            item = {
                "Symbol": clean_sym, "Price": curr_price, "ChangePct": day_pct,
                "SignalTime": sig_time, "VolMultiple": vol_mult, "StatusState": status,
                "TVUrl": tv_url, "Qty": qty
            }

            if direction == "BULLISH":
                bullish_list.append(item)
            elif direction == "BEARISH":
                bearish_list.append(item)

        except:
            continue

    return bullish_list, bearish_list

# --- UI EXECUTION ---
ist_tz = pytz.timezone('Asia/Kolkata')
now_dt = datetime.datetime.now(ist_tz)
now_time = now_dt.strftime("%d %b %Y | %I:%M:%S %p")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([0.25, 0.45, 0.15, 0.15])
with nav_col1:
    st.markdown('<div class="nav-title-clean">HIRA MOUNT TRADER</div>', unsafe_allow_html=True)
with nav_col2:
    st.markdown(f'<div style="font-size: 11px; color: {text_sub}; margin-top:8px;">🕒 {now_time}</div>', unsafe_allow_html=True)
with nav_col3:
    if st.button("🌙 Theme" if st.session_state.theme == 'light' else "☀️ Theme"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
with nav_col4:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

bull_signals, bear_signals = run_combined_scanner()

# --- DISPLAY TABLES ---
col_bull, col_bear = st.columns(2)

with col_bull:
    st.markdown('<div class="setup-header-bull">🟢 BULLISH BREAKOUT SETUPS (Dual Timeframe)</div>', unsafe_allow_html=True)
    if bull_signals:
        for s in bull_signals:
            st_class = "status-ready-bull" if s['StatusState'] == 'READY' else "status-watch"
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <span class="sym-btn-box">{s['Symbol']}</span>
                    <span class="{st_class}">{s['StatusState']}</span>
                    <span style="font-size:11px;">🕒 {s['SignalTime']}</span>
                    <span class="vol-box">{s['VolMultiple']}x</span>
                    <span class="qty-box">Qty: {s['Qty']}</span>
                    <span style="font-weight:900; color:#3fb950;">₹{s['Price']:.2f} ({s['ChangePct']:+.2f}%)</span>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.info("No Bullish Dual-Timeframe Setups Found.")

with col_bear:
    st.markdown('<div class="setup-header-bear">🔴 BEARISH BREAKDOWN SETUPS (Dual Timeframe)</div>', unsafe_allow_html=True)
    if bear_signals:
        for s in bear_signals:
            st_class = "status-ready-bear" if s['StatusState'] == 'READY' else "status-watch"
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <span class="sym-btn-box" style="color:#f85149;">{s['Symbol']}</span>
                    <span class="{st_class}">{s['StatusState']}</span>
                    <span style="font-size:11px;">🕒 {s['SignalTime']}</span>
                    <span class="vol-box">{s['VolMultiple']}x</span>
                    <span class="qty-box">Qty: {s['Qty']}</span>
                    <span style="font-weight:900; color:#f85149;">₹{s['Price']:.2f} ({s['ChangePct']:+.2f}%)</span>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.info("No Bearish Dual-Timeframe Setups Found.")
