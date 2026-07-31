import datetime
import os
import numpy as np
import pandas as pd
import pytz
import streamlit as st
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hira Mount Trader Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- THEME STATE MANAGEMENT ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

bg_color = "#0b0e14" if st.session_state.theme == "dark" else "#f6f8fa"
card_bg = "#161b22" if st.session_state.theme == "dark" else "#ffffff"
sub_card_bg = "#0d1117" if st.session_state.theme == "dark" else "#f3f4f6"
border_color = "#30363d" if st.session_state.theme == "dark" else "#d0d7de"
text_main = "#f0f6fc" if st.session_state.theme == "dark" else "#1f2328"
text_sub = "#8b949e" if st.session_state.theme == "dark" else "#656d76"
accent_blue = "#58a6ff" if st.session_state.theme == "dark" else "#0969da"
btn_bg = "#21262d" if st.session_state.theme == "dark" else "#eaeef2"

# --- CUSTOM CSS ---
st.markdown(
    f"""
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
        .stButton>button {{
            background-color: {btn_bg} !important; color: {accent_blue} !important; border: 1.5px solid {border_color} !important;
            border-radius: 6px !important; font-weight: 800 !important; font-size: 12px !important; padding: 4px 8px !important;
            height: 38px !important; width: 100% !important;
        }}
        .brand-logo {{
            font-size: 18px; font-weight: 900; color: {accent_blue} !important; letter-spacing: 0.5px;
            font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; white-space: nowrap; line-height: 38px;
        }}
        
        .indices-bar-wrapper {{
            display: flex; align-items: center; justify-content: flex-start; gap: 12px; width: 100%; height: 38px; overflow-x: auto;
        }}
        .idx-pill {{
            display: inline-flex; align-items: center; gap: 8px; background-color: {sub_card_bg}; border: 1.5px solid {border_color};
            border-radius: 6px; padding: 5px 12px; text-decoration: none !important; font-size: 12px; white-space: nowrap;
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 12px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 12px; }}
        
        .header-status-box {{ display: flex; align-items: center; justify-content: center; height: 38px; white-space: nowrap; }}
        .header-time-box {{ display: flex; align-items: center; justify-content: center; height: 38px; font-size: 11px; color: {text_sub}; font-weight: 800; white-space: nowrap; background-color:{card_bg}; border: 1.5px solid {border_color}; border-radius: 6px; padding: 0 10px; }}
        
        @keyframes smoothPulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
        
        .market-status-open {{
            background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1.5px solid rgba(63, 185, 80, 0.5);
            padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 900;
            animation: smoothPulse 3.5s ease-in-out infinite;
        }}
        .market-status-closed {{
            background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1.5px solid rgba(248, 81, 73, 0.5);
            padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 900;
        }}
        
        .metric-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px 14px; height: 100%; min-height: 85px; display: flex; flex-direction: column; justify-content: center; text-decoration: none !important; }}
        .card-label {{ font-size: 11px; color: {text_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-value-green {{ font-size: 18px; font-weight: 900; color: #3fb950; margin-top: 2px; }}
        .card-value-red {{ font-size: 18px; font-weight: 900; color: #f85149; margin-top: 2px; }}
        
        .box-container-center {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-top: 10px; margin-bottom: 8px; text-align: center; }}
        .box-title-center {{ font-size: 14px; font-weight: 900; color: {text_main}; letter-spacing: 0.5px; text-transform: uppercase; }}
        
        .stock-card {{ background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px; text-align: left; }}
        .stock-symbol {{ font-size: 13px; font-weight: 900; color: {accent_blue}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .stock-price-up {{ font-size: 14px; font-weight: 900; color: #3fb950; animation: smoothPulse 3.5s ease-in-out infinite; }}
        .stock-price-down {{ font-size: 14px; font-weight: 900; color: #f85149; animation: smoothPulse 3.5s ease-in-out infinite; }}
        
        .setup-box {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 10px; padding: 12px; }}
        .setup-header-bull {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .setup-header-bear {{ font-size: 15px; font-weight: 900; color: #f85149; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        
        .table-col-header-grid {{ display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1.1fr 1fr; gap: 6px; text-align: center; padding: 6px; font-size: 10px; font-weight: 900; color: {text_sub}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; background-color:{sub_card_bg}; border-radius:6px; border:1px solid {border_color}; }}

        .stock-row-grid {{ display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1.1fr 1fr; gap: 6px; margin-bottom: 8px; text-decoration: none !important; align-items: center; }}
        
        .cell-box {{ background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 6px; padding: 6px 4px; text-align: center; font-size: 12px; font-weight: 800; color: {text_main}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; justify-content: center; height: 36px; }}
        .cell-box-sym {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 6px; padding: 6px 4px; text-align: center; font-size: 13px; font-weight: 900; color: {accent_blue}; display: flex; align-items: center; justify-content: center; height: 36px; }}
        
        .cell-price-up {{ background-color: rgba(63, 185, 80, 0.12); color: #3fb950; border: 1.5px solid rgba(63, 185, 80, 0.3); border-radius: 6px; padding: 6px 4px; font-weight: 900; font-size: 12px; display: flex; align-items: center; justify-content: center; height: 36px; animation: smoothPulse 3.5s ease-in-out infinite; }}
        .cell-price-down {{ background-color: rgba(248, 81, 73, 0.12); color: #f85149; border: 1.5px solid rgba(248, 81, 73, 0.3); border-radius: 6px; padding: 6px 4px; font-weight: 900; font-size: 12px; display: flex; align-items: center; justify-content: center; height: 36px; animation: smoothPulse 3.5s ease-in-out infinite; }}
        
        .cell-pct-up {{ background-color: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 6px; padding: 6px 4px; font-weight: 900; font-size: 12px; display: flex; align-items: center; justify-content: center; height: 36px; }}
        .cell-pct-down {{ background-color: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1.5px solid rgba(251, 146, 60, 0.4); border-radius: 6px; padding: 6px 4px; font-weight: 900; font-size: 12px; display: flex; align-items: center; justify-content: center; height: 36px; }}
        
        .badge-ready-bull {{ background-color: {sub_card_bg}; color: #3fb950; border: 1.5px solid #3fb950; border-radius: 6px; padding: 4px; font-size: 11px; font-weight: 900; display: flex; align-items: center; justify-content: center; height: 36px; width: 100%; }}
        .badge-ready-bear {{ background-color: {sub_card_bg}; color: #f85149; border: 1.5px solid #f85149; border-radius: 6px; padding: 4px; font-size: 11px; font-weight: 900; display: flex; align-items: center; justify-content: center; height: 36px; width: 100%; }}
        .badge-watch {{ background-color: {sub_card_bg}; color: #d29922; border: 1.5px solid #d29922; border-radius: 6px; padding: 4px; font-size: 11px; font-weight: 900; display: flex; align-items: center; justify-content: center; height: 36px; width: 100%; }}
        
        .meta-text-box {{ font-size: 11px; color: {text_sub}; font-weight: 800; background-color:{sub_card_bg}; border:1px solid {border_color}; border-radius:4px; padding:2px 6px; display:inline-block; margin-top:4px; }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- STRICTLY LOAD STOCKS FROM HIRA STOCKS.CSV ONLY ---
@st.cache_data(ttl=86400, show_spinner=False)
def load_hira_stocks():
    csv_filename = "Hira Stocks.csv"
    if os.path.exists(csv_filename):
        try:
            df = pd.read_csv(csv_filename)
            symbols = df["symbol"].dropna().str.strip().tolist()
            ns_symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]
            if ns_symbols:
                return ns_symbols
        except Exception:
            pass
    return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

ALL_HIRA_SYMBOLS = load_hira_stocks()
TOTAL_SCANNED_STOCKS = len(ALL_HIRA_SYMBOLS)

# --- MARKET TIME DETECTOR ---
ist_tz = pytz.timezone("Asia/Kolkata")
now_dt = datetime.datetime.now(ist_tz)
market_open_time = now_dt.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_dt.replace(hour=15, minute=30, second=0, microsecond=0)
is_market_open = (now_dt.weekday() < 5) and (market_open_time <= now_dt <= market_close_time)

# --- INDICES FETCH ---
@st.cache_data(ttl=60, show_spinner=False)
def fetch_indices():
    indices = {
        "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
        "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
        "SENSEX": ("^BSESN", "BSE:SENSEX")
    }
    res = {}
    for name, (sym, tv_sym) in indices.items():
        tv_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="5d", interval="1d", timeout=5)
            if df is not None and not df.empty and len(df) >= 2:
                curr = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                change = curr - prev
                res[name] = {
                    "val": round(curr, 2),
                    "change": round(change, 2),
                    "pct": round((change / prev) * 100, 2),
                    "url": tv_url
                }
            else:
                res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
        except Exception:
            res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
    return res

def calculate_vwap(df):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    vol = df["Volume"].replace(0, 1)
    return (tp * vol).cumsum() / vol.cumsum()

def calculate_ema(df, period=20):
    return df["Close"].ewm(span=period, adjust=False).mean()

# --- BATCH DATA FETCHING ---
def fetch_batch_data(symbol_list, period="5d", interval="1d"):
    batch_size = 50
    all_dfs = []
    for i in range(0, len(symbol_list), batch_size):
        chunk = symbol_list[i:i + batch_size]
        try:
            df = yf.download(chunk, period=period, interval=interval, progress=False, group_by="ticker", threads=False, timeout=10, ignore_errors=True)
            if df is not None and not df.empty:
                all_dfs.append(df)
        except Exception:
            continue
    if all_dfs:
        return pd.concat(all_dfs, axis=1)
    return None

def safe_extract_symbol(df_bulk, symbol):
    try:
        if df_bulk is None or df_bulk.empty:
            return None
        if isinstance(df_bulk.columns, pd.MultiIndex):
            if symbol in df_bulk.columns.levels[0]:
                return df_bulk[symbol].dropna(how="all")
            elif symbol in df_bulk.columns.levels[1]:
                return df_bulk.xs(symbol, axis=1, level=1).dropna(how="all")
        elif symbol in df_bulk.columns:
            return df_bulk[[symbol]].dropna()
        return df_bulk.dropna(how="all")
    except Exception:
        return None

# --- ACCURATE SCANNER (FIXED EXACT TRIGGER TIME PER CANDLE) ---
@st.cache_data(ttl=60, show_spinner=False)
def run_market_scanner():
    bullish_list, bearish_list, all_scanned_stocks = [], [], []
    per_trade_cap = 10000

    bulk_1d = fetch_batch_data(ALL_HIRA_SYMBOLS, period="5d", interval="1d")
    bulk_5m = fetch_batch_data(ALL_HIRA_SYMBOLS, period="5d", interval="5m")

    for symbol in ALL_HIRA_SYMBOLS:
        try:
            clean_symbol = symbol.replace(".NS", "").upper()
            df_daily = safe_extract_symbol(bulk_1d, symbol) if bulk_1d is not None else None

            if df_daily is None or df_daily.empty or len(df_daily) < 2:
                try:
                    t = yf.Ticker(symbol)
                    df_daily = t.history(period="5d", interval="1d")
                except Exception:
                    continue

            if df_daily is None or len(df_daily) < 2:
                continue

            curr_price = float(df_daily["Close"].iloc[-1])
            prev_close = float(df_daily["Close"].iloc[-2])

            if curr_price <= 0 or prev_close <= 0:
                continue

            day_change_pct = float(((curr_price - prev_close) / prev_close) * 100)
            change_pts = float(curr_price - prev_close)
            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
            calc_qty = max(1, int((per_trade_cap * 5) / curr_price))

            df_5m_raw = safe_extract_symbol(bulk_5m, symbol) if bulk_5m is not None else None
            status_state = None
            is_bullish = False
            is_bearish = False
            trigger_time = None

            # Helper function: Convert timestamp of candle index directly to IST formatted string
            def format_candle_time(ts):
                try:
                    if hasattr(ts, 'tzinfo') and ts.tzinfo is None:
                        ts = pytz.utc.localize(ts)
                    ist_dt = ts.astimezone(ist_tz)
                    return ist_dt.strftime("%I:%M %p")
                except Exception:
                    return ts.strftime("%I:%M %p")

            if df_5m_raw is not None and not df_5m_raw.empty:
                latest_date = df_5m_raw.index[-1].date()
                today_df = df_5m_raw[df_5m_raw.index.date == latest_date].copy()

                if len(today_df) >= 2:
                    today_df["VWAP"] = calculate_vwap(today_df)
                    today_df["EMA20"] = calculate_ema(today_df, 20)

                    c1 = today_df.iloc[0]
                    c1_high, c1_low = float(c1["High"]), float(c1["Low"])
                    c1_open, c1_close = float(c1["Open"]), float(c1["Close"])
                    c1_ema20 = float(c1["EMA20"])

                    c1_range_pct = ((c1_high - c1_low) / c1_low) * 100

                    # Primary Setup Evaluation
                    if c1_range_pct <= 1.2 and abs(((c1_open - prev_close) / prev_close) * 100) <= 1.5:
                        c2 = today_df.iloc[1]
                        c2_high, c2_low = float(c2["High"]), float(c2["Low"])
                        c2_open, c2_close = float(c2["Open"]), float(c2["Close"])

                        if c1_close > c1_ema20:
                            if (c2_close <= c2_open) and (c2_high <= c1_high * 1.003) and (c2_low >= c1_low * 0.997):
                                status_state = "WATCH"
                                is_bullish = True
                                trigger_time = format_candle_time(today_df.index[1])
                                for idx in range(2, len(today_df)):
                                    ck = today_df.iloc[idx]
                                    if float(ck["Close"]) > max(c1_high, c2_high):
                                        status_state = "READY"
                                        trigger_time = format_candle_time(today_df.index[idx])
                                        break

                        elif c1_close < c1_ema20:
                            if (c2_close >= c2_open) and (c2_low >= c1_low * 0.997) and (c2_high <= c1_high * 0.997):
                                status_state = "WATCH"
                                is_bearish = True
                                trigger_time = format_candle_time(today_df.index[1])
                                for idx in range(2, len(today_df)):
                                    ck = today_df.iloc[idx]
                                    if float(ck["Close"]) < min(c1_low, c2_low):
                                        status_state = "READY"
                                        trigger_time = format_candle_time(today_df.index[idx])
                                        break

                    # Fallback evaluation: Find exact 5-min candle timestamp where stock hit +2% / -2% threshold
                    if not status_state:
                        if day_change_pct >= 2.0:
                            status_state = "READY"
                            is_bullish = True
                            for idx in range(len(today_df)):
                                c_pct = ((float(today_df.iloc[idx]["Close"]) - prev_close) / prev_close) * 100
                                if c_pct >= 2.0:
                                    trigger_time = format_candle_time(today_df.index[idx])
                                    break
                            if not trigger_time:
                                trigger_time = format_candle_time(today_df.index[0])

                        elif day_change_pct <= -2.0:
                            status_state = "READY"
                            is_bearish = True
                            for idx in range(len(today_df)):
                                c_pct = ((float(today_df.iloc[idx]["Close"]) - prev_close) / prev_close) * 100
                                if c_pct <= -2.0:
                                    trigger_time = format_candle_time(today_df.index[idx])
                                    break
                            if not trigger_time:
                                trigger_time = format_candle_time(today_df.index[0])

            # Ensure time is extracted strictly from candle data if available
            if not trigger_time:
                if df_5m_raw is not None and not df_5m_raw.empty:
                    trigger_time = format_candle_time(df_5m_raw.index[0])
                else:
                    trigger_time = "09:15 AM"

            base_info = {
                "Symbol": str(clean_symbol),
                "Price": float(curr_price),
                "ChangePct": float(day_change_pct),
                "ChangePts": float(round(change_pts, 2)),
                "SignalTime": trigger_time,
                "TVUrl": str(tv_url),
                "Qty": int(calc_qty),
                "StatusState": status_state,
                "IsBullish": is_bullish,
                "IsBearish": is_bearish,
            }

            all_scanned_stocks.append(base_info)

            if status_state:
                if is_bullish: bullish_list.append(base_info)
                if is_bearish: bearish_list.append(base_info)

        except Exception:
            continue

    bullish_sorted = sorted(bullish_list, key=lambda x: (x["StatusState"] == "READY", x["ChangePct"]), reverse=True)
    bearish_sorted = sorted(bearish_list, key=lambda x: (x["StatusState"] == "READY", -x["ChangePct"]), reverse=True)

    all_scanned_df = pd.DataFrame(all_scanned_stocks)
    top_gainer, top_loser, market_movers = None, None, []

    if not all_scanned_df.empty:
        try:
            top_gainer = all_scanned_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict()
            top_loser = all_scanned_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict()

            bull_movers = all_scanned_df[all_scanned_df["ChangePct"] > 0].sort_values(by="ChangePct", ascending=False).head(4).to_dict("records")
            bear_movers = all_scanned_df[all_scanned_df["ChangePct"] < 0].sort_values(by="ChangePct", ascending=True).head(4).to_dict("records")

            market_movers = bull_movers + bear_movers
        except Exception:
            pass

    return bullish_sorted, bearish_sorted, top_gainer, top_loser, market_movers, len(bullish_sorted), len(bearish_sorted)

# --- LINE 1: TOP HEADER ---
top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b | %I:%M %p")
status_html = '<span class="market-status-open">🟢 OPEN</span>' if is_market_open else '<span class="market-status-closed">🔴 CLOSED</span>'

l1_c1, l1_c2, l1_c3, l1_c4, l1_c5, l1_c6 = st.columns([0.18, 0.44, 0.08, 0.12, 0.09, 0.09])

with l1_c1:
    st.markdown('<div class="brand-logo">HIRA MOUNT TRADER</div>', unsafe_allow_html=True)

with l1_c2:
    idx_html = '<div class="indices-bar-wrapper">'
    for name, data in top_idx.items():
        cls = "idx-up-p" if data.get("pct", 0) >= 0 else "idx-down-p"
        idx_html += f'<a class="idx-pill" href="{data.get("url", "#")}" target="_blank"><span class="idx-lbl">{name}:</span> <span class="idx-num">{data.get("val", 0):,.2f}</span> <span class="{cls}">{data.get("pct", 0):+.2f}%</span></a>'
    idx_html += '</div>'
    st.markdown(idx_html, unsafe_allow_html=True)

with l1_c3:
    st.markdown(f'<div class="header-status-box">{status_html}</div>', unsafe_allow_html=True)

with l1_c4:
    st.markdown(f'<div class="header-time-box">🕒 {now_time}</div>', unsafe_allow_html=True)

with l1_c5:
    theme_label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

with l1_c6:
    if st.button("🔄 Refresh", key="refresh_btn"):
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<hr style='margin-top: 4px; margin-bottom: 10px; border-color: {border_color}; opacity: 0.4;'>", unsafe_allow_html=True)

# --- RUN SCANNER ---
bullish_signals, bearish_signals, top_gainer, top_loser, market_movers, total_bull_cnt, total_bear_cnt = run_market_scanner()

# --- LINE 2: METRICS CARDS ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    if top_gainer:
        st.markdown(f"""
            <a href="{top_gainer.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                <div class="metric-container">
                    <div class="card-label">TOP GAINER ↗</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size: 16px; font-weight: 900; color: {accent_blue};">{top_gainer.get('Symbol', '-')}</span>
                        <span class="card-value-green">+{top_gainer.get('ChangePct', 0):.2f}%</span>
                    </div>
                    <div style="margin-top:4px;">
                        <span class="meta-text-box">🕒 {top_gainer.get('SignalTime', '-')}</span>
                        <span class="meta-text-box">Qty: {top_gainer.get('Qty', 0)}</span>
                    </div>
                </div>
            </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-container"><div class="card-label">TOP GAINER</div><div style="color:{text_sub};">Scanning...</div></div>', unsafe_allow_html=True)

with c2:
    if top_loser:
        st.markdown(f"""
            <a href="{top_loser.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                <div class="metric-container">
                    <div class="card-label">TOP LOSER ↘</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size: 16px; font-weight: 900; color: {accent_blue};">{top_loser.get('Symbol', '-')}</span>
                        <span class="card-value-red">{top_loser.get('ChangePct', 0):.2f}%</span>
                    </div>
                    <div style="margin-top:4px;">
                        <span class="meta-text-box">🕒 {top_loser.get('SignalTime', '-')}</span>
                        <span class="meta-text-box">Qty: {top_loser.get('Qty', 0)}</span>
                    </div>
                </div>
            </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-container"><div class="card-label">TOP LOSER</div><div style="color:{text_sub};">Scanning...</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 16px; font-weight: 900; color: {'#3fb950' if total_bull_cnt >= total_bear_cnt else '#f85149'}; animation: smoothPulse 3.5s ease-in-out infinite;">
                {'BULLISH 🟢' if total_bull_cnt >= total_bear_cnt else 'BEARISH 🔴'}
            </div>
            <div style="margin-top:2px;">
                <span class="meta-text-box">Bullish: {total_bull_cnt}</span>
                <span class="meta-text-box">Bearish: {total_bear_cnt}</span>
            </div>
        </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">SCANNED STOCKS</div>
            <div style="font-size: 16px; font-weight: 900; color: {accent_blue};">{TOTAL_SCANNED_STOCKS} Stocks</div>
            <div style="margin-top:2px;">
                <span class="meta-text-box" style="color:#3fb950;">Active Trading Setups: {total_bull_cnt + total_bear_cnt}</span>
            </div>
        </div>""", unsafe_allow_html=True)

# --- LINE 3: MARKET MOVERS ---
st.markdown("""<div class="box-container-center"><div class="box-title-center">🔥 MARKET MOVERS</div></div>""", unsafe_allow_html=True)

if market_movers:
    m_cols = st.columns(len(market_movers))
    for idx, m in enumerate(market_movers):
        with m_cols[idx]:
            p_cls = "stock-price-up" if m.get("ChangePct", 0) >= 0 else "stock-price-down"
            st.markdown(f"""
                <a href="{m.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-symbol">{m.get('Symbol', '-')}</div>
                        <div class="{p_cls}">₹{m.get('Price', 0):.2f} ({m.get('ChangePct', 0):+.2f}%)</div>
                        <div class="meta-text-box">🕒 {m.get('SignalTime', '-')} | Qty: {m.get('Qty', 0)}</div>
                    </div>
                </a>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- LINE 4: BULLISH & BEARISH TABLES ---
tb_col1, tb_col2 = st.columns(2)

with tb_col1:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bull">🟢 BULLISH SETUPS</div>
            <div class="table-col-header-grid">
                <span>SYMBOL</span>
                <span>STATUS</span>
                <span>TIME</span>
                <span>QTY</span>
                <span>PRICE</span>
                <span>CHANGE %</span>
            </div>
        </div>""", unsafe_allow_html=True)
    top_5_bull = bullish_signals[:5]
    if top_5_bull:
        for s in top_5_bull:
            badge_class = "badge-ready-bull" if s.get("StatusState") == "READY" else "badge-watch"
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-grid">
                    <div class="cell-box-sym">{s.get('Symbol')}</div>
                    <div class="{badge_class}">{s.get("StatusState")}</div>
                    <div class="cell-box">🕒 {s.get('SignalTime')}</div>
                    <div class="cell-box">Qty: {s.get('Qty')}</div>
                    <div class="cell-price-up">₹{s.get('Price', 0):.2f}</div>
                    <div class="cell-pct-up">▲{s.get('ChangePct', 0):.2f}%</div>
                </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:15px;">No active bullish setups right now.</div>', unsafe_allow_html=True)

with tb_col2:
    st.markdown("""
        <div class="setup-box">
            <div class="setup-header-bear">🔴 BEARISH SETUPS</div>
            <div class="table-col-header-grid">
                <span>SYMBOL</span>
                <span>STATUS</span>
                <span>TIME</span>
                <span>QTY</span>
                <span>PRICE</span>
                <span>CHANGE %</span>
            </div>
        </div>""", unsafe_allow_html=True)
    top_5_bear = bearish_signals[:5]
    if top_5_bear:
        for s in top_5_bear:
            badge_class = "badge-ready-bear" if s.get("StatusState") == "READY" else "badge-watch"
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-grid">
                    <div class="cell-box-sym" style="color:#f85149;">{s.get('Symbol')}</div>
                    <div class="{badge_class}">{s.get("StatusState")}</div>
                    <div class="cell-box">🕒 {s.get('SignalTime')}</div>
                    <div class="cell-box">Qty: {s.get('Qty')}</div>
                    <div class="cell-price-down">₹{s.get('Price', 0):.2f}</div>
                    <div class="cell-pct-down">▼{s.get('ChangePct', 0):.2f}%</div>
                </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:15px;">No active bearish setups right now.</div>', unsafe_allow_html=True)
