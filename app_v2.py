import streamlit as st
import pandas as pd
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fyers_apiv3 import fyersModel

st.set_page_config(page_title="C1 + C2 Inside Bar Scanner", layout="wide")

# ---------------------------------------------------------
# 1. FYERS CLIENT SETUP
# ---------------------------------------------------------
def get_fyers_client(client_id, access_token):
    try:
        fyers = fyersModel.FyersModel(
            client_id=client_id,
            token=access_token,
            is_async=False,
            log_path=""
        )
        return fyers
    except Exception as e:
        st.error(f"Fyers Client Connection Error: {e}")
        return None

# ---------------------------------------------------------
# 2. STRICT C1 + C2 INSIDE BAR SCANNER ENGINE
# ---------------------------------------------------------
def check_5min_pause_candle_setup(symbol, fyers_obj):
    if fyers_obj is None:
        return None
    try:
        # آخری 3 دنوں کا ڈیٹا مانگیں تاکہ مارکیٹ کے بعد یا چھٹی والے دن بھی آخری ٹریڈنگ سیشن کا ڈیٹا ملے
        today = datetime.date.today()
        from_date = (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        data = {
            "symbol": f"NSE:{symbol}-EQ",
            "resolution": "5",
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        
        time.sleep(0.01) # API Safety delay
        res = fyers_obj.history(data=data)
        
        if res.get("s") != "ok" or not res.get("candles"):
            return None

        # pandas DataFrame
        df_all = pd.DataFrame(res["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
        df_all['timestamp'] = pd.to_datetime(df_all['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')

        # صرف آخری ٹریڈنگ سیشن (Latest Trading Date) کا ڈیٹا فلٹر کریں
        latest_date = df_all['timestamp'].dt.date.max()
        df = df_all[df_all['timestamp'].dt.date == latest_date].copy().reset_index(drop=True)

        if len(df) < 2:
            return None

        # C1 = 09:15 AM Candle (First Candle)
        c1 = df.iloc[0]
        c1_high = float(c1['high'])
        c1_low = float(c1['low'])
        c1_close = float(c1['close'])

        if c1_low == 0:
            return None

        # Rule 1: C1 Max Range <= 1.5%
        c1_range_pct = ((c1_high - c1_low) / c1_low) * 100
        if c1_range_pct > 1.5:
            return None

        # C2 = 09:20 AM Candle (Second Candle)
        c2 = df.iloc[1]
        c2_high = float(c2['high'])
        c2_low = float(c2['low'])

        # Rule 2: Strict Inside Candle (C2 must be within C1 range)
        if not (c2_high <= c1_high and c2_low >= c1_low):
            return None

        # Buffers for Breakout (0.05%)
        buy_trigger = round(c1_high * 1.0005, 2)
        sell_trigger = round(c1_low * 0.9995, 2)

        # Check subsequent candles for Breakout or Invalidation
        current_status = "READY"
        breakout_time = None
        breakout_price = None

        for i in range(2, len(df)):
            candle = df.iloc[i]
            c_high = float(candle['high'])
            c_low = float(candle['low'])
            c_time = candle['timestamp'].strftime("%H:%M")

            # Check Buy Breakout
            if c_high >= buy_trigger:
                current_status = "BULLISH BREAKOUT"
                breakout_time = c_time
                breakout_price = round(c_high, 2)
                break
            
            # Check Sell Breakout
            elif c_low <= sell_trigger:
                current_status = "BEARISH BREAKOUT"
                breakout_time = c_time
                breakout_price = round(c_low, 2)
                break

            # Time Invalidation (After 11:00 AM discard if no breakout)
            if candle['timestamp'].hour >= 11 and current_status == "READY":
                return None

        latest_price = round(float(df.iloc[-1]['close']), 2)

        return {
            "Symbol": symbol,
            "C1 High": c1_high,
            "C1 Low": c1_low,
            "Range %": round(c1_range_pct, 2),
            "Buy Above": buy_trigger,
            "Sell Below": sell_trigger,
            "Status": current_status,
            "LTP": latest_price,
            "Trigger Time": breakout_time if breakout_time else "-",
            "Trigger Price": breakout_price if breakout_price else "-"
        }

    except Exception as e:
        return None

# ---------------------------------------------------------
# 3. STREAMLIT UI & SCANNER EXECUTION
# ---------------------------------------------------------
st.title("⚡ Pro Intraday C1 + C2 Inside Bar Scanner")

col1, col2 = st.columns(2)
with col1:
    client_id = st.text_input("Fyers Client ID", type="default")
with col2:
    access_token = st.text_input("Fyers Access Token", type="password")

if st.button("🚀 Run Scanner"):
    if not client_id or not access_token:
        st.warning("براہ کرم Client ID اور Access Token دونوں درج کریں۔")
    else:
        with st.spinner("Fyers API سے رابطہ قائم کیا جا رہا ہے..."):
            fyers = get_fyers_client(client_id, access_token)

        if fyers:
            # Watchlist
            watchlist = ["GAIL", "INOXWIND", "BAJAJFINSV", "INDHOTEL", "BAJAJHLDNG", "360ONE", "GODFRYPHLP", "GALLANTT", "MINDACORP", "DIXON"]
            
            st.info(f"اسکیننگ جاری ہے... کل اسٹاکس: {len(watchlist)}")
            
            results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(check_5min_pause_candle_setup, symbol, fyers): symbol for symbol in watchlist}
                for future in as_completed(futures):
                    res = future.result()
                    if res:
                        results.append(res)

            if results:
                df_res = pd.DataFrame(results)
                st.success(f"فلٹر کے مطابق {len(df_res)} اسٹاکس مل گئے ہیں:")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("آخری ٹریڈنگ سیشن میں C1 + C2 کا کوئی بھی پرفیکٹ سیٹ اپ نہیں ملا۔")
