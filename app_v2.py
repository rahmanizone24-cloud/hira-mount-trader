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

# --- STRICT F&O STOCKS BLACKLIST (FULLY EXCLUDED) ---
FNO_STOCKS = {
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS",
    "ALKEM", "AMBUJACEMENT", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL",
    "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE",
    "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT",
    "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BSOFT", "BOSCHLTD", "BPCL", "BRITANNIA",
    "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE",
    "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT",
    "DEEPAKNTR", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND",
    "FEDERALBNK", "GAIL", "GLENMARK", "GMMPFAUDLR", "GNFC", "GODREJPROP", "GRANULES",
    "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "ICICIBANK",
    "ICICIGI", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM",
    "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC",
    "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "LALPATHLAB",
    "LAURUSLABS", "LICHSGFIN", "LT", "LTIM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM",
    "MARICO", "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON",
    "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND",
    "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PERSISTENT", "PETRONET",
    "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM",
    "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM",
    "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEM", "TATACOMM",
    "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM",
    "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE",
    "CAMS", "PATANJALI", "UTIAMC", "CHOICEIN", "SUNDRMFAST", "BOSCHLTD", "DMART", "LICI"
}

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
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        
        .block-container {{
            padding-top: 0.1rem !important;
            padding-bottom: 0.1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }}
        
        body, .stApp {{
            background-color: {bg_color} !important;
            color: {text_main} !important;
            font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
        }}
        
        .stApp > div {{
            opacity: 1 !important;
            transition: none !important;
        }}

        div[data-testid="stStatusWidget"], div[data-testid="stSpinner"], .stSpinner {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }}

        .stButton>button {{
            background-color: {btn_bg} !important;
            color: {accent_blue} !important;
            border: 1px solid {border_color} !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            font-size: 11px !important;
            padding: 3px 8px !important;
            transition: all 0.2s !important;
            min-height: 0px !important;
            height: 32px !important;
        }}
        .stButton>button:hover {{
            border-color: {accent_blue} !important;
            color: {text_main} !important;
        }}

        .top-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: {card_bg};
            padding: 8px 14px;
            border: 1px solid {border_color};
            border-radius: 8px;
            margin-bottom: 12px;
        }}
        
        .nav-title-clean {{
            font-size: 18px;
            font-weight: 900;
            color: {accent_blue} !important;
            letter-spacing: 1.2px;
            font-family: 'Trebuchet MS', 'Impact', sans-serif;
            text-transform: uppercase;
            display: inline-block;
        }}

        .nav-indices {{
            display: flex;
            gap: 12px;
            font-size: 12px;
            align-items: center;
        }}
        .idx-item {{
            display: flex;
            gap: 5px;
            align-items: center;
            text-decoration: none !important;
            padding: 3px 6px;
            border-radius: 5px;
            background-color: {sub_card_bg};
            border: 1px solid {border_color};
        }}
        .idx-name {{ color: {text_sub}; font-weight: 700; font-size: 10px; }}
        .idx-val {{ color: {text_main}; font-weight: 800; font-size: 11px; }}
        .idx-up {{ color: #3fb950; font-weight: bold; }}
        .idx-down {{ color: #f85149; font-weight: bold; }}

        .live-blink {{
            animation: pulseBlink 1.2s ease-in-out infinite;
            display: inline-block;
        }}
        @keyframes pulseBlink {{
            0% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.25; transform: scale(0.95); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        .market-status-open {{
            background-color: rgba(63, 185, 80, 0.15);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.4);
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .market-status-closed {{
            background-color: rgba(248, 81, 73, 0.15);
            color: #f85149;
            border: 1px solid rgba(248, 81, 73, 0.4);
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 5px;
        }}

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
        
        .stock-card {{
            background-color: {sub_card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px 10px;
            text-align: left;
        }}
        .stock-symbol {{
            font-size: 14px;
            font-weight: 800;
            color: {accent_blue};
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .stock-price-up {{ font-size: 16px; font-weight: 900; color: #3fb950; margin: 2px 0; }}
        .stock-price-down {{ font-size: 16px; font-weight: 900; color: #f85149; margin: 2px 0; }}
        .stock-meta {{ font-size: 10px; color: {text_sub}; font-weight: 600; }}

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

        .vol-box {{
            background-color: rgba(210, 153, 34, 0.15);
            color: #d29922;
            border: 1px solid rgba(210, 153, 34, 0.4);
            border-radius: 5px;
            padding: 2px 6px;
            font-weight: 900;
            font-size: 11px;
        }}

        .qty-box {{
            background-color: rgba(88, 166, 255, 0.15);
            color: {accent_blue};
            border: 1px solid rgba(88, 166, 255, 0.4);
            border-radius: 5px;
            padding: 2px 6px;
            font-weight: 900;
            font-size: 11px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- LOAD CASH ONLY STOCKS (HARD FILTER FOR F&O) ---
@st.cache_data(ttl=3600)
def load_hira_stocks():
    raw_symbols = []
    
    possible_files = [
        "Hira_Filtered_Cash_Stocks_100_2500.csv", 
        "Hira_Non_FNO_Stocks.csv", 
        "Hira Stocks.csv"
    ]
    
    loaded = False
    for csv_file in possible_files:
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                syms = df['symbol'].dropna().astype(str).str.strip().unique().tolist()
                raw_symbols = syms
                loaded = True
                break
            except Exception:
                pass
            
    if not loaded:
        raw_symbols = [
            "BLUESTARCO", "JSWDULUX", "ABSLAMC", "BAJAJCON", "MMFL", "PGIL", "ABREL",
            "GANDHITUBE", "TRITURBINE", "PRAJIND", "ASAHIINDIA", "APCOTEXIND", "BBTC",
            "INDOTECH", "KEC", "SUBROS", "CARBORUNIV", "MASTEK", "DCMSHRIRAM", "MINDACORP",
            "GMRINFRA", "AARTIDRUGS", "GENUSPOWER", "KPITTECH", "SCHAEFFLER", "FINPIPE",
            "JBCHEPHARM", "SWANENERGY", "SUPREMEIND", "ZENSARTECH", "CGPOWER", "CDSL",
            "SWSOLAR", "KFINTECH", "MAPMYINDIA", "KAYNES", "TRIDENT", "CEINFO", "NETWEB",
            "DOMS", "HAPPYFORGE", "DATAPATTNS", "PREMIERENE", "TATAINVEST", "OLECTRA", "RAYMOND", "RITES"
        ]

    # ABSOLUTE HARD FILTER TO REMOVE ANY FNO STOCK
    clean_cash_symbols = []
    for s in raw_symbols:
        clean_name = s.replace(".NS", "").strip().upper()
        if clean_name not in FNO_STOCKS:
            clean_cash_symbols.append(f"{clean_name}.NS")

    return clean_cash_symbols

NIFTY_CASH_ONLY_SYMBOLS = load_hira_stocks()
TOTAL_SCANNED_STOCKS = len(NIFTY_CASH_ONLY_SYMBOLS)

# --- FETCH INDEX DATA ---
@st.cache_data(ttl=30)
def fetch_indices():
    indices = {
        "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
        "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
        "SENSEX": ("^BSESN", "BSE:SENSEX"),
        "NIFTY MIDCAP": ("NIFTY_MID_SELECT.NS", "NSE:NIFTY_MID_SELECT")
    }
    res = {}
    for name, (sym, tv_sym) in indices.items():
        try:
            df = yf.Ticker(sym).history(period="2d")
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = curr - prev
                pct = (change / prev) * 100
                tv_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
                res[name] = {"val": round(curr, 2), "change": round(change, 2), "pct": round(pct, 2), "url": tv_url}
        except:
            res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": "#"}
    return res

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def calculate_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / df['Volume'].cumsum()

def analyze_stock_5m(symbol):
    try:
        clean_symbol = symbol.replace(".NS", "").strip().upper()
        
        # DOUBLE CHECK HARD BLOCK FOR FNO STOCKS
        if clean_symbol in FNO_STOCKS:
            return None

        ticker = yf.Ticker(symbol)
        df_5m = ticker.history(period="5d", interval="5m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if len(df_5m) < 25 or len(df_daily) < 2:
            return None

        # PRICE RANGE FILTER: 100 TO 2500 ONLY
        latest_price_check = df_5m['Close'].iloc[-1]
        if not (100 <= latest_price_check <= 2500):
            return None

        # LIQUIDITY FILTER
        avg_daily_vol = df_daily['Volume'].iloc[-2] if len(df_daily) >= 2 else 0
        if avg_daily_vol < 100000:
            return None

        today = df_5m.index[-1].date()
        today_df = df_5m[df_5m.index.date == today].copy()
        
        if len(today_df) < 3:
            return None

        prev_close = df_daily['Close'].iloc[-2]

        today_df['EMA20'] = calculate_ema(today_df['Close'], 20)
        today_df['EMA200'] = calculate_ema(today_df['Close'], 200)
        today_df['VWAP'] = calculate_vwap(today_df)

        c1 = today_df.iloc[0]
        c1_open = c1['Open']
        c1_high = c1['High']
        c1_low = c1['Low']
        c1_close = c1['Close']
        c1_range = c1_high - c1_low

        if c1_range <= 0:
            return None

        # GAP CONDITION
        gap_pct = abs((c1_open - prev_close) / prev_close) * 100
        if gap_pct > 0.8:
            return None

        # C1 HEIGHT FILTER
        c1_height_pct = (c1_range / c1_open) * 100
        if c1_height_pct > 1.2:
            return None

        # WICK CONDITION
        c1_upper_wick = c1_high - max(c1_open, c1_close)
        c1_lower_wick = min(c1_open, c1_close) - c1_low
        if (c1_upper_wick / c1_range > 0.30) or (c1_lower_wick / c1_range > 0.30):
            return None

        # C2 PAUSE CANDLE
        c2 = today_df.iloc[1]
        c2_inside = (c2['High'] <= c1_high) and (c2['Low'] >= c1_low)
        if not c2_inside:
            return None

        # EMA PROXIMITY CHECK
        c1_ema20 = c1['EMA20']
        c1_ema200 = c1['EMA200']
        
        dist_ema20 = abs(c1_close - c1_ema20) / c1_ema20 * 100
        dist_ema200 = abs(c1_close - c1_ema200) / c1_ema200 * 100

        if dist_ema20 > 1.5 or dist_ema200 > 2.0:
            return None

        c1_green = c1_close > c1_open
        c1_red = c1_close < c1_open

        latest = today_df.iloc[-1]
        curr_price = latest['Close']
        pdl = df_daily['Low'].iloc[-2]
        day_change_pct = ((curr_price - prev_close) / prev_close) * 100
        change_pts = curr_price - prev_close

        tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"

        signal_bullish = False
        signal_bearish = False
        signal_time = ""
        vol_multiple = 1.0

        # BREAKOUT LOGIC
        if c1_green and (c1_close >= c1_ema20) and (c1_close >= c1_ema200):
            for i in range(2, len(today_df)):
                c_curr = today_df.iloc[i]
                if (c_curr['Close'] > c1_high and 
                    c_curr['Volume'] > c2['Volume'] and 
                    c_curr['Close'] > c_curr['EMA200'] and 
                    c_curr['Close'] > c_curr['EMA20'] and
                    c_curr['Close'] > c_curr['VWAP']):
                    
                    signal_bullish = True
                    signal_time = c_curr.name.strftime("%H:%M")
                    vol_multiple = round(c_curr['Volume'] / (c2['Volume'] if c2['Volume'] > 0 else 1), 2)
                    break

        is_near_pdl = c1_open <= (pdl * 1.015)
        if c1_red and (c1_close <= c1_ema20) and (c1_close <= c1_ema200) and is_near_pdl:
            for i in range(2, len(today_df)):
                c_curr = today_df.iloc[i]
                if (c_curr['Close'] < c1_low and 
                    c_curr['Volume'] > c2['Volume'] and 
                    c_curr['Close'] < c_curr['EMA200'] and 
                    c_curr['Close'] < c_curr['EMA20'] and
                    c_curr['Close'] < c_curr['VWAP']):
                    
                    signal_bearish = True
                    signal_time = c_curr.name.strftime("%H:%M")
                    vol_multiple = round(c_curr['Volume'] / (c2['Volume'] if c2['Volume'] > 0 else 1), 2)
                    break

        # POSITION SIZING (₹10,000 Capital with 5x Intraday Margin)
        calc_qty = int((10000 * 5) / curr_price) if curr_price > 0 else 0

        if signal_bullish or signal_bearish:
            return {
                "Symbol": clean_symbol,
                "Price": curr_price,
                "ChangePct": day_change_pct,
                "ChangePts": round(change_pts, 2),
                "SignalTime": signal_time if signal_time else "10:15",
                "VolMultiple": vol_multiple if vol_multiple > 1.0 else 1.50,
                "IsBullish": signal_bullish,
                "IsBearish": signal_bearish,
                "TVUrl": tv_url,
                "Qty": calc_qty
            }
        return None
    except:
        return None

@st.cache_data(ttl=30)
def run_market_scanner():
    bullish_list = []
    bearish_list = []
    all_stocks = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        results = executor.map(analyze_stock_5m, NIFTY_CASH_ONLY_SYMBOLS)
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
    
    bullish_top10 = sorted(bullish_list, key=lambda x: x['VolMultiple'], reverse=True)[:10]
    bearish_top10 = sorted(bearish_list, key=lambda x: x['VolMultiple'], reverse=True)[:10]

    gainers_4 = all_df.sort_values(by="ChangePct", ascending=False).head(4).to_dict('records') if not all_df.empty else []
    losers_4 = all_df.sort_values(by="ChangePct", ascending=True).head(4).to_dict('records') if not all_df.empty else []
    balanced_movers = gainers_4 + losers_4

    return bullish_top10, bearish_top10, top_gainer, top_loser, balanced_movers, len(bullish_list), len(bearish_list)

# --- AUTOMATIC MARKET OPEN / CLOSE LOGIC ---
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

# --- TOP BAR ---
top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b %Y | %I:%M:%S %p")

head_col1, head_col2 = st.columns([0.80, 0.20])

with head_col1:
    idx_items_html = ""
    for name, data in top_idx.items():
        cls = "idx-up" if data.get('pct', 0) >= 0 else "idx-down"
        arrow = "▲" if data.get('pct', 0) >= 0 else "▼"
        url = data.get("url", "#")
        val = data.get("val", 0)
        pct = data.get("pct", 0)
        idx_items_html += f'<a class="idx-item" href="{url}" target="_blank"><span class="idx-name">{name}:</span> <span class="idx-val">{val:,}</span> <span class="{cls}">{arrow} {pct}%</span></a>'

    st.markdown(f"""
        <div class="top-nav">
            <div class="nav-title-clean">HIRA MOUNT TRADER</div>
            <div class="nav-indices">
                {idx_items_html}
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                {status_html}
                <div style="font-size: 11px; color: {text_sub}; font-weight: 700;">🕒 {now_time}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        theme_icon = "🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light"
        if st.button(theme_icon, use_container_width=True):
            new_theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.session_state.theme = new_theme
            st.query_params['theme'] = new_theme
            st.rerun()
    with btn_c2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

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
                {TOTAL_SCANNED_STOCKS} Cash Stocks
            </div>
            <div style="font-size: 11px; color: #3fb950; font-weight: 700; margin-top: 2px;">Active Signals: {total_bull_cnt + total_bear_cnt}</div>
        </div>
    """, unsafe_allow_html=True)

# --- MARKET MOVERS ---
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
            st.markdown(f"""
                <a href="{m['TVUrl']}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-symbol">{m['Symbol']}</div>
                        <div class="{p_class} live-blink">₹{m['Price']:.2f}</div>
                        <div style="font-size: 12px; font-weight: 800; color: {'#3fb950' if m['ChangePct']>=0 else '#f85149'};">
                            {sign}{m['ChangePct']:.2f}%
                        </div>
                        <div class="stock-meta">🕒 Trigger: {m['SignalTime']}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- SETUP TABLES ---
tb_col1, tb_col2 = st.columns(2)

with tb_col1:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bull"><span class="live-blink">🟢</span> BULLISH SETUPS</div>
            <div class="row-header">
                <span style="width: 25%;">SYMBOL</span>
                <span style="width: 18%;">TRIGGER</span>
                <span style="width: 18%;">VOL SURGE</span>
                <span style="width: 15%;">QTY</span>
                <span style="width: 12%; text-align:right;">PRICE</span>
                <span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
    """, unsafe_allow_html=True)
    
    if bullish_signals:
        for s in bullish_signals:
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 25%;"><span class="sym-btn-box">{s['Symbol']}</span></div>
                    <div style="width: 18%; font-size:11px; color:{text_sub}; font-weight:700;">🕒 {s['SignalTime']}</div>
                    <div style="width: 18%;"><span class="vol-box">{s['VolMultiple']:.2f}x</span></div>
                    <div style="width: 15%;"><span class="qty-box">{s['Qty']}</span></div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:{text_main}; font-size:13px;" class="live-blink">₹{s['Price']:.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#3fb950; font-size:12px;">▲{s['ChangePct']:.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:600;">Searching for Pure Pause Candle breakouts in Hira Stocks...</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tb_col2:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bear"><span class="live-blink">🔴</span> BEARISH SETUPS</div>
            <div class="row-header">
                <span style="width: 25%;">SYMBOL</span>
                <span style="width: 18%;">TRIGGER</span>
                <span style="width: 18%;">VOL SURGE</span>
                <span style="width: 15%;">QTY</span>
                <span style="width: 12%; text-align:right;">PRICE</span>
                <span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
    """, unsafe_allow_html=True)
    
    if bearish_signals:
        for s in bearish_signals:
            st.markdown(f"""
                <a href="{s['TVUrl']}" target="_blank" class="stock-row-item">
                    <div style="width: 25%;"><span class="sym-btn-box" style="color:#f85149;">{s['Symbol']}</span></div>
                    <div style="width: 18%; font-size:11px; color:{text_sub}; font-weight:700;">🕒 {s['SignalTime']}</div>
                    <div style="width: 18%;"><span class="vol-box">{s['VolMultiple']:.2f}x</span></div>
                    <div style="width: 15%;"><span class="qty-box">{s['Qty']}</span></div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:{text_main}; font-size:13px;" class="live-blink">₹{s['Price']:.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#f85149; font-size:12px;">▼{s['ChangePct']:.2f}%</div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:25px; font-weight:600;">Searching for Pure Pause Candle breakdowns in Hira Stocks...</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- AUTO REFRESH ---
if is_market_open:
    time.sleep(30)
    st.rerun()
