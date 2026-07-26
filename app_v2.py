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

        .header-indices-wrapper {{
            display: flex;
            align-items: center;
            gap: 8px;
            width: 100%;
            height: 38px;
        }}
        
        .idx-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background-color: {sub_card_bg};
            border: 1.5px solid {border_color};
            border-radius: 7px;
            padding: 4px 10px;
            font-size: 12px;
            text-decoration: none !important;
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 11px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 11px; }}

        .live-blink {{
            animation: pulseBlink 6.0s ease-in-out infinite;
            display: inline-block;
        }}
        @keyframes pulseBlink {{
            0% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.40; transform: scale(0.98); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        .market-status-open {{
            background-color: rgba(63, 185, 80, 0.15);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.4);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
        }}
        
        .market-status-closed {{
            background-color: rgba(248, 81, 73, 0.15);
            color: #f85149;
            border: 1px solid rgba(248, 81, 73, 0.4);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
        }}

        .metric-container {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px 12px;
        }}
        .card-label {{ font-size: 10px; color: {text_sub}; font-weight: 800; }}
        .card-value-green {{ font-size: 15px; font-weight: 900; color: #3fb950; }}
        .card-value-red {{ font-size: 15px; font-weight: 900; color: #f85149; }}

        .box-container {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 10px;
            margin-bottom: 8px;
        }}
        .box-title {{ font-size: 13px; font-weight: 800; color: {text_main}; }}

        .setup-box {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 12px;
        }}
        .setup-header-bull {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-bottom: 10px; }}
        .setup-header-bear {{ font-size: 15px; font-weight: 900; color: #f85149; margin-bottom: 10px; }}

        .row-header {{
            display: flex;
            justify-content: space-between;
            padding: 6px 10px;
            font-size: 10px;
            font-weight: 800;
            color: {text_sub};
            border-bottom: 1px solid {border_color};
            margin-bottom: 6px;
        }}

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
TOTAL_SCANNED_STOCKS = len(ALL_HIRA_SYMBOLS)

# --- FETCH INDICES ---
@st.cache_data(ttl=15)
def fetch_indices():
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
    res = {}
    try:
        data = yf.download(list(indices.values()), period="5d", interval="1d", progress=False, group_by="ticker")
        for name, sym in indices.items():
            try:
                df = data[sym].dropna()
                curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                pct = ((curr - prev) / prev) * 100
                res[name] = {"val": round(curr, 2), "pct": round(pct, 2)}
            except:
                res[name] = {"val": 0.0, "pct": 0.0}
    except:
        pass
    return res

def calc_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

# --- COMBINED SCANNER ENGINE (BULLISH + BEARISH SETUP LOGIC) ---
@st.cache_data(ttl=15)
def run_combined_scanner():
    bullish_list, bearish_list, all_stocks = [], [], []

    try:
        bulk_5m = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="5m", progress=False, group_by="ticker", threads=True)
        bulk_1d = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="1d", progress=False, group_by="ticker", threads=True)
    except:
        return [], [], None, None, 0, 0

    for symbol in ALL_HIRA_SYMBOLS:
        try:
            clean_sym = symbol.replace(".NS", "").upper()
            df_5m = bulk_5m[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_5m.dropna()
            df_1d = bulk_1d[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_1d.dropna()

            if len(df_5m) < 20 or len(df_1d) < 2:
                continue

            df_5m['EMA20'] = calc_ema(df_5m['Close'], 20)
            df_5m['EMA200'] = calc_ema(df_5m['Close'], 200) if len(df_5m) >= 200 else calc_ema(df_5m['Close'], 50)

            latest_date = df_5m.index[-1].date()
            today_df = df_5m[df_5m.index.date == latest_date].copy()

            if len(today_df) < 2:
                continue

            c1 = today_df.iloc[0]
            c2 = today_df.iloc[1]

            # Candle 1 Range Filter <= 1.5%
            c1_range_pct = ((c1['High'] - c1['Low']) / c1['Close']) * 100
            if c1_range_pct > 1.5:
                continue

            latest = today_df.iloc[-1]
            curr_price = latest['Close']
            prev_close = df_1d['Close'].iloc[-2]
            day_pct = ((curr_price - prev_close) / prev_close) * 100

            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_sym}"
            qty = int(50000 / curr_price) if curr_price > 0 else 0

            # --- 🟢 BULLISH SETUP CONDITIONS ---
            c1_bull_ema = (c1['Close'] > c1['EMA20']) and (c1['Close'] > c1['EMA200'])
            c1_bull_prox = (abs(c1['Close'] - c1['EMA20']) / c1['Close'] * 100 <= 0.5)

            c2_inside_bull = (c2['High'] <= c1['High']) and (c2['Low'] >= c1['Low'])

            if c1_bull_ema and c1_bull_prox and c2_inside_bull:
                status = "WATCH"
                sig_time = "09:20"
                vol_mult = 1.0

                # Check Candle 3+ Breakout
                if len(today_df) >= 3:
                    for i in range(2, len(today_df)):
                        c_curr = today_df.iloc[i]
                        base_vol = max(c1['Volume'], c2['Volume'])
                        
                        if (c_curr['High'] > max(c1['High'], c2['High'])) and (c_curr['Close'] > c_curr['Open']) and (c_curr['Volume'] > base_vol * 1.5):
                            status = "READY"
                            sig_time = c_curr.name.strftime("%H:%M")
                            vol_mult = round(c_curr['Volume'] / base_vol, 2) if base_vol > 0 else 1.5
                            break

                bullish_list.append({
                    "Symbol": clean_sym, "Price": curr_price, "ChangePct": day_pct,
                    "SignalTime": sig_time, "VolMultiple": vol_mult, "StatusState": status,
                    "TVUrl": tv_url, "Qty": qty
                })

            # --- 🔴 BEARISH SETUP CONDITIONS ---
            c1_bear_ema = (c1['Close'] < c1['EMA20']) and (c1['Close'] < c1['EMA200'])
            c1_bear_prox = (abs(c1['Close'] - c1['EMA20']) / c1['Close'] * 100 <= 0.5)

            c2_inside_bear = (c2['High'] <= c1['High']) and (c2['Low'] >= c1['Low'])

            if c1_bear_ema and c1_bear_prox and c2_inside_bear:
                status = "WATCH"
                sig_time = "09:20"
                vol_mult = 1.0

                # Check Candle 3+ Breakdown
                if len(today_df) >= 3:
                    for i in range(2, len(today_df)):
                        c_curr = today_df.iloc[i]
                        base_vol = max(c1['Volume'], c2['Volume'])

                        if (c_curr['Low'] < min(c1['Low'], c2['Low'])) and (c_curr['Close'] < c_curr['Open']) and (c_curr['Volume'] > base_vol * 1.5):
                            status = "READY"
                            sig_time = c_curr.name.strftime("%H:%M")
                            vol_mult = round(c_curr['Volume'] / base_vol, 2) if base_vol > 0 else 1.5
                            break

                bearish_list.append({
                    "Symbol": clean_sym, "Price": curr_price, "ChangePct": day_pct,
                    "SignalTime": sig_time, "VolMultiple": vol_mult, "StatusState": status,
                    "TVUrl": tv_url, "Qty": qty
                })

        except:
            continue

    return bullish_list, bearish_list, len(bullish_list), len(bearish_list)

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

bull_signals, bear_signals, total_bull, total_bear = run_combined_scanner()

# --- DISPLAY TABLES ---
col_bull, col_bear = st.columns(2)

with col_bull:
    st.markdown('<div class="setup-header-bull">🟢 BULLISH BREAKOUT SETUPS</div>', unsafe_allow_html=True)
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
        st.info("No Bullish Breakout Setups Found.")

with col_bear:
    st.markdown('<div class="setup-header-bear">🔴 BEARISH BREAKDOWN SETUPS</div>', unsafe_allow_html=True)
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
        st.info("No Bearish Breakdown Setups Found.")
