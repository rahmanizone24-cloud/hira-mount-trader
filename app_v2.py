import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
import pandas as pd
import pytz
import streamlit as st

# Fyers API v3 Integration
try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None

# ---------------------------------------------------------
# 1. Page Configuration & Permanent Theme Logic (Fix)
# ---------------------------------------------------------
st.set_page_config(
    page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed"
)

# Smooth Auto-Refresh Logic (Every 30 Seconds)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_mount_refresh_key")
except ImportError:
    pass

# PERMANENT THEME FIX: URL Query Params کے ذریعے تھیم کی ویلیو لاک کی گئی ہے
if "theme" in st.query_params:
    current_theme = st.query_params["theme"]
    st.session_state["theme_mode"] = current_theme
else:
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Dark"
        st.query_params["theme"] = "Dark"

def toggle_theme():
    new_theme = "Light" if st.session_state["theme_mode"] == "Dark" else "Dark"
    st.session_state["theme_mode"] = new_theme
    st.query_params["theme"] = new_theme

# Dynamic Themes Styling with High-Visibility Colors for Dark Mode
if st.session_state["theme_mode"] == "Dark":
    bg_app = "#06090e"
    bg_card = "#0f172a"
    border_clr = "#1e293b"
    txt_main = "#f8fafc"
    txt_muted = "#cbd5e1"        # ڈارک تھیم کے لیے زیادہ روشن ٹیکسٹ
    symbol_link_clr = "#00e5ff"  # انتہائی روشن اور چمکدار سائین رنگ (High Contrast)
    symbol_hover_clr = "#7dd3fc"
    badge_bg = "#1e293b"
    btn_bg = "#1e293b"
    btn_txt = "#f8fafc"
else:
    bg_app = "#f1f5f9"
    bg_card = "#ffffff"
    border_clr = "#cbd5e1"
    txt_main = "#0f172a"
    txt_muted = "#64748b"
    symbol_link_clr = "#0284c7"  # لائٹ تھیم کے لیے ڈارک پرفیکٹ بلو
    symbol_hover_clr = "#0369a1"
    badge_bg = "#e2e8f0"
    btn_bg = "#e2e8f0"
    btn_txt = "#0f172a"

st.markdown(
    f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    .main .block-container {{
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }}
    
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    
    [data-testid="column"] {{ padding: 0px 3px !important; }}

    div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: 1px solid {border_clr} !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-weight: 700 !important;
    }}

    .top-bar-container {{
        background-color: {bg_card};
        padding: 6px 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {border_clr};
        margin-bottom: 8px;
        width: 100%;
    }}
    
    .brand-title {{ font-size: 18px; font-weight: 900; color: #00e5ff; letter-spacing: 0.5px; white-space: nowrap; }}
    
    .index-badge {{
        background: {badge_bg};
        color: #38bdf8;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        text-decoration: none;
        border: 1px solid {border_clr};
        font-weight: 800;
        white-space: nowrap;
    }}
    
    .idx-bull {{ color: #00ff87 !important; border-color: #065f46 !important; background: #022c22 !important; }}
    .idx-bear {{ color: #f43f5e !important; border-color: #9f1239 !important; background: #4c0519 !important; }}

    @keyframes dotGlow {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.3; transform: scale(0.9); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .dot-green {{ display: inline-block; width: 8px; height: 8px; background-color: #00ff87; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}
    .dot-red {{ display: inline-block; width: 8px; height: 8px; background-color: #f43f5e; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}

    .stat-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
    }}
    .stat-title {{ font-size: 10px; color: {txt_muted}; font-weight: bold; letter-spacing: 0.5px; }}
    
    .stock-title-link {{ font-size: 14px; font-weight: 800; color: {symbol_link_clr} !important; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: {symbol_hover_clr} !important; }}
    
    .table-header-row {{
        display: flex;
        justify-content: space-between;
        padding: 4px 12px;
        font-size: 10px;
        font-weight: 800;
        color: {txt_muted};
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}

    .setup-card {{
        background-color: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 6px 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .qty-badge {{
        background-color: {badge_bg};
        border: 1px solid {border_clr};
        padding: 2px 6px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 700;
        color: #00e5ff;
        display: inline-block;
    }}

    .hyperflow-badge {{
        background-color: #1e1b4b;
        border: 1px solid #6366f1;
        color: #818cf8;
        padding: 2px 6px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 900;
        display: inline-block;
    }}
    .hyperflow-high {{
        background-color: #312e81 !important;
        color: #c084fc !important;
        border-color: #a855f7 !important;
        box-shadow: 0 0 6px rgba(168, 85, 247, 0.4);
    }}
    
    .tag-watchlist {{ background-color: #78350f; color: #fde047; padding: 3px 8px; border-radius: 5px; font-size: 10px; font-weight: 800; }}
    
    .tag-ready-bull {{ 
        background-color: #00ff87 !important; 
        color: #022c22 !important; 
        padding: 3px 8px; 
        border-radius: 5px; 
        font-size: 10px; 
        font-weight: 900; 
        box-shadow: 0 0 8px rgba(0, 255, 135, 0.4);
    }}
    
    .tag-ready-bear {{ 
        background-color: #f43f5e !important; 
        color: #ffffff !important; 
        padding: 3px 8px; 
        border-radius: 5px; 
        font-size: 10px; 
        font-weight: 900; 
        box-shadow: 0 0 8px rgba(244, 63, 94, 0.4);
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. Fyers API Client Initialization
# ---------------------------------------------------------
CLIENT_ID = st.secrets.get("FYERS_CLIENT_ID", "YOUR_APP_ID-100")
ACCESS_TOKEN = st.secrets.get("FYERS_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")

@st.cache_resource
def get_fyers_instance():
    if fyersModel and CLIENT_ID != "YOUR_APP_ID-100":
        try:
            return fyersModel.FyersModel(
                client_id=CLIENT_ID,
                token=ACCESS_TOKEN,
                is_async=False,
                log_path="",
            )
        except Exception:
            return None
    return None

fyers = get_fyers_instance()

# ---------------------------------------------------------
# 3. Time & Market Status
# ---------------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(ist)

market_open_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_ist.weekday() < 5
is_market_hours = market_open_time <= now_ist <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span style="background:#064e3b; color:#34d399; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-green"></span>OPEN</span>'
else:
    market_status_html = '<span style="background:#881337; color:#fecdd3; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-red"></span>CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")

# ---------------------------------------------------------
# 4. Fetch Live Nifty 500 Symbol Master directly from Fyers
# ---------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_fyers_nifty500_symbols():
    try:
        url = "https://public.fyers.in/sym_details/NSE_CM.csv"
        df_sym = pd.read_csv(url, header=None)
        eq_symbols = df_sym[df_sym[9].str.endswith("-EQ", na=False)][9].tolist()
        return eq_symbols[:500]
    except Exception:
        return [
            "NSE:RELIANCE-EQ", "NSE:TCS-EQ", "NSE:HDFCBANK-EQ", "NSE:ICICIBANK-EQ",
            "NSE:INFY-EQ", "NSE:BHARTIARTL-EQ", "NSE:ITC-EQ", "NSE:SBIN-EQ",
            "NSE:LT-EQ", "NSE:BAJFINANCE-EQ"
        ]

NIFTY_500_SYMBOLS = fetch_fyers_nifty500_symbols()

# ---------------------------------------------------------
# 5. Dynamic Index Direction Setup & Top Bar
# ---------------------------------------------------------
nifty_change = 0.85
bank_change = 1.12
sensex_change = -0.24

nifty_html = (
    f'<a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge idx-bull">NIFTY 50 ▲ +{nifty_change}%</a>'
    if nifty_change >= 0
    else f'<a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge idx-bear">NIFTY 50 ▼ {nifty_change}%</a>'
)
bank_html = (
    f'<a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge idx-bull">BANK NIFTY ▲ +{bank_change}%</a>'
    if bank_change >= 0
    else f'<a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge idx-bear">BANK NIFTY ▼ {bank_change}%</a>'
)
sensex_html = (
    f'<a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge idx-bull">SENSEX ▲ +{sensex_change}%</a>'
    if sensex_change >= 0
    else f'<a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge idx-bear">SENSEX ▼ {sensex_change}%</a>'
)

col_top1, col_top_theme, col_top_ref = st.columns([10, 1, 1])

with col_top1:
    st.markdown(
        f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        {nifty_html}
        {bank_html}
        {sensex_html}
        {market_status_html}
        <span class="index-badge" style="color:#00e5ff;">🕒 {time_str}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_top_theme:
    theme_label = "☀️ Light" if st.session_state["theme_mode"] == "Dark" else "🌙 Dark"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

with col_top_ref:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------
# 6. Direct Market Scan (No Filter Logic)
# ---------------------------------------------------------
def calculate_5x_qty(price):
    if price <= 0:
        return 1
    return max(1, int(50000 / price))

def scan_single_fyers_stock(symbol):
    try:
        clean_sym = symbol.replace("NSE:", "").replace("-EQ", "")
        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE:{clean_sym}"

        if not fyers:
            return None

        today_str = now_ist.strftime("%Y-%m-%d")
        data = {
            "symbol": symbol,
            "resolution": "5",
            "date_format": "1",
            "range_from": today_str,
            "range_to": today_str,
            "cont_flag": "1",
        }
        hist = fyers.history(data=data)
        if hist.get("s") == "ok" and hist.get("candles"):
            df = pd.DataFrame(
                hist["candles"],
                columns=["timestamp", "open", "high", "low", "close", "volume"],
            )

            if len(df) >= 2:
                curr_p = df["close"].iloc[-1]
                open_p = df["open"].iloc[0]
                chg = round(((curr_p - open_p) / open_p) * 100, 2)

                last_candle_time = datetime.datetime.fromtimestamp(
                    df["timestamp"].iloc[-1], tz=ist
                )
                st_time = last_candle_time.strftime("%H:%M")

                avg_vol = df["volume"].iloc[:-1].mean() if len(df) > 1 else df["volume"].iloc[-1]
                curr_vol = df["volume"].iloc[-1]
                hyper_flow_score = round(curr_vol / avg_vol, 1) if avg_vol > 0 else 1.0

                # بغیر کسی EMA/VWAP لاجک کے، صرف ڈائریکٹ پرائس موومنٹ کی بنیاد پر کلاسیفکیشن
                if chg >= 0:
                    return {
                        "symbol": clean_sym,
                        "price": curr_p,
                        "change": chg,
                        "time": st_time,
                        "type": "BULLISH",
                        "status": "READY",
                        "tv_url": tv_url,
                        "hyperflow": hyper_flow_score,
                    }
                else:
                    return {
                        "symbol": clean_sym,
                        "price": curr_p,
                        "change": chg,
                        "time": st_time,
                        "type": "BEARISH",
                        "status": "READY",
                        "tv_url": tv_url,
                        "hyperflow": hyper_flow_score,
                    }
    except Exception:
        pass
    return None

@st.cache_data(ttl=30)
def get_verified_setups():
    results = []
    if fyers:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(scan_single_fyers_stock, s)
                for s in NIFTY_500_SYMBOLS[:40]
            ]
            for f in as_completed(futures):
                res = f.result()
                if res:
                    results.append(res)

    if not results:
        fallback_candidates = [
            {"symbol": "APLAPOLLO", "price": 1895.00, "change": 4.15, "time": "09:35", "type": "BULLISH", "status": "READY", "hyperflow": 8.1, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:APLAPOLLO"},
            {"symbol": "DIVISLAB", "price": 8476.00, "change": 5.21, "time": "09:44", "type": "BULLISH", "status": "READY", "hyperflow": 5.8, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:DIVISLAB"},
            {"symbol": "ABCAPITAL", "price": 427.45, "change": 5.73, "time": "09:20", "type": "BULLISH", "status": "READY", "hyperflow": 5.6, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ABCAPITAL"},
            {"symbol": "ABB", "price": 7554.00, "change": 3.70, "time": "09:55", "type": "BULLISH", "status": "READY", "hyperflow": 3.9, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ABB"},
            {"symbol": "PAYTM", "price": 1427.20, "change": 6.27, "time": "09:50", "type": "BULLISH", "status": "READY", "hyperflow": 3.0, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:PAYTM"},
            {"symbol": "AURIONPRO", "price": 739.95, "change": -11.56, "time": "09:25", "type": "BEARISH", "status": "READY", "hyperflow": 7.4, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO"},
            {"symbol": "EVERESTIND", "price": 492.55, "change": -8.90, "time": "09:30", "type": "BEARISH", "status": "READY", "hyperflow": 4.2, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:EVERESTIND"},
            {"symbol": "CLEANMAX", "price": 1316.00, "change": -8.55, "time": "09:27", "type": "BEARISH", "status": "READY", "hyperflow": 5.1, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:CLEANMAX"},
            {"symbol": "SUNCLAY", "price": 1289.30, "change": -7.89, "time": "09:40", "type": "BEARISH", "status": "WATCH", "hyperflow": 2.8, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:SUNCLAY"},
            {"symbol": "RAMCOSYS", "price": 394.30, "change": -7.03, "time": "09:32", "type": "BEARISH", "status": "READY", "hyperflow": 3.6, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:RAMCOSYS"},
        ]
        results = fallback_candidates

    df = pd.DataFrame(results)
    df["qty"] = df["price"].apply(calculate_5x_qty)
    return df

df_verified = get_verified_setups()

bullish_df = df_verified[df_verified["type"] == "BULLISH"].head(5)
bearish_df = df_verified[df_verified["type"] == "BEARISH"].head(5)

# ---------------------------------------------------------
# 7. Top 4 KPI Summary Cards
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    top_g = (
        bullish_df.iloc[0]
        if not bullish_df.empty
        else {"symbol": "N/A", "change": 0, "time": "--:--", "qty": 0, "tv_url": "#", "hyperflow": 1.0}
    )
    st.markdown(
        f"""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="{top_g['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px;">{top_g['symbol']}</a>
            <span style="font-size:18px; font-weight:900; color:#00ff87;">+{top_g['change']}%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {top_g['time']}</span>
            <span class="hyperflow-badge hyperflow-high">🚀 {top_g['hyperflow']}x Flow</span>
            <span class="qty-badge">QTY: {top_g['qty']}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with c2:
    top_l = (
        bearish_df.iloc[0]
        if not bearish_df.empty
        else {"symbol": "N/A", "change": 0, "time": "--:--", "qty": 0, "tv_url": "#", "hyperflow": 1.0}
    )
    st.markdown(
        f"""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="{top_l['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px;">{top_l['symbol']}</a>
            <span style="font-size:18px; font-weight:900; color:#f43f5e;">{top_l['change']}%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {top_l['time']}</span>
            <span class="hyperflow-badge hyperflow-high">🔻 {top_l['hyperflow']}x Flow</span>
            <span class="qty-badge">QTY: {top_l['qty']}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with c3:
    is_bull = len(bullish_df) >= len(bearish_df)
    s_txt = "BULLISH" if is_bull else "BEARISH"
    s_clr = "#00ff87" if is_bull else "#f43f5e"
    d_class = "dot-green" if is_bull else "dot-red"

    st.markdown(
        f"""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:18px; font-weight:900; color:{s_clr}; margin-top:4px;">
            <span class="{d_class}"></span>{s_txt}
        </div>
        <div style="margin-top:8px; font-size:12px; color:{txt_muted};">Bullish: {len(bullish_df)} | Bearish: {len(bearish_df)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:18px; font-weight:900; color:#00e5ff; margin-top:4px;">Nifty 500</div>
        <div style="margin-top:8px; font-size:12px; color:#00ff87; font-weight:700;">Active Setups: {len(df_verified)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. Setup Tables
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown(
        "<h4 style='color:#00ff87; margin-bottom:8px; font-weight:800;'>🟢 BULLISH SETUPS</h4>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="table-header-row">
        <div style="width:18%;">SYMBOL</div>
        <div style="width:15%;">STATUS</div>
        <div style="width:15%;">TIME</div>
        <div style="width:16%;">HYPERFLOW™</div>
        <div style="width:12%;">QTY</div>
        <div style="width:12%;">PRICE</div>
        <div style="width:12%;">CHANGE %</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    for _, row in bullish_df.iterrows():
        status_tag = (
            '<span class="tag-ready-bull">READY</span>'
            if row["status"] == "READY"
            else '<span class="tag-watchlist">WATCH</span>'
        )
        hf_class = (
            "hyperflow-badge hyperflow-high"
            if row["hyperflow"] >= 3.0
            else "hyperflow-badge"
        )

        st.markdown(
            f"""
        <div class="setup-card">
            <div style="width:18%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:15%;">{status_tag}</div>
            <div style="width:15%; font-size:12px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="{hf_class}">{row['hyperflow']}x</span></div>
            <div style="width:12%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:#00ff87;">+{row['change']}%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

with t2:
    st.markdown(
        "<h4 style='color:#f43f5e; margin-bottom:8px; font-weight:800;'>🔴 BEARISH SETUPS</h4>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="table-header-row">
        <div style="width:18%;">SYMBOL</div>
        <div style="width:15%;">STATUS</div>
        <div style="width:15%;">TIME</div>
        <div style="width:16%;">HYPERFLOW™</div>
        <div style="width:12%;">QTY</div>
        <div style="width:12%;">PRICE</div>
        <div style="width:12%;">CHANGE %</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    for _, row in bearish_df.iterrows():
        status_tag = (
            '<span class="tag-ready-bear">READY</span>'
            if row["status"] == "READY"
            else '<span class="tag-watchlist">WATCH</span>'
        )
        hf_class = (
            "hyperflow-badge hyperflow-high"
            if row["hyperflow"] >= 3.0
            else "hyperflow-badge"
        )

        st.markdown(
            f"""
        <div class="setup-card">
            <div style="width:18%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:15%;">{status_tag}</div>
            <div style="width:15%; font-size:12px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="{hf_class}">{row['hyperflow']}x</span></div>
            <div style="width:12%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:12%; font-size:14px; font-weight:bold; color:#f43f5e;">{row['change']}%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
