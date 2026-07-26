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

# --- CUSTOM ENHANCED CSS WITH PERFECT TOP HEADER COMPACT SPACING ---
st.markdown(f"""
    <style>
        header {{visibility: hidden !important; height: 0px !important;}}
        footer {{visibility: hidden !important; display: none !important;}}
        #MainMenu {{visibility: hidden !important;}}
        div[data-testid="stStatusWidget"], div[data-testid="stDecoration"], div[class*="viewerBadge"], div[data-testid="stToolbar"] {{
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }}
        .block-container {{
            padding-top: 0.4rem !important; padding-bottom: 0.2rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; max-width: 100% !important;
        }}
        body, .stApp {{
            background-color: {bg_color} !important; color: {text_main} !important; font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
        }}
        div[data-testid="stSpinner"], .stSpinner {{
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }}
        
        /* BUTTONS */
        .stButton>button {{
            background-color: {btn_bg} !important; color: {accent_blue} !important; border: 1px solid {border_color} !important;
            border-radius: 6px !important; font-weight: 800 !important; font-size: 12px !important; padding: 2px 6px !important;
            transition: all 0.2s !important; min-height: 0px !important; height: 36px !important; width: 100% !important;
        }}
        .stButton>button:hover {{ border-color: {accent_blue} !important; color: {text_main} !important; }}
        
        /* TOP HEADER COMPACT & CLEAN ALIGNMENT */
        .brand-logo {{
            font-size: 18px; font-weight: 900; color: {accent_blue} !important; letter-spacing: 0.5px;
            font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; white-space: nowrap; line-height: 36px;
        }}
        .indices-bar-wrapper {{
            display: flex; align-items: center; justify-content: flex-start; gap: 4px; width: 100%; height: 36px; overflow-x: auto;
        }}
        .idx-pill {{
            display: inline-flex; align-items: center; gap: 4px; background-color: {sub_card_bg}; border: 1.5px solid {border_color};
            border-radius: 6px; padding: 4px 6px; text-decoration: none !important; font-size: 11px; white-space: nowrap;
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 10px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 11px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 11px; }}
        
        .header-status-box {{ display: flex; align-items: center; justify-content: center; height: 36px; white-space: nowrap; }}
        .header-time-box {{ display: flex; align-items: center; justify-content: center; height: 36px; font-size: 11px; color: {text_sub}; font-weight: 800; white-space: nowrap; }}

        .market-status-open {{ background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1.5px solid rgba(63, 185, 80, 0.4); padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 900; }}
        .market-status-closed {{ background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1.5px solid rgba(248, 81, 73, 0.4); padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 900; }}
        
        /* TOP 4 METRIC CARDS */
        .metric-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 12px 14px; height: 100%; box-sizing: border-box; }}
        .card-label {{ font-size: 11px; color: {text_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-value-green {{ font-size: 18px; font-weight: 900; color: #3fb950; margin-top: 4px; }}
        .card-value-red {{ font-size: 18px; font-weight: 900; color: #f85149; margin-top: 4px; }}
        
        .box-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-top: 10px; margin-bottom: 8px; }}
        .box-title {{ font-size: 14px; font-weight: 900; color: {text_main}; letter-spacing: 0.5px; }}
        
        /* MARKET MOVERS CARDS */
        .stock-card {{ background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px 12px; text-align: left; }}
        .stock-card-top {{ display: flex; justify-content: space-between; align-items: center; }}
        .stock-symbol {{ font-size: 14px; font-weight: 900; color: {accent_blue}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .stock-card-body {{ display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }}
        .stock-price-up {{ font-size: 15px; font-weight: 900; color: #3fb950; }}
        .stock-price-down {{ font-size: 15px; font-weight: 900; color: #f85149; }}
        .stock-meta {{ font-size: 11px; color: {text_sub}; font-weight: 700; text-align: right; }}
        
        /* TABLES & ROWS */
        .setup-box {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 10px; padding: 12px; }}
        .setup-header-bull {{ font-size: 16px; font-weight: 900; color: #3fb950; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .setup-header-bear {{ font-size: 16px; font-weight: 900; color: #f85149; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        
        .row-header {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; font-size: 11px; font-weight: 900; color: {text_sub}; text-transform: uppercase; border-bottom: 1px solid {border_color}; margin-bottom: 8px; }}
        .stock-row-item {{ display: flex; justify-content: space-between; align-items: center; background-color: {sub_card_bg}; border: 1px solid {border_color}; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; text-decoration: none !important; }}
        .sym-btn-box {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 5px; padding: 3px 8px; color: {accent_blue}; font-weight: 900; font-size: 13px; display: inline-block; }}
        
        .status-watch {{ background-color: #C0C0C0; color: #000000; border: 1px solid #A9A9A9; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .status-ready-bull {{ background-color: #006400; color: #FFFFFF; border: 1px solid #004d00; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .status-ready-bear {{ background-color: #8B0000; color: #FFFFFF; border: 1px solid #660000; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .vol-box {{ background-color: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); border-radius: 5px; padding: 2px 6px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .qty-box {{ background-color: rgba(88, 166, 255, 0.15); color: {accent_blue}; border: 1px solid rgba(88, 166, 255, 0.4); border-radius: 5px; padding: 2px 6px; font-weight: 900; font-size: 11px; display: inline-block; }}

        .live-blink {{ animation: pulseBlink 6.0s ease-in-out infinite; display: inline-block; }}
        @keyframes pulseBlink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    </style>
""", unsafe_allow_html=True)

ETF_KEYWORDS = ["BEES", "ETF", "GOLD", "SILVER", "LIQUID", "IWIN", "SETF", "HDFCMF", "ICICIMFC", "GILT", "NIFTY100", "MID150", "MOM50", "NIF100"]

FNO_STOCKS = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS", "ALKEM", "AMBUJACEMENT", 
    "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", 
    "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", 
    "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BSOFT", "BPCL", "BRITANNIA", "CANBK", "CANFINHOME", "CHAMBLFERT", 
    "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", 
    "DABUR", "DALBHARAT", "DEEPAKNTR", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", 
    "FEDERALBNK", "GAIL", "GLENMARK", "GMMPFAUDLR", "GNFC", "GODREJPROP", "GODREJCP", "GRANULES", "GRASIM", "GUJGASLTD", 
    "HAL", "HAVELLS", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HDFCAMC", "HEROMOTOCO", "HINDALCO", "HAL", "HINDCOPPER", 
    "HINDPETRO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", 
    "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC", "ITC", "JINDALSTEL", 
    "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "LALPATHLAB", "LT", "LTIM", "LTF", "LTI", "LTTS", 
    "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", 
    "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", 
    "NTPC", "OBEROIRLTY", "OFFS", "ONGC", "PAGEIND", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", 
    "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", 
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEMICALS", 
    "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", 
    "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE"
]

@st.cache_data(ttl=86400)
def load_hira_stocks():
    csv_candidates = ["Hira Stocks (2).csv", "Hira Stocks (1).csv", "Hira Stocks.csv"]
    for file_candidate in csv_candidates:
        if os.path.exists(file_candidate):
            try:
                df = pd.read_csv(file_candidate)
                col = 'symbol' if 'symbol' in df.columns else df.columns[0]
                syms = df[col].dropna().astype(str).str.strip().unique().tolist()
                filtered_syms = []
                for s in syms:
                    clean_s = s.upper().replace(".NS", "")
                    if (not any(kw in clean_s for kw in ETF_KEYWORDS)) and (clean_s not in FNO_STOCKS):
                        filtered_syms.append(f"{s}.NS" if not s.endswith(".NS") else s)
                if len(filtered_syms) > 0:
                    return filtered_syms
            except Exception:
                pass
    return ['ALOKINDS.NS', 'TRIDENT.NS', 'SUZLON.NS', 'BDL.NS', 'SJVN.NS']

ALL_HIRA_SYMBOLS = load_hira_stocks()
TOTAL_SCANNED_STOCKS = len(ALL_HIRA_SYMBOLS)

# --- MARKET TIME DETECTOR ---
ist_tz = pytz.timezone('Asia/Kolkata')
now_dt = datetime.datetime.now(ist_tz)
market_open_time = now_dt.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_dt.replace(hour=15, minute=30, second=0, microsecond=0)
is_market_open = (now_dt.weekday() < 5) and (market_open_time <= now_dt <= market_close_time)

cache_ttl_seconds = 60 if is_market_open else 3600

@st.cache_data(ttl=cache_ttl_seconds)
def fetch_indices():
    indices = {
        "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
        "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
        "SENSEX": ("^BSESN", "BSE:SENSEX"),
        "MIDCAP": ("NIFTY_MID_SELECT.NS", "NSE:NIFTY_MID_SELECT")
    }
    symbols = [v[0] for v in indices.values()]
    res = {}
    try:
        data = yf.download(symbols, period="5d", interval="1d", progress=False, group_by="ticker")
        for name, (sym, tv_sym) in indices.items():
            tv_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
            try:
                df = data[sym].dropna() if len(symbols) > 1 else data.dropna()
                if len(df) >= 2:
                    curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    change = curr - prev
                    res[name] = {"val": round(float(curr), 2), "change": round(float(change), 2), "pct": round(float((change/prev)*100), 2), "url": tv_url}
                else:
                    res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
            except Exception:
                res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
    except Exception:
        for name, (sym, tv_sym) in indices.items():
            res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": f"https://www.tradingview.com/chart/?symbol={tv_sym}"}
    return res

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def calculate_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / df['Volume'].cumsum()

@st.cache_data(ttl=cache_ttl_seconds)
def run_market_scanner():
    bullish_list, bearish_list, all_stocks = [], [], []
    per_trade_cap = 10000

    chunk_size = 100
    symbol_chunks = [ALL_HIRA_SYMBOLS[i:i + chunk_size] for i in range(0, len(ALL_HIRA_SYMBOLS), chunk_size)]

    for chunk in symbol_chunks:
        try:
            bulk_5m = yf.download(chunk, period="2d", interval="5m", progress=False, group_by="ticker", threads=True)
            bulk_1d = yf.download(chunk, period="5d", interval="1d", progress=False, group_by="ticker", threads=True)
        except Exception:
            continue

        if bulk_5m is None or bulk_1d is None:
            continue

        for symbol in chunk:
            try:
                clean_symbol = symbol.replace(".NS", "").upper()
                df_5m = bulk_5m[symbol].dropna() if len(chunk) > 1 else bulk_5m.dropna()
                df_daily = bulk_1d[symbol].dropna() if len(chunk) > 1 else bulk_1d.dropna()

                if len(df_5m) < 15 or len(df_daily) < 2:
                    continue

                df_5m['EMA20'] = calculate_ema(df_5m['Close'], 20)
                df_5m['EMA200'] = calculate_ema(df_5m['Close'], 200)
                df_5m['VWAP'] = calculate_vwap(df_5m)

                latest_trading_date = df_5m.index[-1].date()
                today_df = df_5m[df_5m.index.date == latest_trading_date].copy()

                if len(today_df) < 2:
                    continue

                prev_day = df_daily.iloc[-2]
                is_prev_day_sideways = (((prev_day['High'] - prev_day['Low']) / prev_day['Close']) * 100) <= 1.5

                c1, c2 = today_df.iloc[0], today_df.iloc[1]
                c1_high, c1_low, c1_open, c1_close = float(c1['High']), float(c1['Low']), float(c1['Open']), float(c1['Close'])
                c1_range = c1_high - c1_low

                if c1_range == 0:
                    continue

                c1_range_pct = (c1_range / c1_close) * 100
                c1_ema20_dist = abs(c1_close - float(c1['EMA20'])) / c1_close * 100
                c1_ema200_dist = abs(c1_close - float(c1['EMA200'])) / c1_close * 100

                body_ratio = abs(c1_close - c1_open) / c1_range
                upper_wick_ratio = (c1_high - max(c1_open, c1_close)) / c1_range
                lower_wick_ratio = (min(c1_open, c1_close) - c1_low) / c1_range

                max_base_vol = max(float(c1['Volume']), float(c2['Volume']))
                if max_base_vol < 1000:
                    continue

                valid_closes = today_df['Close'].dropna()
                if valid_closes.empty:
                    continue
                curr_price = float(valid_closes.iloc[-1])

                valid_daily_closes = df_daily['Close'].dropna()
                prev_close = float(valid_daily_closes.iloc[-2]) if len(valid_daily_closes) >= 2 else curr_price

                if curr_price <= 0:
                    continue

                day_change_pct = float(((curr_price - prev_close) / prev_close) * 100)
                change_pts = float(curr_price - prev_close)
                tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
                
                calc_qty = max(1, int((per_trade_cap * 5) / curr_price))

                signal_bullish, signal_bearish = False, False
                status_state, signal_time, vol_multiple = "", "-", 1.0

                c1_bull_cond = (
                    is_prev_day_sideways and (c1_close > c1_low) and (c1_range_pct <= 1.5) and
                    (body_ratio >= 0.55) and (upper_wick_ratio <= 0.30) and (c1_close >= float(c1['VWAP'])) and
                    (c1_close > float(c1['EMA20'])) and (c1_close > float(c1['EMA200'])) and
                    (c1_ema20_dist <= 0.3) and (c1_ema200_dist <= 0.3)
                )

                c2_bull_cond = (
                    (float(c2['High']) <= c1_high) and (float(c2['Low']) >= c1_low) and (float(c2['High']) < c1_high) and
                    (float(c2['Close']) >= (float(c2['Low']) + (float(c2['High']) - float(c2['Low'])) * 0.3)) and
                    ((float(c2['High']) - float(c2['Low'])) <= c1_range)
                )

                c1_bear_cond = (
                    is_prev_day_sideways and (c1_close < c1_high) and (c1_range_pct <= 1.5) and
                    (body_ratio >= 0.55) and (lower_wick_ratio <= 0.30) and (c1_close <= float(c1['VWAP'])) and
                    (c1_close < float(c1['EMA20'])) and (c1_close < float(c1['EMA200'])) and
                    (c1_ema20_dist <= 0.3) and (c1_ema200_dist <= 0.3)
                )

                c2_bear_cond = (
                    (float(c2['High']) <= c1_high) and (float(c2['Low']) >= c1_low) and (float(c2['Low']) > c1_low) and
                    (float(c2['Close']) <= (float(c2['High']) - (float(c2['High']) - float(c2['Low'])) * 0.3)) and
                    ((float(c2['High']) - float(c2['Low'])) <= c1_range)
                )

                if c1_bull_cond and c2_bull_cond:
                    signal_bullish = True
                    status_state, signal_time = "WATCH", "09:20"
                    if len(today_df) >= 3:
                        for i in range(2, len(today_df)):
                            c_curr = today_df.iloc[i]
                            if (float(c_curr['High']) > max(c1_high, float(c2['High']))) and (float(c_curr['Close']) > float(c_curr['Open'])) and (float(c_curr['Close']) > float(c_curr['VWAP'])) and (float(c_curr['Volume']) > (max_base_vol * 1.5)):
                                status_state = "READY"
                                signal_time = c_curr.name.strftime("%H:%M")
                                vol_multiple = float(round(float(c_curr['Volume']) / max_base_vol, 2)) if max_base_vol > 0 else 1.5
                                break

                elif c1_bear_cond and c2_bear_cond:
                    signal_bearish = True
                    status_state, signal_time = "WATCH", "09:20"
                    if len(today_df) >= 3:
                        for i in range(2, len(today_df)):
                            c_curr = today_df.iloc[i]
                            if (float(c_curr['Low']) < min(c1_low, float(c2['Low']))) and (float(c_curr['Close']) < float(c_curr['Open'])) and (float(c_curr['Close']) < float(c_curr['VWAP'])) and (float(c_curr['Volume']) > (max_base_vol * 1.5)):
                                status_state = "READY"
                                signal_time = c_curr.name.strftime("%H:%M")
                                vol_multiple = float(round(float(c_curr['Volume']) / max_base_vol, 2)) if max_base_vol > 0 else 1.5
                                break

                latest_vol = float(today_df.iloc[-1]['Volume'])
                if max_base_vol > 0 and vol_multiple == 1.0:
                    vol_multiple = float(round(latest_vol / max_base_vol, 2))

                res = {
                    "Symbol": str(clean_symbol), 
                    "Price": float(curr_price), 
                    "ChangePct": float(day_change_pct),
                    "ChangePts": float(round(change_pts, 2)), 
                    "SignalTime": str(signal_time), 
                    "VolMultiple": float(vol_multiple),
                    "IsBullish": bool(signal_bullish), 
                    "IsBearish": bool(signal_bearish), 
                    "StatusState": str(status_state),
                    "TVUrl": str(tv_url), 
                    "Qty": int(calc_qty)
                }
                all_stocks.append(res)
                if signal_bullish: bullish_list.append(res)
                if signal_bearish: bearish_list.append(res)
            except Exception:
                continue

    all_df = pd.DataFrame(all_stocks)
    
    top_gainer, top_loser, balanced_movers = None, None, []

    if not all_df.empty:
        try:
            top_gainer = all_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict()
            top_loser = all_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict()

            gainers_4 = all_df.sort_values(by="ChangePct", ascending=False).head(4).to_dict('records')
            losers_4 = all_df.sort_values(by="ChangePct", ascending=True).head(4).to_dict('records')
            balanced_movers = gainers_4 + losers_4
        except Exception:
            pass

    # 🚀 SORTING & TOP 10 DISPLAY LIMIT
    sorted_bullish = sorted(bullish_list, key=lambda x: (x.get('StatusState') == 'READY', x.get('VolMultiple', 0), x.get('ChangePct', 0)), reverse=True)
    sorted_bearish = sorted(bearish_list, key=lambda x: (x.get('StatusState') == 'READY', x.get('VolMultiple', 0), abs(x.get('ChangePct', 0))), reverse=True)

    top_bullish = sorted_bullish[:10]
    top_bearish = sorted_bearish[:10]

    return top_bullish, top_bearish, top_gainer, top_loser, balanced_movers, len(bullish_list), len(bearish_list)

# --- MARKET STATUS & HEADER HTML ---
status_html = '<span class="market-status-open"><span class="live-blink">🟢</span> OPEN</span>' if is_market_open else '<span class="market-status-closed"><span class="live-blink">🔴</span> CLOSED</span>'

top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b | %I:%M %p")

# --- 🎯 PERFECT SINGLE LINE TOP HEADER ---
head_c1, head_c2, head_c3, head_c4, head_c5, head_c6 = st.columns([0.16, 0.51, 0.07, 0.10, 0.08, 0.08])

with head_c1:
    st.markdown('<div class="brand-logo">HIRA MOUNT TRADER</div>', unsafe_allow_html=True)

with head_c2:
    idx_pills_html = '<div class="indices-bar-wrapper">'
    for name, data in top_idx.items():
        pct = data.get('pct', 0)
        cls = "idx-up-p" if pct >= 0 else "idx-down-p"
        arrow = "▲" if pct >= 0 else "▼"
        idx_pills_html += f'<a class="idx-pill" href="{data.get("url", "#")}" target="_blank"><span class="idx-lbl">{name}:</span> <span class="idx-num">{data.get("val", 0):,.2f}</span> <span class="{cls}">{arrow}{pct:+.2f}%</span></a>'
    idx_pills_html += '</div>'
    st.markdown(idx_pills_html, unsafe_allow_html=True)

with head_c3:
    st.markdown(f'<div class="header-status-box">{status_html}</div>', unsafe_allow_html=True)

with head_c4:
    st.markdown(f'<div class="header-time-box">🕒 {now_time}</div>', unsafe_allow_html=True)

with head_c5:
    if st.button("🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.query_params['theme'] = st.session_state.theme
        st.rerun()

with head_c6:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<hr style='margin-top: 4px; margin-bottom: 10px; border-color: {border_color}; opacity: 0.5;'>", unsafe_allow_html=True)

# --- EXECUTE SCANNER ---
bullish_signals, bearish_signals, top_gainer, top_loser, market_movers, total_bull_cnt, total_bear_cnt = run_market_scanner()
sideways_cnt = TOTAL_SCANNED_STOCKS - (total_bull_cnt + total_bear_cnt)
sentiment_label = "Bullish" if total_bull_cnt >= total_bear_cnt else "Bearish"
sentiment_color = "#3fb950" if total_bull_cnt >= total_bear_cnt else "#f85149"
sentiment_blink = "🟢" if total_bull_cnt >= total_bear_cnt else "🔴"
sentiment_arrow = "▲" if total_bull_cnt >= total_bear_cnt else "▼"

c1, c2, c3, c4 = st.columns(4)

with c1:
    if top_gainer and isinstance(top_gainer, dict):
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP GAINER</div>
                <a href="{top_gainer.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 900; color: {accent_blue}; margin-top:3px; overflow:hidden; text-overflow:ellipsis;">{top_gainer.get('Symbol', '-')}</div>
                    <div class="card-value-green">+{top_gainer.get('ChangePct', 0):.2f}% <span style="font-size:12px; font-weight:700;">(+₹{top_gainer.get('ChangePts', 0)})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c2:
    if top_loser and isinstance(top_loser, dict):
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP LOSER</div>
                <a href="{top_loser.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 900; color: {accent_blue}; margin-top:3px; overflow:hidden; text-overflow:ellipsis;">{top_loser.get('Symbol', '-')}</div>
                    <div class="card-value-red">{top_loser.get('ChangePct', 0):.2f}% <span style="font-size:12px; font-weight:700;">(₹{top_loser.get('ChangePts', 0)})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 17px; font-weight: 900; color: {sentiment_color}; margin-top:3px; display:flex; align-items:center; gap:6px;">
                <span class="live-blink">{sentiment_blink}</span>
                <span>{sentiment_label}</span>
                <span style="font-size:13px;">{sentiment_arrow}</span>
            </div>
            <div style="font-size: 11px; color: {text_sub}; margin-top: 3px; font-weight: 800;">
                <span style="color:#3fb950;">▲ {total_bull_cnt}</span> | 
                <span style="color:#f85149;">▼ {total_bear_cnt}</span> | 
                <span>⚪ {sideways_cnt}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">SCANNED STOCKS</div>
            <div style="font-size: 17px; font-weight: 900; color: {accent_blue}; margin-top:3px;">
                {TOTAL_SCANNED_STOCKS} Stocks
            </div>
            <div style="font-size: 11px; color: #3fb950; font-weight: 800; margin-top: 3px;">Active: {total_bull_cnt + total_bear_cnt}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="box-container"><div class="box-title">🔥 MARKET MOVERS</div></div>""", unsafe_allow_html=True)

if market_movers:
    m_cols = st.columns(len(market_movers))
    for i, m in enumerate(market_movers):
        with m_cols[i]:
            p_class = "stock-price-up" if m.get('ChangePct', 0) >= 0 else "stock-price-down"
            sign = "+" if m.get('ChangePct', 0) >= 0 else ""
            time_str = m.get('SignalTime', '09:20') if m.get('SignalTime') != "-" else "09:20"
            st.markdown(f"""
                <a href="{m.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-card-top">
                            <span class="stock-symbol">{m.get('Symbol', '-')}</span>
                            <div style="display:flex; gap:3px;">
                                <span class="qty-box">{m.get('Qty', 1)}</span>
                                <span class="vol-box">{m.get('VolMultiple', 1.0):.1f}x</span>
                            </div>
                        </div>
                        <div class="stock-card-body">
                            <div>
                                <span class="{p_class} live-blink">₹{m.get('Price', 0):.2f}</span>
                                <span style="font-size: 12px; font-weight: 900; color: {'#3fb950' if m.get('ChangePct', 0)>=0 else '#f85149'};">{sign}{m.get('ChangePct', 0):.2f}%</span>
                            </div>
                            <div class="stock-meta">🕒 {time_str}</div>
                        </div>
                    </div>
                </a>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

tb_col1, tb_col2 = st.columns(2)

with tb_col1:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bull"><span class="live-blink">🟢</span> BULLISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span><span style="width: 15%;">STATUS</span><span style="width: 15%;">ALERT TIME</span><span style="width: 15%;">VOL SURGE</span><span style="width: 12%;">QTY</span><span style="width: 11%; text-align:right;">PRICE</span><span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if bullish_signals:
        for s in bullish_signals[:10]:
            status_btn = '<span class="status-watch">WATCH</span>' if s.get('StatusState') == 'WATCH' else '<span class="status-ready-bull">READY</span>'
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box">{s.get('Symbol')}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
                    <div style="width: 15%; font-size:12px; color:{text_sub}; font-weight:800;">🕒 {s.get('SignalTime')}</div>
                    <div style="width: 15%;"><span class="vol-box">{s.get('VolMultiple', 1.0):.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s.get('Qty', 1)}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:14px;" class="live-blink">₹{s.get('Price', 0):.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#3fb950; font-size:13px;">▲{s.get('ChangePct', 0):.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:700; font-size:13px;">Searching for High-Volume Bullish breakouts...</div>', unsafe_allow_html=True)

with tb_col2:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bear"><span class="live-blink">🔴</span> BEARISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span><span style="width: 15%;">STATUS</span><span style="width: 15%;">ALERT TIME</span><span style="width: 15%;">VOL SURGE</span><span style="width: 12%;">QTY</span><span style="width: 11%; text-align:right;">PRICE</span><span style="width: 11%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if bearish_signals:
        for s in bearish_signals[:10]:
            status_btn = '<span class="status-watch">WATCH</span>' if s.get('StatusState') == 'WATCH' else '<span class="status-ready-bear">READY</span>'
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box" style="color:#f85149;">{s.get('Symbol')}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
                    <div style="width: 15%; font-size:12px; color:{text_sub}; font-weight:800;">🕒 {s.get('SignalTime')}</div>
                    <div style="width: 15%;"><span class="vol-box">{s.get('VolMultiple', 1.0):.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s.get('Qty', 1)}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:14px;" class="live-blink">₹{s.get('Price', 0):.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#f85149; font-size:13px;">▼{s.get('ChangePct', 0):.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:700; font-size:13px;">Searching for High-Volume Bearish breakdowns...</div>', unsafe_allow_html=True)

if is_market_open:
    st.markdown("""<script>setTimeout(function(){ window.location.reload(); }, 30000);</script>""", unsafe_allow_html=True)
