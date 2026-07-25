import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import concurrent.futures
import os
import pytz
import time

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

# --- THEME CSS DEFINITIONS ---
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
        /* Hide Default Streamlit Chrome */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        
        /* Remove Page Padding */
        .block-container {{
            padding-top: 0.3rem !important;
            padding-bottom: 0.1rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            max-width: 100% !important;
        }}
        
        /* Dynamic Terminal Background */
        body, .stApp {{
            background-color: {bg_color} !important;
            color: {text_main} !important;
            font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
        }}

        /* HIDE ALL LOADING POPUPS / SPINNERS */
        div[data-testid="stStatusWidget"], div[data-testid="stSpinner"], .stSpinner {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }}

        /* Custom Larger Button Styling */
        .stButton>button {{
            background-color: {btn_bg} !important;
            color: {accent_blue} !important;
            border: 1px solid {border_color} !important;
            border-radius: 6px !important;
            font-weight: 800 !important;
            font-size: 12px !important;
            padding: 4px 8px !important;
            transition: all 0.2s !important;
            min-height: 0px !important;
            height: 38px !important;
            width: 100% !important;
        }}
        .stButton>button:hover {{
            border-color: {accent_blue} !important;
            color: {text_main} !important;
        }}

        /* CLEAN & BOLD TITLE TEXT */
        .nav-title-clean {{
            font-size: 17px;
            font-weight: 900;
            color: {accent_blue} !important;
            letter-spacing: 0.8px;
            font-family: 'Trebuchet MS', 'Impact', sans-serif;
            text-transform: uppercase;
            white-space: nowrap;
            line-height: 38px;
        }}

        /* SPACIOUS & LARGER TOP ROW INDEX PILLS WITH PROPER SPACING */
        .header-indices-wrapper {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 8px;
            width: 100%;
            height: 38px;
            white-space: nowrap;
        }}
        
        .idx-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background-color: {sub_card_bg};
            border: 1.5px solid {border_color};
            border-radius: 7px;
            padding: 4px 10px;
            text-decoration: none !important;
            font-size: 12px;
            transition: border-color 0.2s, transform 0.1s;
        }}
        .idx-pill:hover {{
            border-color: {accent_blue};
            transform: translateY(-1px);
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 11px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 11px; }}

        /* LIVE BLINKING ANIMATION */
        .live-blink {{
            animation: pulseBlink 1.2s ease-in-out infinite;
            display: inline-block;
        }}
        @keyframes pulseBlink {{
            0% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.25; transform: scale(0.95); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        /* COMPACT & NEAT MARKET STATUS TAGS */
        .market-status-open {{
            background-color: rgba(63, 185, 80, 0.15);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.4);
            padding: 3px 6px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: 800;
            white-space: nowrap;
            display: inline-block;
        }}
        
        .market-status-closed {{
            background-color: rgba(248, 81, 73, 0.15);
            color: #f85149;
            border: 1px solid rgba(248, 81, 73, 0.4);
            padding: 3px 6px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: 800;
            white-space: nowrap;
            display: inline-block;
        }}

        /* Metric Summary Cards */
        .metric-container {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px 14px;
            height: 100%;
        }}
        .card-label {{
            font-size: 11px;
            color: {text_sub};
            font-weight: 800;
            text-transform: uppercase;
        }}
        .card-value-green {{
            font-size: 18px;
            font-weight: 900;
            color: #3fb950;
            margin-top: 2px;
        }}
        .card-value-red {{
            font-size: 18px;
            font-weight: 900;
            color: #f85149;
            margin-top: 2px;
        }}

        /* Section Title Header */
        .box-container {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 10px;
            margin-bottom: 8px;
        }}
        .box-title {{
            font-size: 13px;
            font-weight: 800;
            color: {text_main};
            letter-spacing: 0.5px;
        }}
        
        /* MARKET MOVERS STOCK CARDS - COMPACT SIDE-BY-SIDE LAYOUT */
        .stock-card {{
            background-color: {sub_card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 8px 10px;
            text-align: left;
        }}
        .stock-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .stock-symbol {{
            font-size: 13px;
            font-weight: 800;
            color: {accent_blue};
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .stock-card-body {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 4px;
        }}
        .stock-price-up {{ font-size: 14px; font-weight: 900; color: #3fb950; }}
        .stock-price-down {{ font-size: 14px; font-weight: 900; color: #f85149; }}
        .stock-meta {{ font-size: 10px; color: {text_sub}; font-weight: 600; text-align: right; }}

        /* SETUP CONTAINER BOX */
        .setup-box {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 12px;
        }}
        .setup-header-bull {{
            font-size: 15px;
            font-weight: 900;
            color: #3fb950;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .setup-header-bear {{
            font-size: 15px;
            font-weight: 900;
            color: #f85149;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        /* TABLE HEADER BAR */
        .row-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 10px;
            font-size: 10px;
            font-weight: 800;
            color: {text_sub};
            text-transform: uppercase;
            border-bottom: 1px solid {border_color};
            margin-bottom: 6px;
        }}

        /* ROW ITEM WITH ROUNDED BUTTON BOX FOR SYMBOL */
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
            display: inline-block;
        }}

        /* STATUS BUTTON STYLES */
        .status-watch {{
            background-color: #C0C0C0;
            color: #000000;
            border: 1px solid #A9A9A9;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
            display: inline-block;
        }}

        .status-ready-bull {{
            background-color: #006400;
            color: #FFFFFF;
            border: 1px solid #004d00;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
            display: inline-block;
        }}

        .status-ready-bear {{
            background-color: #8B0000;
            color: #FFFFFF;
            border: 1px solid #660000;
            border-radius: 5px;
            padding: 3px 8px;
            font-weight: 900;
            font-size: 11px;
            display: inline-block;
        }}

        .vol-box {{
            background-color: rgba(210, 153, 34, 0.15);
            color: #d29922;
            border: 1px solid rgba(210, 153, 34, 0.4);
            border-radius: 4px;
            padding: 1px 5px;
            font-weight: 900;
            font-size: 10px;
            display: inline-block;
        }}

        .qty-box {{
            background-color: rgba(88, 166, 255, 0.15);
            color: {accent_blue};
            border: 1px solid rgba(88, 166, 255, 0.4);
            border-radius: 4px;
            padding: 1px 5px;
            font-weight: 900;
            font-size: 10px;
            display: inline-block;
        }}
    </style>
""", unsafe_allow_html=True)

# --- KEYWORDS TO STRICTLY BAN ETFs & FNO HEAVYWEIGHTS (TO PREFER CASH STOCKS) ---
ETF_KEYWORDS = ["BEES", "ETF", "GOLD", "SILVER", "LIQUID", "IWIN", "SETF", "HDFCMF", "ICICIMFC", "GILT", "NIFTY100", "MID150", "MOM50", "NIF100"]

# --- DYNAMIC CSV LOADER (FILTERING OUT ETFs) ---
@st.cache_data(ttl=3600)
def load_hira_stocks():
    csv_candidates = [
        "Hira Stocks (2).csv",
        "Hira Stocks (1).csv",
        "Hira Stocks.csv"
    ]
    for file_candidate in csv_candidates:
        if os.path.exists(file_candidate):
            try:
                df = pd.read_csv(file_candidate)
                col = 'symbol' if 'symbol' in df.columns else df.columns[0]
                syms = df[col].dropna().astype(str).str.strip().unique().tolist()
                
                # FILTER OUT ETFs
                filtered_syms = []
                for s in syms:
                    clean_s = s.upper()
                    if not any(kw in clean_s for kw in ETF_KEYWORDS):
                        filtered_syms.append(f"{s}.NS" if not s.endswith(".NS") else s)
                
                if len(filtered_syms) > 0:
                    return filtered_syms
            except Exception:
                pass
            
    return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']

ALL_HIRA_SYMBOLS = load_hira_stocks()
TOTAL_SCANNED_STOCKS = len(ALL_HIRA_SYMBOLS)

# --- ACCURATE FETCH FOR TOP INDICES ---
@st.cache_data(ttl=30)
def fetch_indices():
    indices = {
        "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
        "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
        "SENSEX": ("^BSESN", "BSE:SENSEX"),
        "NIFTY MIDCAP": ("NIFTY_MID_SELECT.NS", "NSE:NIFTY_MID_SELECT")
    }
    res = {}
    for name, (sym, tv_sym) in indices.items():
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="5d")
            tv_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
            
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = curr - prev
                pct = (change / prev) * 100
                res[name] = {"val": round(curr, 2), "change": round(change, 2), "pct": round(pct, 2), "url": tv_url}
            else:
                curr = ticker.fast_info.last_price
                prev = ticker.fast_info.previous_close
                if curr and prev:
                    change = curr - prev
                    pct = (change / prev) * 100
                    res[name] = {"val": round(curr, 2), "change": round(change, 2), "pct": round(pct, 2), "url": tv_url}
                else:
                    res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
        except:
            res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": f"https://www.tradingview.com/chart/?symbol={tv_sym}"}
    return res

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def analyze_stock_5m(symbol):
    try:
        clean_symbol = symbol.replace(".NS", "").upper()
        
        # DOUBLE CHECK ETF FILTER
        if any(kw in clean_symbol for kw in ETF_KEYWORDS):
            return None

        ticker = yf.Ticker(symbol)
        df_5m = ticker.history(period="5d", interval="5m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if len(df_5m) < 5 or len(df_daily) < 2:
            return None

        # CONTINUOUS 20 EMA CALCULATION
        df_5m['EMA20'] = calculate_ema(df_5m['Close'], 20)

        latest_trading_date = df_5m.index[-1].date()
        today_df = df_5m[df_5m.index.date == latest_trading_date].copy()
        
        if len(today_df) < 2:
            return None

        c1 = today_df.iloc[0] # 09:15 Candle
        c2 = today_df.iloc[1] # 09:20 Candle (Inside Bar / Profit Booking)

        # VOLUME FILTER: REJECT LOW VOLUME STOCKS (Base Candle Volume < 5,000)
        max_base_vol = max(c1['Volume'], c2['Volume'])
        if max_base_vol < 5000:
            return None

        latest = today_df.iloc[-1]
        curr_price = latest['Close']
        prev_close = df_daily['Close'].iloc[-2]
        day_change_pct = ((curr_price - prev_close) / prev_close) * 100
        change_pts = curr_price - prev_close

        tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
        calc_qty = int((10000 * 5) / curr_price) if curr_price > 0 else 0

        signal_bullish = False
        signal_bearish = False
        status_state = ""
        signal_time = "-"
        vol_multiple = 1.0

        # --- CANDLE 1 STRICT MOMENTUM & RANGE ANALYSIS ---
        c1_high, c1_low = c1['High'], c1['Low']
        c1_open, c1_close = c1['Open'], c1['Close']
        c1_range = c1_high - c1_low

        if c1_range == 0:
            return None

        c1_range_pct = (c1_range / c1_low) * 100

        # STRICT RULE 1: IF CANDLE 1 RANGE IS GREATER THAN 1.50%, IGNORE IMMEDIATELY
        if c1_range_pct > 1.50:
            return None

        c1_body = abs(c1_close - c1_open)
        body_ratio = c1_body / c1_range

        upper_wick = c1_high - max(c1_open, c1_close)
        lower_wick = min(c1_open, c1_close) - c1_low

        upper_wick_ratio = upper_wick / c1_range
        lower_wick_ratio = lower_wick / c1_range

        # --- STRICT BULLISH CONDITION ---
        c1_bull_cond = (
            (c1_range_pct <= 1.50) and 
            (c1_close > c1['EMA20']) and 
            (body_ratio >= 0.65) and 
            (upper_wick_ratio <= 0.25)
        )
        c2_bull_inside = (c2['High'] <= c1['High']) and (c2['Low'] >= c1['Low'])

        # --- STRICT BEARISH CONDITION ---
        c1_bear_cond = (
            (c1_range_pct <= 1.50) and 
            (c1_close < c1['EMA20']) and 
            (body_ratio >= 0.65) and 
            (lower_wick_ratio <= 0.25)
        )
        c2_bear_inside = (c2['High'] <= c1['High']) and (c2['Low'] >= c1['Low'])

        # --- CHECK BULLISH SIGNAL (STARTS AT WATCH) ---
        if c1_bull_cond and c2_bull_inside:
            signal_bullish = True
            status_state = "WATCH"
            signal_time = "09:20"
            
            if len(today_df) >= 3:
                for i in range(2, len(today_df)):
                    c_curr = today_df.iloc[i]
                    c_time_str = c_curr.name.strftime("%H:%M")
                    
                    if (c_curr['High'] > c1['High']):
                        status_state = "READY"
                        signal_time = c_time_str
                        vol_multiple = round(c_curr['Volume'] / max_base_vol, 2) if max_base_vol > 0 else 1.5
                        break

        # --- CHECK BEARISH SIGNAL (STARTS AT WATCH) ---
        if c1_bear_cond and c2_bear_inside:
            signal_bearish = True
            status_state = "WATCH"
            signal_time = "09:20"
            
            if len(today_df) >= 3:
                for i in range(2, len(today_df)):
                    c_curr = today_df.iloc[i]
                    c_time_str = c_curr.name.strftime("%H:%M")
                    
                    if (c_curr['Low'] < c1['Low']):
                        status_state = "READY"
                        signal_time = c_time_str
                        vol_multiple = round(c_curr['Volume'] / max_base_vol, 2) if max_base_vol > 0 else 1.5
                        break

        # Calculate Vol Surge for Market Movers
        latest_vol = latest['Volume']
        if max_base_vol > 0:
            vol_multiple = round(latest_vol / max_base_vol, 2)

        return {
            "Symbol": clean_symbol,
            "Price": curr_price,
            "ChangePct": day_change_pct,
            "ChangePts": round(change_pts, 2),
            "SignalTime": signal_time,
            "VolMultiple": vol_multiple,
            "IsBullish": signal_bullish,
            "IsBearish": signal_bearish,
            "StatusState": status_state,
            "TVUrl": tv_url,
            "Qty": calc_qty
        }
    except:
        return None

@st.cache_data(ttl=30)
def run_market_scanner():
    bullish_list = []
    bearish_list = []
    all_stocks = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(analyze_stock_5m, ALL_HIRA_SYMBOLS)
        for res in results:
            if res:
                all_stocks.append(res)
                if res['IsBullish']:
                    bullish_list.append(res)
                if res['IsBearish']:
                    bearish_list.append(res)

    all_df = pd.DataFrame(all_stocks)
    top_gainer = all_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict() if not all_df.empty else None
    top_loser = all_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict() if not all_df.empty else None

    # SORTING: READY SETUPS TOP, HIGH VOL MULTIPLE & CHANGE PCT TOP
    sorted_bullish = sorted(bullish_list, key=lambda x: (x['StatusState'] == 'READY', x['VolMultiple'], x['ChangePct']), reverse=True)
    sorted_bearish = sorted(bearish_list, key=lambda x: (x['StatusState'] == 'READY', x['VolMultiple'], abs(x['ChangePct'])), reverse=True)

    # LIMIT TO TOP 10
    top_bullish = sorted_bullish[:10]
    top_bearish = sorted_bearish[:10]

    gainers_4 = all_df.sort_values(by="ChangePct", ascending=False).head(4).to_dict('records') if not all_df.empty else []
    losers_4 = all_df.sort_values(by="ChangePct", ascending=True).head(4).to_dict('records') if not all_df.empty else []
    balanced_movers = gainers_4 + losers_4

    return top_bullish, top_bearish, top_gainer, top_loser, balanced_movers, len(bullish_list), len(bearish_list)

# --- MARKET OPEN / CLOSE LOGIC ---
ist_tz = pytz.timezone('Asia/Kolkata')
now_dt = datetime.datetime.now(ist_tz)

market_open_time = now_dt.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_dt.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_dt.weekday() < 5
is_market_open = is_weekday and (market_open_time <= now_dt <= market_close_time)

if is_market_open:
    status_html = '<span class="market-status-open"><span class="live-blink">🟢</span> MARKET OPEN</span>'
else:
    status_html = '<span class="market-status-closed"><span class="live-blink">🔴</span> MARKET CLOSED</span>'

# --- TOP SINGLE ROW NAVIGATION HEADER ---
top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b %Y | %I:%M:%S %p")

idx_pills_html = '<div class="header-indices-wrapper">'
for name, data in top_idx.items():
    pct = data.get('pct', 0)
    cls = "idx-up-p" if pct >= 0 else "idx-down-p"
    arrow = "▲" if pct >= 0 else "▼"
    url = data.get("url", "#")
    val = data.get("val", 0)
    
    idx_pills_html += (
        f'<a class="idx-pill" href="{url}" target="_blank">'
        f'<span class="idx-lbl">{name}:</span> '
        f'<span class="idx-num">{val:,.2f}</span> '
        f'<span class="{cls}">{arrow}{pct:+.2f}%</span>'
        f'</a>'
    )
idx_pills_html += '</div>'

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns([0.15, 0.53, 0.09, 0.11, 0.06, 0.06])

with nav_col1:
    st.markdown('<div class="nav-title-clean">HIRA MOUNT TRADER</div>', unsafe_allow_html=True)

with nav_col2:
    st.markdown(idx_pills_html, unsafe_allow_html=True)

with nav_col3:
    st.markdown(f'<div style="margin-top:6px; text-align:center;">{status_html}</div>', unsafe_allow_html=True)

with nav_col4:
    st.markdown(f'<div style="font-size: 11px; color: {text_sub}; font-weight: 800; margin-top:8px; white-space:nowrap;">🕒 {now_time}</div>', unsafe_allow_html=True)

with nav_col5:
    theme_icon = "🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light"
    if st.button(theme_icon):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.query_params['theme'] = st.session_state.theme
        st.rerun()

with nav_col6:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- EXECUTE SCANNER ---
bullish_signals, bearish_signals, top_gainer, top_loser, market_movers, total_bull_cnt, total_bear_cnt = run_market_scanner()

# --- METRIC CARDS ROW ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    if top_gainer:
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP GAINER</div>
                <a href="{top_gainer['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 800; color: {accent_blue}; margin-top:2px;">{top_gainer['Symbol']}</div>
                    <div class="card-value-green">+{top_gainer['ChangePct']:.2f}% <span style="font-size:12px; font-weight:normal;">(+₹{top_gainer['ChangePts']})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c2:
    if top_loser:
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP LOSER</div>
                <a href="{top_loser['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 800; color: {accent_blue}; margin-top:2px;">{top_loser['Symbol']}</div>
                    <div class="card-value-red">{top_loser['ChangePct']:.2f}% <span style="font-size:12px; font-weight:normal;">(₹{top_loser['ChangePts']})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 16px; font-weight: 900; color: {text_main}; margin-top:2px;">
                <span class="live-blink">🟢</span> {'Bullish' if total_bull_cnt >= total_bear_cnt else 'Bearish'}
            </div>
            <div style="font-size: 11px; color: {text_sub}; margin-top: 2px;">Bullish: {total_bull_cnt} | Bearish: {total_bear_cnt}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">SCANNED STOCKS</div>
            <div style="font-size: 16px; font-weight: 900; color: {accent_blue}; margin-top:2px;">
                {TOTAL_SCANNED_STOCKS} Stocks
            </div>
            <div style="font-size: 11px; color: #3fb950; font-weight: 700; margin-top: 2px;">Active Signals: {total_bull_cnt + total_bear_cnt}</div>
        </div>
    """, unsafe_allow_html=True)

# --- MARKET MOVERS (COMPACT SIDE-BY-SIDE QTY & VOL BOXES) ---
st.markdown("""
    <div class="box-container">
        <div class="box-title">🔥 MARKET MOVERS</div>
    </div>
""", unsafe_allow_html=True)

if market_movers:
    m_cols = st.columns(len(market_movers))
    for i, m in enumerate(market_movers):
        with m_cols[i]:
            p_class = "stock-price-up" if m['ChangePct'] >= 0 else "stock-price-down"
            sign = "+" if m['ChangePct'] >= 0 else ""
            
            time_str = m['SignalTime'] if m['SignalTime'] != "-" else "09:20"
            
            st.markdown(f"""
                <a href="{m['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-card-top">
                            <span class="stock-symbol">{m['Symbol']}</span>
                            <div style="display:flex; gap:3px;">
                                <span class="qty-box" title="Quantity">{m['Qty']}</span>
                                <span class="vol-box" title="Volume Surge">{m['VolMultiple']:.1f}x</span>
                            </div>
                        </div>
                        <div class="stock-card-body">
                            <div>
                                <span class="{p_class} live-blink">₹{m['Price']:.2f}</span>
                                <span style="font-size: 11px; font-weight: 800; color: {'#3fb950' if m['ChangePct']>=0 else '#f85149'};">
                                    {sign}{m['ChangePct']:.2f}%
                                </span>
                            </div>
                            <div class="stock-meta">🕒 {time_str}</div>
                        </div>
                    </div>
                </a>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- ROW LIST (BULLISH & BEARISH SETUPS - CLEAN HEADERS) ---
tb_col1, tb_col2 = st.columns(2)

with tb_col1:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bull"><span class="live-blink">🟢</span> BULLISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span>
                <span style="width: 15%;">STATUS</span>
                <span style="width: 15%;">ALERT TIME</span>
                <span style="width: 15%;">VOL SURGE</span>
                <span style="width: 12%;">QTY</span>
                <span style="width: 11%; text-align:right;">PRICE</span>
                <span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if bullish_signals:
        for s in bullish_signals:
            if s['StatusState'] == 'WATCH':
                status_btn_html = '<span class="status-watch">WATCH</span>'
            else:
                status_btn_html = '<span class="status-ready-bull">READY</span>'

            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box">{s['Symbol']}</span></div>
                    <div style="width: 15%;">{status_btn_html}</div>
                    <div style="width: 15%; font-size:11px; color:{text_sub}; font-weight:700;">🕒 {s['SignalTime']}</div>
                    <div style="width: 15%;"><span class="vol-box">{s['VolMultiple']:.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s['Qty']}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:13px;" class="live-blink">₹{s['Price']:.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#3fb950; font-size:12px;">▲{s['ChangePct']:.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:600;">Searching for High-Volume Bullish breakouts...</div>', unsafe_allow_html=True)

with tb_col2:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bear"><span class="live-blink">🔴</span> BEARISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span>
                <span style="width: 15%;">STATUS</span>
                <span style="width: 15%;">ALERT TIME</span>
                <span style="width: 15%;">VOL SURGE</span>
                <span style="width: 12%;">QTY</span>
                <span style="width: 11%; text-align:right;">PRICE</span>
                <span style="width: 11%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if bearish_signals:
        for s in bearish_signals:
            if s['StatusState'] == 'WATCH':
                status_btn_html = '<span class="status-watch">WATCH</span>'
            else:
                status_btn_html = '<span class="status-ready-bear">READY</span>'

            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box" style="color:#f85149;">{s['Symbol']}</span></div>
                    <div style="width: 15%;">{status_btn_html}</div>
                    <div style="width: 15%; font-size:11px; color:{text_sub}; font-weight:700;">🕒 {s['SignalTime']}</div>
                    <div style="width: 15%;"><span class="vol-box">{s['VolMultiple']:.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s['Qty']}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:13px;" class="live-blink">₹{s['Price']:.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#f85149; font-size:12px;">▼{s['ChangePct']:.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:600;">Searching for High-Volume Bearish breakdowns...</div>', unsafe_allow_html=True)

# --- AUTO-REFRESH (30 SECONDS) ---
if is_market_open:
    st.markdown("""
        <script>
            setTimeout(function(){
                window.location.reload();
            }, 30000);
        </script>
    """, unsafe_allow_html=True)
