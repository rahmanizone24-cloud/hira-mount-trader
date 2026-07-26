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
        div[data-testid="stStatusWidget"], div[data-testid="stDecoration"], div[class*="viewerBadge"], div[data-testid="stToolbar"] {{
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }}
        .block-container {{
            padding-top: 0.3rem !important; padding-bottom: 0.1rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; max-width: 100% !important;
        }}
        body, .stApp {{
            background-color: {bg_color} !important; color: {text_main} !important; font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
        }}
        div[data-testid="stSpinner"], .stSpinner {{
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }}
        .stButton>button {{
            background-color: {btn_bg} !important; color: {accent_blue} !important; border: 1px solid {border_color} !important;
            border-radius: 6px !important; font-weight: 800 !important; font-size: 12px !important; padding: 4px 8px !important;
            transition: all 0.2s !important; min-height: 0px !important; height: 38px !important; width: 100% !important;
        }}
        .stButton>button:hover {{ border-color: {accent_blue} !important; color: {text_main} !important; }}
        .nav-title-clean {{
            font-size: 17px; font-weight: 900; color: {accent_blue} !important; letter-spacing: 0.8px;
            font-family: 'Trebuchet MS', 'Impact', sans-serif; text-transform: uppercase; white-space: nowrap; line-height: 38px;
        }}
        .header-indices-wrapper {{ display: flex; align-items: center; justify-content: flex-start; gap: 8px; width: 100%; height: 38px; white-space: nowrap; }}
        .idx-pill {{ display: inline-flex; align-items: center; gap: 5px; background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 7px; padding: 4px 10px; text-decoration: none !important; font-size: 12px; transition: border-color 0.2s, transform 0.1s; }}
        .idx-pill:hover {{ border-color: {accent_blue}; transform: translateY(-1px); }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 11px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 11px; }}
        .live-blink {{ animation: pulseBlink 6.0s ease-in-out infinite; display: inline-block; }}
        @keyframes pulseBlink {{ 0% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.40; transform: scale(0.98); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        .market-status-open {{ background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1px solid rgba(63, 185, 80, 0.4); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; white-space: nowrap; display: block; text-align: center; }}
        .market-status-closed {{ background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; white-space: nowrap; display: block; text-align: center; }}
        .metric-container {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px 12px; height: 100%; box-sizing: border-box; }}
        .card-label {{ font-size: 10px; color: {text_sub}; font-weight: 800; text-transform: uppercase; }}
        .card-value-green {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-top: 2px; }}
        .card-value-red {{ font-size: 15px; font-weight: 900; color: #f85149; margin-top: 2px; }}
        .box-container {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-top: 10px; margin-bottom: 8px; }}
        .box-title {{ font-size: 13px; font-weight: 800; color: {text_main}; letter-spacing: 0.5px; }}
        .stock-card {{ background-color: {sub_card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 8px 10px; text-align: left; }}
        .stock-card-top {{ display: flex; justify-content: space-between; align-items: center; }}
        .stock-symbol {{ font-size: 13px; font-weight: 800; color: {accent_blue}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .stock-card-body {{ display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }}
        .stock-price-up {{ font-size: 14px; font-weight: 900; color: #3fb950; }}
        .stock-price-down {{ font-size: 14px; font-weight: 900; color: #f85149; }}
        .stock-meta {{ font-size: 10px; color: {text_sub}; font-weight: 600; text-align: right; }}
        .setup-box {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 12px; }}
        .setup-header-bull {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .setup-header-bear {{ font-size: 15px; font-weight: 900; color: #f85149; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .row-header {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; font-size: 10px; font-weight: 800; color: {text_sub}; text-transform: uppercase; border-bottom: 1px solid {border_color}; margin-bottom: 6px; }}
        .stock-row-item {{ display: flex; justify-content: space-between; align-items: center; background-color: {sub_card_bg}; border: 1px solid {border_color}; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px; text-decoration: none !important; }}
        .sym-btn-box {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 5px; padding: 4px 10px; color: {accent_blue}; font-weight: 800; font-size: 12px; display: inline-block; }}
        .status-watch {{ background-color: #C0C0C0; color: #000000; border: 1px solid #A9A9A9; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .status-ready-bull {{ background-color: #006400; color: #FFFFFF; border: 1px solid #004d00; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .status-ready-bear {{ background-color: #8B0000; color: #FFFFFF; border: 1px solid #660000; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .vol-box {{ background-color: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); border-radius: 4px; padding: 1px 5px; font-weight: 900; font-size: 10px; display: inline-block; }}
        .qty-box {{ background-color: rgba(88, 166, 255, 0.15); color: {accent_blue}; border: 1px solid rgba(88, 166, 255, 0.4); border-radius: 4px; padding: 1px 5px; font-weight: 900; font-size: 10px; display: inline-block; }}

        @media screen and (max-width: 768px) {{
            div[data-testid="column"]:has(div.nav-title-clean) {{ width: 50% !important; order: 1 !important; float: left !important; text-align: center !important; }}
            .nav-title-clean {{ text-align: center !important; font-size: 15px !important; }}
            div[data-testid="column"]:has(button) {{ width: 25% !important; float: left !important; margin-bottom: 8px !important; }}
            div[data-testid="column"]:has(div.header-indices-wrapper) {{ width: 100% !important; clear: both !important; margin-bottom: 8px !important; }}
            .header-indices-wrapper {{ display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 6px !important; height: auto !important; white-space: normal !important; }}
            .idx-pill {{ width: 100% !important; justify-content: space-between !important; padding: 4px 6px !important; }}
            div[data-testid="column"]:has(span.market-status-closed), div[data-testid="column"]:has(span.market-status-open) {{ width: 100% !important; clear: both !important; margin-bottom: 4px !important; }}
            div[data-testid="column"]:has(div[style*="white-space:nowrap"]) {{ width: 100% !important; text-align: center !important; margin-bottom: 10px !important; }}
            div[data-testid="column"]:has(div.metric-container) {{ width: 48.5% !important; display: inline-block !important; float: left !important; margin-bottom: 8px !important; }}
            div[data-testid="column"]:has(div.setup-box) {{ width: 100% !important; display: block !important; clear: both !important; margin-bottom: 12px !important; }}
            .row-header, .stock-row-item {{ min-width: 380px !important; }}
            .setup-box {{ overflow-x: auto !important; }}
        }}
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
    "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", 
    "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", 
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEMICALS", 
    "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", 
    "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE"
]

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=60)
def fetch_indices():
    indices = {
        "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
        "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
        "SENSEX": ("^BSESN", "BSE:SENSEX"),
        "NIFTY MIDCAP": ("NIFTY_MID_SELECT.NS", "NSE:NIFTY_MID_SELECT")
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
                    res[name] = {"val": round(curr, 2), "change": round(change, 2), "pct": round((change/prev)*100, 2), "url": tv_url}
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

@st.cache_data(ttl=60)
def run_market_scanner():
    bullish_list, bearish_list, all_stocks = [], [], []
    try:
        bulk_5m = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="5m", progress=False, group_by="ticker", threads=True)
        bulk_1d = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="1d", progress=False, group_by="ticker", threads=True)
    except Exception:
        return [], [], None, None, [], 0, 0

    if bulk_5m is None or bulk_1d is None:
        return [], [], None, None, [], 0, 0

    per_trade_cap = 10000

    for symbol in ALL_HIRA_SYMBOLS:
        try:
            clean_symbol = symbol.replace(".NS", "").upper()
            df_5m = bulk_5m[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_5m.dropna()
            df_daily = bulk_1d[symbol].dropna() if len(ALL_HIRA_SYMBOLS) > 1 else bulk_1d.dropna()

            if len(df_5m) < 20 or len(df_daily) < 2:
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
            c1_high, c1_low, c1_open, c1_close = c1['High'], c1['Low'], c1['Open'], c1['Close']
            c1_range = c1_high - c1_low

            if c1_range == 0:
                continue

            c1_range_pct = (c1_range / c1_close) * 100
            c1_ema20_dist = abs(c1_close - c1['EMA20']) / c1_close * 100
            c1_ema200_dist = abs(c1_close - c1['EMA200']) / c1_close * 100

            body_ratio = abs(c1_close - c1_open) / c1_range
            upper_wick_ratio = (c1_high - max(c1_open, c1_close)) / c1_range
            lower_wick_ratio = (min(c1_open, c1_close) - c1_low) / c1_range

            max_base_vol = max(c1['Volume'], c2['Volume'])
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

            day_change_pct = ((curr_price - prev_close) / prev_close) * 100
            change_pts = curr_price - prev_close
            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
            
            calc_qty = max(1, int((per_trade_cap * 5) / curr_price))

            signal_bullish, signal_bearish = False, False
            status_state, signal_time, vol_multiple = "", "-", 1.0

            c1_bull_cond = (
                is_prev_day_sideways and (c1_close > c1_low) and (c1_range_pct <= 1.5) and
                (body_ratio >= 0.55) and (upper_wick_ratio <= 0.30) and (c1_close >= c1['VWAP']) and
                (c1_close > c1['EMA20']) and (c1_close > c1['EMA200']) and
                (c1_ema20_dist <= 0.3) and (c1_ema200_dist <= 0.3)
            )

            c2_bull_cond = (
                (c2['High'] <= c1_high) and (c2['Low'] >= c1_low) and (c2['High'] < c1_high) and
                (c2['Close'] >= (c2['Low'] + (c2['High'] - c2['Low']) * 0.3)) and
                ((c2['High'] - c2['Low']) <= c1_range)
            )

            c1_bear_cond = (
                is_prev_day_sideways and (c1_close < c1_high) and (c1_range_pct <= 1.5) and
                (body_ratio >= 0.55) and (lower_wick_ratio <= 0.30) and (c1_close <= c1['VWAP']) and
                (c1_close < c1['EMA20']) and (c1_close < c1['EMA200']) and
                (c1_ema20_dist <= 0.3) and (c1_ema200_dist <= 0.3)
            )

            c2_bear_cond = (
                (c2['High'] <= c1_high) and (c2['Low'] >= c1_low) and (c2['Low'] > c1_low) and
                (c2['Close'] <= (c2['High'] - (c2['High'] - c2['Low']) * 0.3)) and
                ((c2['High'] - c2['Low']) <= c1_range)
            )

            if c1_bull_cond and c2_bull_cond:
                signal_bullish = True
                status_state, signal_time = "WATCH", "09:20"
                if len(today_df) >= 3:
                    for i in range(2, len(today_df)):
                        c_curr = today_df.iloc[i]
                        if (c_curr['High'] > max(c1_high, c2['High'])) and (c_curr['Close'] > c_curr['Open']) and (c_curr['Close'] > c_curr['VWAP']) and (c_curr['Volume'] > (max_base_vol * 1.5)):
                            status_state = "READY"
                            signal_time = c_curr.name.strftime("%H:%M")
                            vol_multiple = round(c_curr['Volume'] / max_base_vol, 2) if max_base_vol > 0 else 1.5
                            break

            elif c1_bear_cond and c2_bear_cond:
                signal_bearish = True
                status_state, signal_time = "WATCH", "09:20"
                if len(today_df) >= 3:
                    for i in range(2, len(today_df)):
                        c_curr = today_df.iloc[i]
                        if (c_curr['Low'] < min(c1_low, c2['Low'])) and (c_curr['Close'] < c_curr['Open']) and (c_curr['Close'] < c_curr['VWAP']) and (c_curr['Volume'] > (max_base_vol * 1.5)):
                            status_state = "READY"
                            signal_time = c_curr.name.strftime("%H:%M")
                            vol_multiple = round(c_curr['Volume'] / max_base_vol, 2) if max_base_vol > 0 else 1.5
                            break

            latest_vol = today_df.iloc[-1]['Volume']
            if max_base_vol > 0 and vol_multiple == 1.0:
                vol_multiple = round(latest_vol / max_base_vol, 2)

            res = {
                "Symbol": clean_symbol, "Price": curr_price, "ChangePct": day_change_pct,
                "ChangePts": round(change_pts, 2), "SignalTime": signal_time, "VolMultiple": vol_multiple,
                "IsBullish": signal_bullish, "IsBearish": signal_bearish, "StatusState": status_state,
                "TVUrl": tv_url, "Qty": calc_qty
            }
            all_stocks.append(res)
            if signal_bullish: bullish_list.append(res)
            if signal_bearish: bearish_list.append(res)
        except Exception:
            continue

    all_df = pd.DataFrame(all_stocks)
    top_gainer = all_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict() if not all_df.empty else None
    top_loser = all_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict() if not all_df.empty else None

    sorted_bullish = sorted(bullish_list, key=lambda x: (x['StatusState'] == 'READY', x['VolMultiple'], x['ChangePct']), reverse=True)
    sorted_bearish = sorted(bearish_list, key=lambda x: (x['StatusState'] == 'READY', x['VolMultiple'], abs(x['ChangePct'])), reverse=True)

    top_bullish = sorted_bullish[:10]
    top_bearish = sorted_bearish[:10]

    gainers_4 = all_df.sort_values(by="ChangePct", ascending=False).head(4).to_dict('records') if not all_df.empty else []
    losers_4 = all_df.sort_values(by="ChangePct", ascending=True).head(4).to_dict('records') if not all_df.empty else []
    balanced_movers = gainers_4 + losers_4

    return top_bullish, top_bearish, top_gainer, top_loser, balanced_movers, len(bullish_list), len(bearish_list)

# --- MARKET TIME & HEADER ---
ist_tz = pytz.timezone('Asia/Kolkata')
now_dt = datetime.datetime.now(ist_tz)
market_open_time = now_dt.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_dt.replace(hour=15, minute=30, second=0, microsecond=0)
is_market_open = (now_dt.weekday() < 5) and (market_open_time <= now_dt <= market_close_time)

status_html = '<span class="market-status-open"><span class="live-blink">🟢</span> MARKET OPEN</span>' if is_market_open else '<span class="market-status-closed"><span class="live-blink">🔴</span> MARKET CLOSED</span>'

top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b %Y | %I:%M:%S %p")

idx_pills_html = '<div class="header-indices-wrapper">'
for name, data in top_idx.items():
    pct = data.get('pct', 0)
    cls = "idx-up-p" if pct >= 0 else "idx-down-p"
    arrow = "▲" if pct >= 0 else "▼"
    idx_pills_html += f'<a class="idx-pill" href="{data.get("url", "#")}" target="_blank"><span class="idx-lbl">{name}:</span> <span class="idx-num">{data.get("val", 0):,.2f}</span> <span class="{cls}">{arrow}{pct:+.2f}%</span></a>'
idx_pills_html += '</div>'

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns([0.08, 0.52, 0.10, 0.12, 0.09, 0.09])

with nav_col1:
    if st.button("🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.query_params['theme'] = st.session_state.theme
        st.rerun()

with nav_col2:
    st.markdown('<div class="nav-title-clean">HIRA MOUNT TRADER</div>', unsafe_allow_html=True)

with nav_col3:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown(idx_pills_html, unsafe_allow_html=True)

m_status_col1, m_status_col2 = st.columns([0.5, 0.5])
with m_status_col1:
    st.markdown(f'<div style="margin-top:4px; text-align:center;">{status_html}</div>', unsafe_allow_html=True)

with m_status_col2:
    st.markdown(f'<div style="font-size: 11px; color: {text_sub}; font-weight: 800; margin-top:8px; white-space:nowrap; text-align:center;">🕒 {now_time}</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- EXECUTE SCANNER ---
bullish_signals, bearish_signals, top_gainer, top_loser, market_movers, total_bull_cnt, total_bear_cnt = run_market_scanner()
sideways_cnt = TOTAL_SCANNED_STOCKS - (total_bull_cnt + total_bear_cnt)
sentiment_label = "Bullish" if total_bull_cnt >= total_bear_cnt else "Bearish"
sentiment_color = "#3fb950" if total_bull_cnt >= total_bear_cnt else "#f85149"
sentiment_blink = "🟢" if total_bull_cnt >= total_bear_cnt else "🔴"
sentiment_arrow = "▲" if total_bull_cnt >= total_bear_cnt else "▼"

c1, c2, c3, c4 = st.columns(4)

with c1:
    if top_gainer:
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP GAINER</div>
                <a href="{top_gainer['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 14px; font-weight: 800; color: {accent_blue}; margin-top:2px; overflow:hidden; text-overflow:ellipsis;">{top_gainer['Symbol']}</div>
                    <div class="card-value-green">+{top_gainer['ChangePct']:.2f}% <span style="font-size:10px; font-weight:normal;">(+₹{top_gainer['ChangePts']})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c2:
    if top_loser:
        st.markdown(f"""
            <div class="metric-container">
                <div class="card-label">TOP LOSER</div>
                <a href="{top_loser['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 14px; font-weight: 800; color: {accent_blue}; margin-top:2px; overflow:hidden; text-overflow:ellipsis;">{top_loser['Symbol']}</div>
                    <div class="card-value-red">{top_loser['ChangePct']:.2f}% <span style="font-size:10px; font-weight:normal;">(₹{top_loser['ChangePts']})</span></div>
                </a>
            </div>
        """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 15px; font-weight: 900; color: {sentiment_color}; margin-top:2px; display:flex; align-items:center; gap:4px;">
                <span class="live-blink">{sentiment_blink}</span>
                <span>{sentiment_label}</span>
                <span style="font-size:12px;">{sentiment_arrow}</span>
            </div>
            <div style="font-size: 9px; color: {text_sub}; margin-top: 3px; font-weight: 700; white-space:nowrap;">
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
            <div style="font-size: 15px; font-weight: 900; color: {accent_blue}; margin-top:2px;">
                {TOTAL_SCANNED_STOCKS} Stocks
            </div>
            <div style="font-size: 10px; color: #3fb950; font-weight: 700; margin-top: 2px;">Active: {total_bull_cnt + total_bear_cnt}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="box-container"><div class="box-title">🔥 MARKET MOVERS</div></div>""", unsafe_allow_html=True)

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
                                <span class="qty-box">{m['Qty']}</span>
                                <span class="vol-box">{m['VolMultiple']:.1f}x</span>
                            </div>
                        </div>
                        <div class="stock-card-body">
                            <div>
                                <span class="{p_class} live-blink">₹{m['Price']:.2f}</span>
                                <span style="font-size: 11px; font-weight: 800; color: {'#3fb950' if m['ChangePct']>=0 else '#f85149'};">{sign}{m['ChangePct']:.2f}%</span>
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
        for s in bullish_signals:
            status_btn = '<span class="status-watch">WATCH</span>' if s['StatusState'] == 'WATCH' else '<span class="status-ready-bull">READY</span>'
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box">{s['Symbol']}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
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
                <span style="width: 20%;">SYMBOL</span><span style="width: 15%;">STATUS</span><span style="width: 15%;">ALERT TIME</span><span style="width: 15%;">VOL SURGE</span><span style="width: 12%;">QTY</span><span style="width: 11%; text-align:right;">PRICE</span><span style="width: 11%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if bearish_signals:
        for s in bearish_signals:
            status_btn = '<span class="status-watch">WATCH</span>' if s['StatusState'] == 'WATCH' else '<span class="status-ready-bear">READY</span>'
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box" style="color:#f85149;">{s['Symbol']}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
                    <div style="width: 15%; font-size:11px; color:{text_sub}; font-weight:700;">🕒 {s['SignalTime']}</div>
                    <div style="width: 15%;"><span class="vol-box">{s['VolMultiple']:.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s['Qty']}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:13px;" class="live-blink">₹{s['Price']:.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#f85149; font-size:12px;">▼{s['ChangePct']:.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:600;">Searching for High-Volume Bearish breakdowns...</div>', unsafe_allow_html=True)

if is_market_open:
    st.markdown("""<script>setTimeout(function(){ window.location.reload(); }, 30000);</script>""", unsafe_allow_html=True)
