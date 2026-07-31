import streamlit as st
import pandas as pd
from datetime import datetime
from fyers_apiv3 import fyersModel

# --- CONFIGURATION & FYERS API SETUP ---
APP_ID = "8L18MZNAIT-200"
SECRET_ID = "7T15kjQ0xzuVGEE9"
REDIRECT_URI = "https://trade.fyers.in/api-login/default-redirect-uri/"

st.set_page_config(page_title="Fyers 5M Breakout Scanner", layout="wide")
st.title("🎯 Strict Logic 5-Min Scanner (Fyers API Integrated)")

# Sidebar for Access Token input
st.sidebar.header("🔑 Fyers Authentication")
access_token = st.sidebar.text_input("Enter Today's Access Token:", type="password")

if not access_token:
    st.info("👈 Please enter your Access Token in the sidebar to start scanning.")
    st.stop()

# Initialize Fyers Model
fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")

# --- SCANNER LOGIC ---
def analyze_stock(symbol):
    try:
        data = {
            "symbol": f"NSE:{symbol}-EQ",
            "resolution": "5",
            "date_format": "0",
            "range_from": str(int((datetime.now().timestamp() - 86400 * 3))), # Last 3 days
            "range_to": str(int(datetime.now().timestamp())),
            "cont_flag": "1"
        }
        response = fyers.history(data=data)
        
        if response.get("s") != "ok" or not response.get("candles"):
            return None
        
        df = pd.DataFrame(response['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Calculate Technical Indicators
        df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean()
        df['Vol_MA20'] = df['volume'].rolling(window=20).mean()
        
        results = []
        
        # Scan through candles (excluding recent unclosed candle)
        for i in range(2, len(df) - 1):
            c1 = df.iloc[i-2] # First Candle
            c2 = df.iloc[i-1] # Second Candle (Inside Bar)
            c3 = df.iloc[i]   # Breakout Candle
            
            # Candle 1 Range calculation (<= 1.5%)
            c1_range_pct = ((c1['high'] - c1['low']) / c1['open']) * 100
            if c1_range_pct > 1.5:
                continue
                
            # Candle 2 must be Inside Bar of Candle 1
            is_inside_bar = (c2['high'] <= c1['high']) and (c2['low'] >= c1['low'])
            if not is_inside_bar:
                continue
                
            # Candle 3 High Volume Check
            has_volume = c3['volume'] > c3['Vol_MA20']
            if not has_volume:
                continue

            # BULLISH BREAKOUT LOGIC
            if (c1['close'] > c1['EMA20']) and (c1['close'] > c1['EMA200']):
                if c3['close'] > c1['high']:
                    results.append({
                        "Symbol": symbol,
                        "Type": "🟢 BULLISH",
                        "Time": c3['datetime'].strftime('%Y-%m-%d %H:%M'),
                        "Breakout Price": c3['close'],
                        "1st Candle High": c1['high'],
                        "Volume": c3['volume']
                    })

            # BEARISH BREAKOUT LOGIC
            if (c1['close'] < c1['EMA20']) and (c1['close'] < c1['EMA200']):
                if c3['close'] < c1['low']:
                    results.append({
                        "Symbol": symbol,
                        "Type": "🔴 BEARISH",
                        "Time": c3['datetime'].strftime('%Y-%m-%d %H:%M'),
                        "Breakout Price": c3['close'],
                        "1st Candle Low": c1['low'],
                        "Volume": c3['volume']
                    })
                    
        return results
    except Exception as e:
        return None

# --- MAIN DASHBOARD ---
WATCHLIST = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE", "ALKEM", "TATAMOTORS", "AXISBANK"]

if st.button("🚀 Start Scan"):
    all_signals = []
    with st.spinner("Analyzing 5-minute candles via Fyers API..."):
        for stock in WATCHLIST:
            signals = analyze_stock(stock)
            if signals:
                all_signals.extend(signals)
                
    if all_signals:
        df_results = pd.DataFrame(all_signals)
        st.success(f"Found {len(df_results)} Valid Setups!")
        st.dataframe(df_results, use_container_width=True)
    else:
        st.warning("No stocks matching strict criteria right now.")
