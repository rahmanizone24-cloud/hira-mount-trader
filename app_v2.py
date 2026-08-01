import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List

import pandas as pd
import pytz
import streamlit as st

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HiraMountTrader")

try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None
    logger.warning("fyers_apiv3 not installed")

# ---------------------------------------------------------
# 1. Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="HIRA MOUNT TRADER",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📈"
)

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_refresh")
except ImportError:
    pass

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"


def toggle_theme():
    st.session_state["theme_mode"] = "Light" if st.session_state["theme_mode"] == "Dark" else "Dark"


# Theme Colors
if st.session_state["theme_mode"] == "Dark":
    bg_app = "#06090e"
    bg_card = "#0f172a"
    border_clr = "#1e293b"
    txt_main = "#f8fafc"
    txt_muted = "#94a3b8"
    badge_bg = "#1e293b"
    btn_bg = "#1e293b"
    btn_txt = "#f8fafc"
else:
    bg_app = "#f1f5f9"
    bg_card = "#ffffff"
    border_clr = "#cbd5e1"
    txt_main = "#0f172a"
    txt_muted = "#64748b"
    badge_bg = "#e2e8f0"
    btn_bg = "#e2e8f0"
    btn_txt = "#0f172a"

# ---------------------------------------------------------
# CSS (Corrected)
# ---------------------------------------------------------
st.markdown(
    f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    .main .block-container {{
        max-width: 100% !important;
        padding: 0.6rem 0.8rem 0.4rem 0.8rem !important;
    }}
    
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    
    [data-testid="column"] {{ padding: 0 4px !important; }}

    div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: 1px solid {border_clr} !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }}

    .top-bar-container {{
        background-color: {bg_card};
        padding: 8px 14px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {border_clr};
        margin-bottom: 10px;
        flex-wrap: wrap;
        gap: 8px;
    }}
    
    .brand-title {{ font-size: 18px; font-weight: 900; color: #00e5ff; letter-spacing: 0.5px; }}
    
    .index-badge {{
        background: {badge_bg};
        color: #38bdf8;
        padding: 4px 9px;
        border-radius: 6px;
        font-size: 11px;
        border: 1px solid {border_clr};
        font-weight: 800;
        text-decoration: none;
    }}
    
    .idx-bull {{ color: #00ff87 !important; border-color: #065f46 !important; background: #022c22 !important; }}
    .idx-bear {{ color: #f43f5e !important; border-color: #9f1239 !important; background: #4c0519 !important; }}

    @keyframes dotGlow {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.35; }}
        100% {{ opacity: 1; }}
    }}
    .dot-green {{ display: inline-block; width: 8px; height: 8px; background: #00ff87; border-radius: 50%; animation: dotGlow 2.2s infinite; margin-right: 5px; }}
    .dot-red {{ display: inline-block; width: 8px; height: 8px; background: #f43f5e; border-radius: 50%; animation: dotGlow 2.2s infinite; margin-right: 5px; }}

    .stat-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }}
    .stat-title {{ font-size: 10px; color: {txt_muted}; font-weight: 700; letter-spacing: 0.4px; }}
    
    .mover-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 7px 6px;
        text-align: center;
    }}
    
    .stock-title-link {{ font-size: 14px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: #7dd3fc; }}
    
    .table-header-row {{
        display: flex;
        justify-content: space-between;
        padding: 5px 12px;
        font-size: 10px;
        font-weight: 800;
        color: {txt_muted};
        margin-bottom: 4px;
    }}

    .setup-card {{
        background-color: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 7px 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .qty-badge {{
        background-color: {badge_bg};
        border: 1px solid {border_clr};
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 700;
        color: #00e5ff;
    }}
    
    .tag-ready-bull {{ 
        background-color: #00ff87 !important; 
        color: #022c22 !important; 
        padding: 3px 8px; 
        border-radius: 5px; 
        font-size: 10px; 
        font-weight: 900; 
    }}
    
    .tag-ready-bear {{ 
        background-color: #f43f5e !important; 
        color: #ffffff !important; 
        padding: 3px 8px; 
        border-radius: 5px; 
        font-size: 10px; 
        font-weight: 900; 
    }}

    #MainMenu {{visibility: hidden;}} 
    footer {{visibility: hidden;}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. Fyers Client
# ---------------------------------------------------------
CLIENT_ID = st.secrets.get("FYERS_CLIENT_ID", "")
ACCESS_TOKEN = st.secrets.get("FYERS_ACCESS_TOKEN", "")


@st.cache_resource
def get_fyers():
    if not fyersModel or not CLIENT_ID or not ACCESS_TOKEN:
        return None
    try:
        return fyersModel.FyersModel(
            client_id=CLIENT_ID,
            token=ACCESS_TOKEN,
            is_async=False,
            log_path=""
        )
    except Exception as e:
        logger.error(f"Fyers init failed: {e}")
        return None


fyers = get_fyers()

# ---------------------------------------------------------
# 3. Time & Market Status + Target Date Logic
# ---------------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(ist)

market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
is_weekday = now_ist.weekday() < 5
is_market_open = is_weekday and market_open <= now_ist <= market_close

if is_market_open:
    market_status_html = '<span style="background:#064e3b;color:#34d399;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold;"><span class="dot-green"></span>OPEN</span>'
else:
    market_status_html = '<span style="background:#881337;color:#fecdd3;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold;"><span class="dot-red"></span>CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")


def get_last_trading_day(current_dt: datetime.datetime) -> datetime.date:
    """Return the most recent trading day (skip Sat/Sun)."""
    d = current_dt.date()
    # If today is weekday and market already closed, still use today
    if current_dt.weekday() < 5 and current_dt.time() >= datetime.time(15, 30):
        return d
    # Otherwise go back until we find a weekday
    while True:
        d = d - datetime.timedelta(days=1)
        if d.weekday() < 5:  # Mon-Fri
            return d


# Target date for scanning
if is_market_open:
    TARGET_DATE = now_ist.date()
else:
    TARGET_DATE = get_last_trading_day(now_ist)

# ---------------------------------------------------------
# 4. Symbol Universe
# ---------------------------------------------------------
@st.cache_data(ttl=86400)
def get_symbol_universe() -> List[str]:
    try:
        url = "https://public.fyers.in/sym_details/NSE_CM.csv"
        df = pd.read_csv(url, header=None)
        symbols = (
            df[df[9].astype(str).str.endswith("-EQ", na=False)][9]
            .dropna()
            .unique()
            .tolist()
        )
        return symbols[:600]
    except Exception as e:
        logger.error(f"Symbol master fetch failed: {e}")
        return [
            "NSE:RELIANCE-EQ", "NSE:TCS-EQ", "NSE:HDFCBANK-EQ", "NSE:ICICIBANK-EQ",
            "NSE:INFY-EQ", "NSE:BHARTIARTL-EQ", "NSE:ITC-EQ", "NSE:SBIN-EQ",
            "NSE:LT-EQ", "NSE:BAJFINANCE-EQ", "NSE:HINDUNILVR-EQ", "NSE:KOTAKBANK-EQ",
            "NSE:AXISBANK-EQ", "NSE:ASIANPAINT-EQ", "NSE:MARUTI-EQ", "NSE:SUNPHARMA-EQ",
            "NSE:TITAN-EQ", "NSE:ULTRACEMCO-EQ", "NSE:WIPRO-EQ", "NSE:NESTLEIND-EQ"
        ]


SYMBOL_UNIVERSE = get_symbol_universe()

# ---------------------------------------------------------
# 5. Live Index Quotes
# ---------------------------------------------------------
@st.cache_data(ttl=20)
def get_live_indices():
    default = {"nifty": 0.0, "bank": 0.0, "sensex": 0.0}
    if not fyers:
        return default
    try:
        data = {"symbols": "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX,BSE:SENSEX-INDEX"}
        resp = fyers.quotes(data=data)
        if resp.get("s") != "ok":
            return default
        result = default.copy()
        for item in resp.get("d", []):
            n = item.get("n", "")
            v = item.get("v", {})
            chp = float(v.get("chp", 0) or 0)
            if "NIFTY50" in n:
                result["nifty"] = chp
            elif "NIFTYBANK" in n or "BANKNIFTY" in n:
                result["bank"] = chp
            elif "SENSEX" in n:
                result["sensex"] = chp
        return result
    except Exception as e:
        logger.error(f"Index quotes error: {e}")
        return default


indices = get_live_indices()

def make_index_badge(name: str, change: float, symbol: str) -> str:
    if change >= 0:
        return (f'<a href="https://in.tradingview.com/chart/?symbol={symbol}" target="_blank" '
                f'class="index-badge idx-bull">{name} ▲ +{change:.2f}%</a>')
    else:
        return (f'<a href="https://in.tradingview.com/chart/?symbol={symbol}" target="_blank" '
                f'class="index-badge idx-bear">{name} ▼ {change:.2f}%</a>')

nifty_html = make_index_badge("NIFTY 50", indices["nifty"], "NSE:NIFTY")
bank_html = make_index_badge("BANK NIFTY", indices["bank"], "NSE:BANKNIFTY")
sensex_html = make_index_badge("SENSEX", indices["sensex"], "BSE:SENSEX")

# ---------------------------------------------------------
# Top Bar
# ---------------------------------------------------------
col1, col2, col3 = st.columns([10, 1, 1])
with col1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        {nifty_html}
        {bank_html}
        {sensex_html}
        {market_status_html}
        <span class="index-badge" style="color:#00e5ff;">🕒 {time_str}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    theme_label = "☀️ Light" if st.session_state["theme_mode"] == "Dark" else "🌙 Dark"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------------
# 6. Core Strategy Engine
# ---------------------------------------------------------
def calculate_qty(price: float) -> int:
    if price <= 0:
        return 1
    return max(1, int(50000 / price))


def scan_single_stock(symbol: str) -> Optional[Dict]:
    try:
        if not fyers:
            return None

        clean_sym = symbol.replace("NSE:", "").replace("-EQ", "")
        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE:{clean_sym}"

        # Fetch enough history
        end_dt = TARGET_DATE
        start_dt = end_dt - datetime.timedelta(days=12)

        data = {
            "symbol": symbol,
            "resolution": "5",
            "date_format": "1",
            "range_from": start_dt.strftime("%Y-%m-%d"),
            "range_to": end_dt.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }

        resp = fyers.history(data=data)
        if resp.get("s") != "ok" or not resp.get("candles"):
            return None

        df = pd.DataFrame(resp["candles"], columns=["ts", "open", "high", "low", "close", "volume"])
        if len(df) < 50:
            return None

        df["datetime"] = pd.to_datetime(df["ts"], unit="s").dt.tz_localize("UTC").dt.tz_convert(ist)
        df = df.sort_values("datetime").reset_index(drop=True)

        # Filter for TARGET_DATE candles (from 09:15)
        day_mask = (df["datetime"].dt.date == TARGET_DATE) & (df["datetime"].dt.time >= datetime.time(9, 15))
        day_df = df[day_mask].copy()

        if len(day_df) < 3:
            return None

        # Indicators
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

        typical = (df["high"] + df["low"] + df["close"]) / 3
        df["cum_tp_vol"] = (typical * df["volume"]).cumsum()
        df["cum_vol"] = df["volume"].cumsum()
        df["vwap"] = df["cum_tp_vol"] / df["cum_vol"]

        day_df = df.loc[day_df.index].copy()

        first = day_df.iloc[0]
        second = day_df.iloc[1]

        first_range_pct = ((first["high"] - first["low"]) / first["open"]) * 100
        if first_range_pct > 1.5:
            return None

        if not (first["low"] <= second["open"] <= first["high"] and
                first["low"] <= second["close"] <= first["high"] and
                second["high"] <= first["high"] and
                second["low"] >= first["low"]):
            return None

        first_close = first["close"]
        first_ema20 = first["ema20"]
        first_ema200 = first["ema200"]
        first_vwap = first["vwap"]

        is_bullish_bias = (first_close > first_ema20 and
                          first_close > first_ema200 and
                          first_close > first_vwap)

        is_bearish_bias = (first_close < first_ema20 and
                           first_close < first_ema200 and
                           first_close < first_vwap)

        if not (is_bullish_bias or is_bearish_bias):
            return None

        for i in range(2, len(day_df)):
            candle = day_df.iloc[i]
            prev_5 = day_df.iloc[max(0, i-5):i]
            avg_vol = prev_5["volume"].mean() if len(prev_5) > 0 else candle["volume"]

            volume_ok = candle["volume"] > (avg_vol * 1.2)

            if is_bullish_bias:
                if (candle["high"] > first["high"] and
                    candle["close"] > candle["vwap"] and
                    volume_ok):

                    return {
                        "symbol": clean_sym,
                        "price": round(float(candle["close"]), 2),
                        "change": round(((candle["close"] - first["open"]) / first["open"]) * 100, 2),
                        "time": candle["datetime"].strftime("%H:%M"),
                        "type": "BULLISH",
                        "status": "READY",
                        "tv_url": tv_url,
                        "qty": calculate_qty(float(candle["close"]))
                    }

            elif is_bearish_bias:
                if (candle["low"] < first["low"] and
                    candle["close"] < candle["vwap"] and
                    volume_ok):

                    return {
                        "symbol": clean_sym,
                        "price": round(float(candle["close"]), 2),
                        "change": round(((candle["close"] - first["open"]) / first["open"]) * 100, 2),
                        "time": candle["datetime"].strftime("%H:%M"),
                        "type": "BEARISH",
                        "status": "READY",
                        "tv_url": tv_url,
                        "qty": calculate_qty(float(candle["close"]))
                    }

        return None

    except Exception as e:
        logger.debug(f"Error scanning {symbol}: {e}")
        return None


@st.cache_data(ttl=25, show_spinner=False)
def run_scanner() -> pd.DataFrame:
    results = []
    if not fyers:
        return pd.DataFrame()

    symbols_to_scan = SYMBOL_UNIVERSE[:180]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scan_single_stock, sym): sym for sym in symbols_to_scan}
        for future in as_completed(futures):
            res = future.result()
            if res and res["price"] >= 200:
                results.append(res)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df = df.sort_values("change", ascending=False).reset_index(drop=True)
    return df


# ---------------------------------------------------------
# 7. Run Scanner
# ---------------------------------------------------------
with st.spinner(f"Scanning setups for {TARGET_DATE.strftime('%d %b %Y')}..."):
    df_all = run_scanner()

bullish_df = df_all[df_all["type"] == "BULLISH"].head(8) if not df_all.empty else pd.DataFrame()
bearish_df = df_all[df_all["type"] == "BEARISH"].head(8) if not df_all.empty else pd.DataFrame()

# ---------------------------------------------------------
# 8. KPI Cards
# ---------------------------------------------------------
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
        <div style="margin-top:8px;font-size:12px;color:{txt_muted};">
            Bullish: {len(bullish_df)} | Bearish: {len(bearish_df)}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">ACTIVE SETUPS</div>
        <div style="font-size:17px;font-weight:900;color:#00e5ff;margin-top:4px;">{len(df_all)}</div>
        <div style="margin-top:8px;font-size:12px;color:{txt_muted};">
            {TARGET_DATE.strftime('%d %b')} | Price ≥ ₹200
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 9. Market Movers
# ---------------------------------------------------------
st.markdown("<h3 style='text-align:center;margin:8px 0 12px 0;font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)

movers_bull = bullish_df.head(4)
movers_bear = bearish_df.head(4)
m_cols = st.columns(8)

for idx, (_, item) in enumerate(movers_bull.iterrows()):
    with m_cols[idx]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link">{item['symbol']}</a><br>
            <div style="font-size:13px;color:#00ff87;font-weight:bold;margin-top:2px;">₹{item['price']}</div>
            <div style="font-size:11px;color:#00ff87;font-weight:bold;">(+{item['change']}%)</div>
            <div style="margin-top:4px;display:flex;justify-content:center;gap:4px;">
                <span class="qty-badge">{item['qty']}</span>
                <span style="font-size:10px;color:{txt_muted};">🕒 {item['time']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

for idx, (_, item) in enumerate(movers_bear.iterrows()):
    with m_cols[idx + 4]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="color:#f43f5e;">{item['symbol']}</a><br>
            <div style="font-size:13px;color:#f43f5e;font-weight:bold;margin-top:2px;">₹{item['price']}</div>
            <div style="font-size:11px;color:#f43f5e;font-weight:bold;">({item['change']}%)</div>
            <div style="margin-top:4px;display:flex;justify-content:center;gap:4px;">
                <span class="qty-badge">{item['qty']}</span>
                <span style="font-size:10px;color:{txt_muted};">🕒 {item['time']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 10. Setup Tables
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#00ff87;margin-bottom:8px;font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:22%;">SYMBOL</div>
        <div style="width:16%;">STATUS</div>
        <div style="width:16%;">TIME</div>
        <div style="width:14%;">QTY</div>
        <div style="width:16%;">PRICE</div>
        <div style="width:16%;">CHANGE</div>
    </div>
    """, unsafe_allow_html=True)

    if bullish_df.empty:
        st.info(f"کوئی Bullish Setup نہیں ملا ({TARGET_DATE.strftime('%d %b')})")
    else:
        for _, row in bullish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:16%;"><span class="tag-ready-bull">READY</span></div>
                <div style="width:16%;font-size:13px;color:{txt_muted};font-weight:600;">🕒 {row['time']}</div>
                <div style="width:14%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:16%;font-size:14px;font-weight:bold;">₹{row['price']}</div>
                <div style="width:16%;font-size:14px;font-weight:bold;color:#00ff87;">+{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='color:#f43f5e;margin-bottom:8px;font-weight:800;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:22%;">SYMBOL</div>
        <div style="width:16%;">STATUS</div>
        <div style="width:16%;">TIME</div>
        <div style="width:14%;">QTY</div>
        <div style="width:16%;">PRICE</div>
        <div style="width:16%;">CHANGE</div>
    </div>
    """, unsafe_allow_html=True)

    if bearish_df.empty:
        st.info(f"کوئی Bearish Setup نہیں ملا ({TARGET_DATE.strftime('%d %b')})")
    else:
        for _, row in bearish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:22%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:16%;"><span class="tag-ready-bear">READY</span></div>
                <div style="width:16%;font-size:13px;color:{txt_muted};font-weight:600;">🕒 {row['time']}</div>
                <div style="width:14%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:16%;font-size:14px;font-weight:bold;">₹{row['price']}</div>
                <div style="width:16%;font-size:14px;font-weight:bold;color:#f43f5e;">{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)
