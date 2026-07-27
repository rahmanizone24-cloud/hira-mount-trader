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
            display: flex; align-items: center; justify-content: flex-start; gap: 6px; width: 100%; height: 38px; overflow-x: auto;
        }}
        .idx-pill {{
            display: inline-flex; align-items: center; gap: 6px; background-color: {sub_card_bg}; border: 1.5px solid {border_color};
            border-radius: 6px; padding: 4px 10px; text-decoration: none !important; font-size: 12px; white-space: nowrap;
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 12px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 12px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 12px; }}
        .header-status-box {{ display: flex; align-items: center; justify-content: center; height: 38px; white-space: nowrap; }}
        .header-time-box {{ display: flex; align-items: center; justify-content: center; height: 38px; font-size: 11px; color: {text_sub}; font-weight: 800; white-space: nowrap; }}
        .market-status-open {{ background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1.5px solid rgba(63, 185, 80, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 900; }}
        .market-status-closed {{ background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1.5px solid rgba(248, 81, 73, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 900; }}
        
        /* METRIC CARDS */
        .metric-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px 12px; height: 100%; min-height: 82px; display: flex; flex-direction: column; justify-content: center; text-decoration: none !important; }}
        .card-label {{ font-size: 11px; color: {text_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-value-green {{ font-size: 18px; font-weight: 900; color: #3fb950; margin-top: 2px; }}
        .card-value-red {{ font-size: 18px; font-weight: 900; color: #f85149; margin-top: 2px; }}
        
        .box-container-center {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-top: 10px; margin-bottom: 8px; text-align: center; }}
        .box-title-center {{ font-size: 14px; font-weight: 900; color: {text_main}; letter-spacing: 0.5px; text-transform: uppercase; }}
        
        .stock-card {{ background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px; text-align: left; }}
        .stock-symbol {{ font-size: 13px; font-weight: 900; color: {accent_blue}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .stock-price-up {{ font-size: 14px; font-weight: 900; color: #3fb950; }}
        .stock-price-down {{ font-size: 14px; font-weight: 900; color: #f85149; }}
        
        .setup-box {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 10px; padding: 12px; }}
        .setup-header-bull {{ font-size: 15px; font-weight: 900; color: #3fb950; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .setup-header-bear {{ font-size: 15px; font-weight: 900; color: #f85149; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        
        /* SEPARATE BOX LAYOUT FOR STOCKS LIST */
        .stock-row-item {{ display: flex; justify-content: space-between; align-items: center; background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px; text-decoration: none !important; }}
        .sym-btn-box {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 6px; padding: 4px 8px; color: {accent_blue}; font-weight: 900; font-size: 13px; display: inline-block; }}
        .price-box-up {{ background-color: rgba(63, 185, 80, 0.12); color: #3fb950; border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 6px; padding: 4px 8px; font-weight: 900; font-size: 13px; display: inline-block; }}
        .price-box-down {{ background-color: rgba(248, 81, 73, 0.12); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.3); border-radius: 6px; padding: 4px 8px; font-weight: 900; font-size: 13px; display: inline-block; }}
        .qty-box {{ background-color: rgba(88, 166, 255, 0.12); color: {accent_blue}; border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 6px; padding: 3px 7px; font-weight: 800; font-size: 11px; display: inline-block; }}
        .time-box {{ background-color: {card_bg}; color: {text_sub}; border: 1px solid {border_color}; border-radius: 6px; padding: 3px 7px; font-weight: 800; font-size: 11px; display: inline-block; }}
        .badge-ready {{ background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; border-radius: 5px; padding: 3px 7px; font-size: 10px; font-weight: 900; display: inline-block; }}
        .badge-watch {{ background-color: rgba(210, 153, 34, 0.2); color: #d29922; border: 1px solid #d29922; border-radius: 5px; padding: 3px 7px; font-size: 10px; font-weight: 900; display: inline-block; }}
        .meta-text {{ font-size: 11px; color: {text_sub}; font-weight: 700; }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- LOAD STOCKS FROM HIRA STOCKS.CSV ---
@st.cache_data(ttl=86400, show_spinner=False)
def load_hira_stocks():
    csv_filename = "Hira Stocks.csv"
    if os.path.exists(csv_filename):
        try:
            df = pd.read_csv(csv_filename)
            symbols = df["symbol"].dropna().str.strip().tolist()
            ns_symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]
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

# --- SAFE DATAFRAME EXTRACTOR ---
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

@st.cache_data(ttl=30, show_spinner=False)
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
            df = yf.download(sym, period="5d", interval="1d", progress=False)
            if df is not None and not df.empty and len(df) >= 2:
                curr = float(df["Close"].dropna().iloc[-1])
                prev = float(df["Close"].dropna().iloc[-2])
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

@st.cache_data(ttl=30, show_spinner=False)
def run_market_scanner():
    bullish_list, bearish_list, all_stocks = [], [], []
    per_trade_cap = 10000

    try:
        bulk_5m = yf.download(ALL_HIRA_SYMBOLS, period="2d", interval="5m", progress=False, group_by="ticker")
        bulk_1d = yf.download(ALL_HIRA_SYMBOLS, period="5d", interval="1d", progress=False, group_by="ticker")
    except Exception:
        return [], [], None, None, 0, 0

    for symbol in ALL_HIRA_SYMBOLS:
        try:
            clean_symbol = symbol.replace(".NS", "").upper()
            df_5m = safe_extract_symbol(bulk_5m, symbol)
            df_daily = safe_extract_symbol(bulk_1d, symbol)

            if df_5m is None or df_daily is None or len(df_5m) < 5 or len(df_daily) < 2:
                continue

            df_5m["VWAP"] = calculate_vwap(df_5m)
            latest_trading_date = df_5m.index[-1].date()
            today_df = df_5m[df_5m.index.date == latest_trading_date].copy()

            if len(today_df) < 2:
                continue

            curr_price = float(today_df["Close"].iloc[-1])
            prev_close = float(df_daily["Close"].iloc[-2])

            if curr_price <= 0 or prev_close <= 0:
                continue

            day_change_pct = float(((curr_price - prev_close) / prev_close) * 100)
            change_pts = float(curr_price - prev_close)
            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
            
            # Intraday Qty on ₹10,000 Capital (with 5x leverage)
            calc_qty = max(1, int((per_trade_cap * 5) / curr_price))

            c1 = today_df.iloc[0]
            c1_high, c1_low = float(c1["High"]), float(c1["Low"])
            
            signal_bullish = curr_price > c1_high
            signal_bearish = curr_price < c1_low
            trigger_time = str(today_df.index[-1].strftime("%I:%M %p"))

            res = {
                "Symbol": str(clean_symbol),
                "Price": float(curr_price),
                "ChangePct": float(day_change_pct),
                "ChangePts": float(round(change_pts, 2)),
                "SignalTime": trigger_time,
                "IsBullish": signal_bullish,
                "IsBearish": signal_bearish,
                "StatusState": "READY" if abs(day_change_pct) >= 1.5 else "WATCH",
                "TVUrl": str(tv_url),
                "Qty": int(calc_qty),
            }
            all_stocks.append(res)
            if signal_bullish: bullish_list.append(res)
            if signal_bearish: bearish_list.append(res)
        except Exception:
            continue

    all_df = pd.DataFrame(all_stocks)
    top_gainer, top_loser = None, None

    if not all_df.empty:
        try:
            top_gainer = all_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict()
            top_loser = all_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict()
        except Exception:
            pass

    bullish_sorted = sorted(bullish_list, key=lambda x: x["ChangePct"], reverse=True)
    bearish_sorted = sorted(bearish_list, key=lambda x: x["ChangePct"])

    return bullish_sorted, bearish_sorted, top_gainer, top_loser, len(bullish_sorted), len(bearish_sorted)

# --- LINE 1: TOP HEADER ---
top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b | %I:%M %p")
status_html = '<span class="market-status-open">🟢 OPEN</span>' if is_market_open else '<span class="market-status-closed">🔴 CLOSED</span>'

l1_c1, l1_c2, l1_c3, l1_c4, l1_c5, l1_c6 = st.columns([0.18, 0.40, 0.08, 0.12, 0.11, 0.11])

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
bullish_signals, bearish_signals, top_gainer, top_loser, total_bull_cnt, total_bear_cnt = run_market_scanner()

# --- LINE 2: METRICS CARDS (Top Gainer & Top Loser with TradingView Redirect) ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    if top_gainer:
        st.markdown(f"""
            <a href="{top_gainer.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                <div class="metric-container">
                    <div class="card-label">TOP GAINER ↗</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size: 15px; font-weight: 900; color: {accent_blue};">{top_gainer.get('Symbol', '-')}</span>
                        <span class="card-value-green">+{top_gainer.get('ChangePct', 0):.2f}%</span>
                    </div>
                    <div class="meta-text" style="margin-top:3px;">🕒 {top_gainer.get('SignalTime', '-')} | Qty (₹10k): {top_gainer.get('Qty', 0)}</div>
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
                        <span style="font-size: 15px; font-weight: 900; color: {accent_blue};">{top_loser.get('Symbol', '-')}</span>
                        <span class="card-value-red">{top_loser.get('ChangePct', 0):.2f}%</span>
                    </div>
                    <div class="meta-text" style="margin-top:3px;">🕒 {top_loser.get('SignalTime', '-')} | Qty (₹10k): {top_loser.get('Qty', 0)}</div>
                </div>
            </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-container"><div class="card-label">TOP LOSER</div><div style="color:{text_sub};">Scanning...</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 16px; font-weight: 900; color: {'#3fb950' if total_bull_cnt >= total_bear_cnt else '#f85149'};">
                {'BULLISH 🟢' if total_bull_cnt >= total_bear_cnt else 'BEARISH 🔴'}
            </div>
            <div class="meta-text" style="margin-top:3px;">Bullish: {total_bull_cnt} | Bearish: {total_bear_cnt}</div>
        </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-container">
            <div class="card-label">SCANNED STOCKS</div>
            <div style="font-size: 16px; font-weight: 900; color: {accent_blue};">{TOTAL_SCANNED_STOCKS} Stocks</div>
            <div class="meta-text" style="color:#3fb950; margin-top:3px;">Active Trading Setups: {total_bull_cnt + total_bear_cnt}</div>
        </div>""", unsafe_allow_html=True)

# --- LINE 3: MARKET MOVERS ---
st.markdown("""<div class="box-container-center"><div class="box-title-center">🔥 MARKET MOVERS</div></div>""", unsafe_allow_html=True)

top_4_bull = bullish_signals[:4]
top_4_bear = bearish_signals[:4]
combined_movers = top_4_bull + top_4_bear

if combined_movers:
    m_cols = st.columns(len(combined_movers))
    for idx, m in enumerate(combined_movers):
        with m_cols[idx]:
            p_cls = "stock-price-up" if m.get("ChangePct", 0) >= 0 else "stock-price-down"
            st.markdown(f"""
                <a href="{m.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-symbol">{m.get('Symbol', '-')}</div>
                        <div class="{p_cls}">₹{m.get('Price', 0):.2f} ({m.get('ChangePct', 0):+.2f}%)</div>
                        <div class="meta-text" style="margin-top:4px;">🕒 {m.get('SignalTime', '-')} | Qty: {m.get('Qty', 0)}</div>
                    </div>
                </a>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- LINE 4: BULLISH & BEARISH TABLES (With Separated Element Boxes) ---
tb_col1, tb_col2 = st.columns(2)

with tb_col1:
    st.markdown("""<div class="setup-box"><div class="setup-header-bull">🟢 BULLISH SETUPS</div></div>""", unsafe_allow_html=True)
    top_5_bull = bullish_signals[:5]
    if top_5_bull:
        for s in top_5_bull:
            badge_class = "badge-ready" if s.get("StatusState") == "READY" else "badge-watch"
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="sym-btn-box">{s.get('Symbol')}</span>
                        <span class="{badge_class}">{s.get('StatusState')}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="time-box">🕒 {s.get('SignalTime')}</span>
                        <span class="qty-box">Qty: {s.get('Qty')}</span>
                        <span class="price-box-up">₹{s.get('Price', 0):.2f} (▲{s.get('ChangePct', 0):.2f}%)</span>
                    </div>
                </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:15px;">No active bullish setups right now.</div>', unsafe_allow_html=True)

with tb_col2:
    st.markdown("""<div class="setup-box"><div class="setup-header-bear">🔴 BEARISH SETUPS</div></div>""", unsafe_allow_html=True)
    top_5_bear = bearish_signals[:5]
    if top_5_bear:
        for s in top_5_bear:
            badge_class = "badge-ready" if s.get("StatusState") == "READY" else "badge-watch"
            st.markdown(f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="sym-btn-box" style="color:#f85149;">{s.get('Symbol')}</span>
                        <span class="{badge_class}">{s.get('StatusState')}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="time-box">🕒 {s.get('SignalTime')}</span>
                        <span class="qty-box">Qty: {s.get('Qty')}</span>
                        <span class="price-box-down">₹{s.get('Price', 0):.2f} (▼{s.get('ChangePct', 0):.2f}%)</span>
                    </div>
                </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center; color:{text_sub}; padding:15px;">No active bearish setups right now.</div>', unsafe_allow_html=True)
