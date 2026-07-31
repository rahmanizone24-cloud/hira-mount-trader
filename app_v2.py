import streamlit as st
import pandas as pd
import datetime
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from fyers_apiv3 import fyersModel

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Hira Mount Trader", layout="wide")

st.title("🎯 Hira Mount Trader - 5 Min Pause Candle Scanner")
st.caption("Live Market Automation Engine - Built for Hira Stocks Watchlist")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Settings & Authentication")

client_id = st.sidebar.text_input("Fyers Client ID", value="", type="default")
access_token = st.sidebar.text_input("Fyers Access Token", value="", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Watchlist Status")

# --- AUTOMATIC CSV FILE LOADING (No manual upload needed) ---
# اپنی فائل کا صحیح نام یہاں درج رکھیں
CSV_FILE_NAME = "hira_stocks.csv"  

@st.cache_data
def auto_load_hira_watchlist(file_path):
    """سسٹم میں موجود Hira Stocks CSV فائل کو خود بخود ریڈ کرنے کا فنکشن"""
    default_list = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN"]
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # سمبل والے کالم کو خودکار طریقے سے ڈھونڈنا
            possible_cols = [c for c in df.columns if c.lower() in ['symbol', 'ticker', 'stock', 'tradingsymbol']]
            if possible_cols:
                col = possible_cols[0]
                stocks = df[col].dropna().astype(str).str.strip().tolist()
            else:
                stocks = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
                
            # Fyers Format cleaning (NSE: اور -EQ صاف کرنا)
            cleaned_stocks = [s.replace("NSE:", "").replace("-EQ", "") for s in stocks if s]
            return cleaned_stocks, True
        except Exception as e:
            st.sidebar.error(f"Error reading {file_path}: {e}")
            return default_list, False
    else:
        return default_list, False

WATCHLIST, is_loaded = auto_load_hira_watchlist(CSV_FILE_NAME)

if is_loaded:
    st.sidebar.success(f"✅ Auto-Loaded **{len(WATCHLIST)}** Hira Stocks!")
else:
    st.sidebar.warning(f"⚠️ `{CSV_FILE_NAME}` فائل نہیں ملی! ڈیمو لسٹ استعمال ہو رہی ہے۔")

# Performance Tweaks for Rate Limit
MAX_THREADS = st.sidebar.slider("Scanner Multi-Threading Speed", min_value=5, max_value=30, value=15, help="ایک ساتھ کتنے اسٹاکس اسکین کرنے ہیں")

# --- FYERS API INITIALIZATION ---
def get_fyers_instance():
    if client_id and access_token:
        return fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
    return None

fyers = get_fyers_instance()

# --- HELPER FUNCTIONS & EMA CALCULATION ---
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def fetch_5min_data(symbol, fyers_obj):
    """5 Minute Data Fetcher from Fyers"""
    try:
        today = datetime.date.today()
        from_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        fyers_symbol = f"NSE:{symbol}-EQ"
        data = {
            "symbol": fyers_symbol,
            "resolution": "5",
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        
        response = fyers_obj.history(data=data)
        if response.get("s") == "ok":
            cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df = pd.DataFrame(response['candles'], columns=cols)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata')
            return df
    except Exception:
        pass
    return None

# --- CORE FILTRATION ENGINE (Single Stock Logic) ---
def process_single_stock(symbol, fyers_obj):
    time.sleep(0.04) # Rate limit safety buffer
    df = fetch_5min_data(symbol, fyers_obj)
    
    if df is None or len(df) < 200:
        return None

    # Calculate Indicators
    df['EMA_20'] = calculate_ema(df, 20)
    df['EMA_200'] = calculate_ema(df, 200)
    df['Vol_MA_20'] = df['volume'].rolling(window=20).mean()

    # Filter Today's Candles Only
    today_date = datetime.date.today()
    df_today = df[df['timestamp'].dt.date == today_date].copy().reset_index(drop=True)

    if len(df_today) < 3:
        return None

    # 1. Candle C1 (09:15 - 09:20)
    c1 = df_today.iloc[0]
    c1_range_pct = ((c1['high'] - c1['low']) / c1['open']) * 100
    
    c1_above_ema = (c1['close'] > c1['EMA_20']) and (c1['close'] > c1['EMA_200'])
    c1_below_ema = (c1['close'] < c1['EMA_20']) and (c1['close'] < c1['EMA_200'])

    if c1_range_pct > 1.5 or not (c1_above_ema or c1_below_ema):
        return None

    # 2. Candle C2 (09:20 - 09:25) -> Inside Candle
    c2 = df_today.iloc[1]
    is_inside_candle = (c2['high'] <= c1['high']) and (c2['low'] >= c1['low'])

    if not is_inside_candle:
        return None

    # 3. Candle C3+ Breakout Check
    for i in range(2, len(df_today)):
        curr = df_today.iloc[i]
        
        # Bullish Breakout
        if c1_above_ema and (curr['close'] > c1['high']) and (curr['volume'] > curr['Vol_MA_20']):
            return {
                "Symbol": symbol,
                "Type": "BULLISH 🟢",
                "Trigger Time": curr['timestamp'].strftime("%H:%M"),
                "Breakout Price": curr['close'],
                "C1 High": c1['high'],
                "C1 Low": c1['low'],
                "Volume Multiple": round(curr['volume'] / curr['Vol_MA_20'], 2)
            }
        
        # Bearish Breakout
        elif c1_below_ema and (curr['close'] < c1['low']) and (curr['volume'] > curr['Vol_MA_20']):
            return {
                "Symbol": symbol,
                "Type": "BEARISH 🔴",
                "Trigger Time": curr['timestamp'].strftime("%H:%M"),
                "Breakout Price": curr['close'],
                "C1 High": c1['high'],
                "C1 Low": c1['low'],
                "Volume Multiple": round(curr['volume'] / curr['Vol_MA_20'], 2)
            }

    return None

# --- MAIN CONTROLLER & MULTI-THREADING ENGINE ---
col_head, col_btn = st.columns([4, 1])

with col_head:
    st.subheader(f"Scanning {len(WATCHLIST)} Hira Stocks Automatically...")

with col_btn:
    run_scan = st.button("🚀 Run Live Scan", type="primary", use_container_width=True)

if run_scan:
    if not fyers:
        st.error("❌ Please provide Client ID and Access Token in the Sidebar.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        
        # Multi-Threading Execution
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_symbol = {executor.submit(process_single_stock, sym, fyers): sym for sym in WATCHLIST}
            
            completed = 0
            total_stocks = len(WATCHLIST)

            for future in as_completed(future_to_symbol):
                completed += 1
                symbol = future_to_symbol[future]
                
                try:
                    res = future.result()
                    if res:
                        results.append(res)
                except Exception:
                    pass

                progress_bar.progress(completed / total_stocks)
                status_text.text(f"Scanning: {completed}/{total_stocks} stocks completed...")

        progress_bar.empty()
        status_text.empty()
        elapsed = round(time.time() - start_time, 2)

        st.success(f"Scan Completed in {elapsed} seconds!")

        # --- DISPLAY RESULTS ---
        if results:
            res_df = pd.DataFrame(results)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Opportunities", len(res_df))
            c2.metric("Bullish Signals", len(res_df[res_df['Type'] == "BULLISH 🟢"]))
            c3.metric("Bearish Signals", len(res_df[res_df['Type'] == "BEARISH 🔴"]))

            st.dataframe(
                res_df,
                column_config={
                    "Breakout Price": st.column_config.NumberColumn(format="₹%.2f"),
                    "C1 High": st.column_config.NumberColumn(format="₹%.2f"),
                    "C1 Low": st.column_config.NumberColumn(format="₹%.2f"),
                    "Volume Multiple": st.column_config.NumberColumn(format="%.1fx Vol"),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("🤐 Silent Engine: No high-precision setups matched the parameters right now.")
