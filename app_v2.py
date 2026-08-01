import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Tuple

import pandas as pd
import pytz
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HiraMountTrader")

from fyers_apiv3 import fyersModel

session = fyersModel.SessionModel(client_id=st.secrets["FYERS_CLIENT_ID"], secret_key="7T15kjQ0xzuVGEE9", grant_type="authorization_code", response_type="code")
session.set_token(st.secrets["FYERS_ACCESS_TOKEN"])
response = session.generate_token()
fyers = fyersModel.FyersModel(client_id=st.secrets["FYERS_CLIENT_ID"], is_async=False, token=response.get("access_token"), log_path="")

st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed", page_icon="📈")
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_refresh")
except ImportError:
    pass

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

def toggle_theme():
    st.session_state["theme_mode"] = "Light" if st.session_state["theme_mode"] == "Dark" else "Dark"

if st.session_state["theme_mode"] == "Dark":
    bg_app, bg_card, border_clr, txt_main, txt_muted, badge_bg, btn_bg, btn_txt = (
        "#06090e", "#0f172a", "#1e293b", "#f8fafc", "#94a3b8", "#1e293b", "#1e293b", "#f8fafc"
    )
else:
    bg_app, bg_card, border_clr, txt_main, txt_muted, badge_bg, btn_bg, btn_txt = (
        "#f1f5f9", "#ffffff", "#cbd5e1", "#0f172a", "#64748b", "#e2e8f0", "#e2e8f0", "#0f172a"
    )

st.markdown(f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .main .block-container {{ max-width: 100% !important; padding: 0.6rem 0.8rem 0.4rem 0.8rem !important; }}
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    [data-testid="column"] {{ padding: 0 4px !important; }}
    div.stButton > button {{
        background-color: {btn_bg} !important; color: {btn_txt} !important;
        border: 1px solid {border_clr} !important; border-radius: 6px !important; font-weight: 700 !important;
    }}
    .top-bar-container {{
        background-color: {bg_card}; padding: 8px 14px; border-radius: 10px;
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid {border_clr}; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;
    }}
    .brand-title {{ font-size: 18px; font-weight: 900; color: #00e5ff; }}
    .index-badge {{
        background: {badge_bg}; color: #38bdf8; padding: 4px 9px; border-radius: 6px;
        font-size: 11px; border: 1px solid {border_clr}; font-weight: 800; text-decoration: none;
    }}
    .idx-bull {{ color: #00ff87 !important; border-color: #065f46 !important; background: #022c22 !important; }}
    .idx-bear {{ color: #f43f5e !important; border-color: #9f1239 !important; background: #4c0519 !important; }}
    @keyframes dotGlow {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.35; }} 100% {{ opacity: 1; }} }}
    .dot-green {{ display: inline-block; width: 8px; height: 8px; background: #00ff87; border-radius: 50%; animation: dotGlow 2.2s infinite; margin-right: 5px; }}
    .dot-red {{ display: inline-block; width: 8px; height: 8px; background: #f43f5e; border-radius: 50%; animation: dotGlow 2.2s infinite; margin-right: 5px; }}
    .stat-box {{ background: {bg_card}; border: 1px solid {border_clr}; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; }}
    .stat-title {{ font-size: 10px; color: {txt_muted}; font-weight: 700; }}
    .mover-box {{ background: {bg_card}; border: 1px solid {border_clr}; border-radius: 8px; padding: 7px 6px; text-align: center; }}
    .stock-title-link {{ font-size: 14px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .setup-card {{ background-color: {bg_card}; border: 1px solid {border_clr}; border-radius: 8px; padding: 7px 10px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between; }}
    .qty-badge {{ background-color: {badge_bg}; border: 1px solid {border_clr}; padding: 2px 7px; border-radius: 5px; font-size: 11px; font-weight: 700; color: #00e5ff; }}
    .tag-ready-bull {{ background-color: #00ff87 !important; color: #022c22 !important; padding: 3px 8px; border-radius: 5px; font-size: 10px; font-weight: 900; }}
    .tag-ready-bear {{ background-color: #f43f5e !important; color: #ffffff !important; padding: 3px 8px; border-radius: 5px; font-size: 10px; font-weight: 900; }}
    #MainMenu, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

CLIENT_ID = st.secrets.get("FYERS_CLIENT_ID", "")
ACCESS_TOKEN = st.secrets.get("FYERS_ACCESS_TOKEN", "")

@st.cache_resource
def get_fyers():
    if not fyersModel or not CLIENT_ID or not ACCESS_TOKEN:
        return None
    try:
        return fyersModel.FyersModel(client_id=CLIENT_ID, token=ACCESS_TOKEN, is_async=False, log_path="")
    except Exception:
        return None

fyers = get_fyers()

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(ist)
is_weekday = now_ist.weekday() < 5
is_market_open = is_weekday and datetime.time(9, 15) <= now_ist.time() <= datetime.time(15, 30)

market_status_html = (
    '<span style="background:#064e3b;color:#34d399;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold;"><span class="dot-green"></span>OPEN</span>'
    if is_market_open else
    '<span style="background:#881337;color:#fecdd3;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold;"><span class="dot-red"></span>CLOSED</span>'
)
time_str = now_ist.strftime("%d %b | %I:%M %p")

def get_target_date(current: datetime.datetime) -> datetime.date:
    d = current.date()
    if current.weekday() < 5:
        return d
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d

TARGET_DATE = get_target_date(now_ist)

@st.cache_data(ttl=86400)
def get_symbol_universe() -> List[str]:
    try:
        url = "https://public.fyers.in/sym_details/NSE_CM.csv"
        df = pd.read_csv(url, header=None)
        symbols = df[df[9].astype(str).str.endswith("-EQ", na=False)][9].dropna().unique().tolist()
        return symbols[:500]
    except Exception:
        return ["NSE:RELIANCE-EQ", "NSE:TCS-EQ", "NSE:HDFCBANK-EQ", "NSE:ICICIBANK-EQ", "NSE:INFY-EQ"]

SYMBOL_UNIVERSE = get_symbol_universe()

@st.cache_data(ttl=20)
def get_live_indices():
    default = {"nifty": 0.0, "bank": 0.0, "sensex": 0.0}
    if not fyers:
        return default
    try:
        resp = fyers.quotes(data={"symbols": "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX,BSE:SENSEX-INDEX"})
        if resp.get("s") != "ok":
            return default
        result = default.copy()
        for item in resp.get("d", []):
            n = item.get("n", "")
            chp = float(item.get("v", {}).get("chp", 0) or 0)
            if "NIFTY50" in n:
                result["nifty"] = chp
            elif "NIFTYBANK" in n or "BANKNIFTY" in n:
                result["bank"] = chp
            elif "SENSEX" in n:
                result["sensex"] = chp
        return result
    except Exception:
        return default

indices = get_live_indices()

def make_index_badge(name, change, symbol):
    cls = "idx-bull" if change >= 0 else "idx-bear"
    sign = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
    arrow = "▲" if change >= 0 else "▼"
    return f'<a href="https://in.tradingview.com/chart/?symbol={symbol}" target="_blank" class="index-badge {cls}">{name} {arrow} {sign}</a>'

nifty_html = make_index_badge("NIFTY 50", indices["nifty"], "NSE:NIFTY")
bank_html = make_index_badge("BANK NIFTY", indices["bank"], "NSE:BANKNIFTY")
sensex_html = make_index_badge("SENSEX", indices["sensex"], "BSE:SENSEX")

col1, col2, col3 = st.columns([10, 1, 1])
with col1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        {nifty_html} {bank_html} {sensex_html} {market_status_html}
        <span class="index-badge" style="color:#00e5ff;">🕒 {time_str}</span>
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("☀️ Light" if st.session_state["theme_mode"] == "Dark" else "🌙 Dark", use_container_width=True):
        toggle_theme()
        st.rerun()
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

def calculate_qty(price: float) -> int:
    return max(1, int(50000 / price)) if price > 0 else 1

def scan_single_stock(symbol: str) -> Tuple[Optional[Dict], dict]:
    local_stats = {
        "scanned": 1, "data_rcvd": 0, "pass_range": 0,
        "pass_2nd": 0, "pass_bias": 0, "reached_breakout": 0, "final": 0
    }
    
    if not fyers:
        return None, local_stats

    clean_sym = symbol.replace("NSE:", "").replace("-EQ", "")
    tv_url = f"https://in.tradingview.com/chart/?symbol=NSE:{clean_sym}"

    end_dt = TARGET_DATE
    start_dt = end_dt - datetime.timedelta(days=15)

    data = {
        "symbol": symbol,
        "resolution": "5",
        "date_format": "1",
        "range_from": start_dt.strftime("%Y-%m-%d"),
        "range_to": end_dt.strftime("%Y-%m-%d"),
        "cont_flag": "1"
    }

    try:
        resp = fyers.history(data=data)
        if resp.get("s") != "ok" or not resp.get("candles"):
            return None, local_stats

        local_stats["data_rcvd"] = 1

        df = pd.DataFrame(resp["candles"], columns=["ts", "open", "high", "low", "close", "volume"])
        if len(df) < 40:
            return None, local_stats

        df["datetime"] = pd.to_datetime(df["ts"], unit="s").dt.tz_localize("UTC").dt.tz_convert(ist)
        df = df.sort_values("datetime").reset_index(drop=True)

        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

        day_mask = (df["datetime"].dt.date == TARGET_DATE) & (df["datetime"].dt.time >= datetime.time(9, 15))
        day_df = df.loc[day_mask].copy()

        if len(day_df) < 3:
            return None, local_stats

        typical = (day_df["high"] + day_df["low"] + day_df["close"]) / 3.0
        day_df["cum_tp_vol"] = (typical * day_df["volume"]).cumsum()
        day_df["cum_vol"] = day_df["volume"].cumsum()
        day_df["vwap"] = day_df["cum_tp_vol"] / day_df["cum_vol"]

        first = day_df.iloc[0]
        second = day_df.iloc[1]

        first_range_pct = ((first["high"] - first["low"]) / first["open"]) * 100
        if first_range_pct > 1.5:
            return None, local_stats
        local_stats["pass_range"] = 1

        if not (first["low"] <= second["open"] <= first["high"] and
                first["low"] <= second["close"] <= first["high"] and
                second["high"] <= first["high"] and
                second["low"] >= first["low"]):
            return None, local_stats
        local_stats["pass_2nd"] = 1

        first_close = float(first["close"])
        first_ema20 = float(first["ema20"])
        first_ema200 = float(first["ema200"])
        first_vwap = float(first["vwap"])

        is_bullish = first_close > first_ema20 and first_close > first_ema200 and first_close > first_vwap
        is_bearish = first_close < first_ema20 and first_close < first_ema200 and first_close < first_vwap

        if not (is_bullish or is_bearish):
            return None, local_stats
        local_stats["pass_bias"] = 1
        local_stats["reached_breakout"] = 1

        for i in range(2, len(day_df)):
            candle = day_df.iloc[i]
            prev_vols = day_df.iloc[max(0, i-5):i]["volume"]
            avg_vol = prev_vols.mean() if len(prev_vols) > 0 else float(candle["volume"])
            volume_ok = float(candle["volume"]) > (avg_vol * 1.2)

            c_close = float(candle["close"])
            c_vwap = float(candle["vwap"])

            if is_bullish and float(candle["high"]) > float(first["high"]) and c_close > c_vwap and volume_ok:
                local_stats["final"] = 1
                return {
                    "symbol": clean_sym,
                    "price": round(c_close, 2),
                    "change": round(((c_close - float(first["open"])) / float(first["open"])) * 100, 2),
                    "time": candle["datetime"].strftime("%H:%M"),
                    "type": "BULLISH",
                    "status": "READY",
                    "tv_url": tv_url,
                    "qty": calculate_qty(c_close)
                }, local_stats

            if is_bearish and float(candle["low"]) < float(first["low"]) and c_close < c_vwap and volume_ok:
                local_stats["final"] = 1
                return {
                    "symbol": clean_sym,
                    "price": round(c_close, 2),
                    "change": round(((c_close - float(first["open"])) / float(first["open"])) * 100, 2),
                    "time": candle["datetime"].strftime("%H:%M"),
                    "type": "BEARISH",
                    "status": "READY",
                    "tv_url": tv_url,
                    "qty": calculate_qty(c_close)
                }, local_stats

        return None, local_stats
    except Exception:
        return None, local_stats

@st.cache_data(ttl=30, show_spinner=False)
def run_scanner() -> Tuple[pd.DataFrame, dict]:
    summary_stats = {
        "total_scanned": 0, "data_received": 0, "passed_range": 0,
        "passed_second_candle": 0, "passed_bias": 0, "reached_breakout_check": 0, "final_qualified": 0
    }

    results = []
    if not fyers:
        st.error("❌ Fyers Client Initialization Failed! Please check FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN in Streamlit Secrets.")
        return pd.DataFrame(), summary_stats

    symbols_to_scan = SYMBOL_UNIVERSE[:120]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scan_single_stock, sym) for sym in symbols_to_scan]
        for future in as_completed(futures):
            res, st_data = future.result()
            summary_stats["total_scanned"] += st_data["scanned"]
            summary_stats["data_received"] += st_data["data_rcvd"]
            summary_stats["passed_range"] += st_data["pass_range"]
            summary_stats["passed_second_candle"] += st_data["pass_2nd"]
            summary_stats["passed_bias"] += st_data["pass_bias"]
            summary_stats["reached_breakout_check"] += st_data["reached_breakout"]
            summary_stats["final_qualified"] += st_data["final"]

            if res and res.get("price", 0) >= 200:
                results.append(res)

    df = pd.DataFrame(results).sort_values("change", ascending=False).reset_index(drop=True) if results else pd.DataFrame()
    return df, summary_stats

with st.spinner(f"Scanning {TARGET_DATE.strftime('%d %b %Y')}..."):
    df_all, stats = run_scanner()

bullish_df = df_all[df_all["type"] == "BULLISH"].head(8) if not df_all.empty else pd.DataFrame()
bearish_df = df_all[df_all["type"] == "BEARISH"].head(8) if not df_all.empty else pd.DataFrame()

# KPI
c1, c2, c3, c4 = st.columns(4)
with c1:
    top_g = bullish_df.iloc[0] if not bullish_df.empty else {"symbol": "—", "change": 0, "time": "--:--", "qty": 0, "tv_url": "#"}
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
            <a href="{top_g['tv_url']}" target="_blank" class="stock-title-link" style="font-size:17px;">{top_g['symbol']}</a>
            <span style="font-size:17px;font-weight:900;color:#00ff87;">+{top_g['change']}%</span>
        </div>
        <div style="margin-top:8px;display:flex;justify-content:space-between;">
            <span style="font-size:12px;color:{txt_muted};">🕒 {top_g['time']}</span>
            <span class="qty-badge">QTY: {top_g['qty']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    top_l = bearish_df.iloc[0] if not bearish_df.empty else {"symbol": "—", "change": 0, "time": "--:--", "qty": 0, "tv_url": "#"}
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
            <a href="{top_l['tv_url']}" target="_blank" class="stock-title-link" style="font-size:17px;color:#f43f5e;">{top_l['symbol']}</a>
            <span style="font-size:17px;font-weight:900;color:#f43f5e;">{top_l['change']}%</span>
        </div>
        <div style="margin-top:8px;display:flex;justify-content:space-between;">
            <span style="font-size:12px;color:{txt_muted};">🕒 {top_l['time']}</span>
            <span class="qty-badge">QTY: {top_l['qty']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    is_bull = len(bullish_df) >= len(bearish_df)
    s_txt = "BULLISH" if is_bull else "BEARISH"
    s_clr = "#00ff87" if is_bull else "#f43f5e"
    d_class = "dot-green" if is_bull else "dot-red"
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:17px;font-weight:900;color:{s_clr};margin-top:4px;">
            <span class="{d_class}"></span>{s_txt}
        </div>
        <div style="margin-top:8px;font-size:12px;color:{txt_muted};">Bullish: {len(bullish_df)} | Bearish: {len(bearish_df)}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">ACTIVE SETUPS</div>
        <div style="font-size:17px;font-weight:900;color:#00e5ff;margin-top:4px;">{len(df_all)}</div>
        <div style="margin-top:8px;font-size:12px;color:{txt_muted};">{TARGET_DATE.strftime('%d %b %Y')} | ≥ ₹200</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h3 style='text-align:center;margin:8px 0 12px 0;font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)
m_cols = st.columns(8)
for idx, (_, item) in enumerate(bullish_df.head(4).iterrows()):
    with m_cols[idx]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link">{item['symbol']}</a><br>
            <div style="font-size:13px;color:#00ff87;font-weight:bold;">₹{item['price']}</div>
            <div style="font-size:11px;color:#00ff87;font-weight:bold;">(+{item['change']}%)</div>
            <div style="margin-top:4px;"><span class="qty-badge">{item['qty']}</span> <span style="font-size:10px;color:{txt_muted};">🕒 {item['time']}</span></div>
        </div>
        """, unsafe_allow_html=True)
for idx, (_, item) in enumerate(bearish_df.head(4).iterrows()):
    with m_cols[idx+4]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="color:#f43f5e;">{item['symbol']}</a><br>
            <div style="font-size:13px;color:#f43f5e;font-weight:bold;">₹{item['price']}</div>
            <div style="font-size:11px;color:#f43f5e;font-weight:bold;">({item['change']}%)</div>
            <div style="margin-top:4px;"><span class="qty-badge">{item['qty']}</span> <span style="font-size:10px;color:{txt_muted};">🕒 {item['time']}</span></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

t1, t2 = st.columns(2)
with t1:
    st.markdown("<h4 style='color:#00ff87;margin-bottom:8px;font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    if bullish_df.empty:
        st.info(f"کوئی Bullish Setup نہیں ملا ({TARGET_DATE.strftime('%d %b')})")
    else:
        for _, row in bullish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:16%;"><span class="tag-ready-bull">READY</span></div>
                <div style="width:16%;font-size:13px;color:{txt_muted};">🕒 {row['time']}</div>
                <div style="width:14%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:16%;font-size:14px;font-weight:bold;">₹{row['price']}</div>
                <div style="width:16%;font-size:14px;font-weight:bold;color:#00ff87;">+{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#f43f5e;margin-bottom:8px;font-weight:800;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    if bearish_df.empty:
        st.info(f"کوئی Bearish Setup نہیں ملا ({TARGET_DATE.strftime('%d %b')})")
    else:
        for _, row in bearish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:16%;"><span class="tag-ready-bear">READY</span></div>
                <div style="width:16%;font-size:13px;color:{txt_muted};">🕒 {row['time']}</div>
                <div style="width:14%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:16%;font-size:14px;font-weight:bold;">₹{row['price']}</div>
                <div style="width:16%;font-size:14px;font-weight:bold;color:#f43f5e;">{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- DEBUG PANEL -----------------
st.markdown("---")
st.subheader("🔍 Debug Information")
st.write(f"""
- **Total Symbols Attempted**: {stats['total_scanned']}
- **Data Received from Fyers**: {stats['data_received']}
- **Passed Range ≤ 1.5%**: {stats['passed_range']}
- **Passed Second Candle Inside**: {stats['passed_second_candle']}
- **Passed Bias (EMA + VWAP)**: {stats['passed_bias']}
- **Reached Breakout Check**: {stats['reached_breakout_check']}
- **Final Qualified Setups**: {stats['final_qualified']}
""")
