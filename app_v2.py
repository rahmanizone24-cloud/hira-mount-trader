import streamlit as st
import pandas as pd
import numpy as np
import datetime
import pytz

# ---------------------------------------------------------
# 1. Page Config & Session Theme Management
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed")

if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Dark'

def toggle_theme():
    st.session_state['theme_mode'] = 'Light' if st.session_state['theme_mode'] == 'Dark' else 'Dark'

# Auto-Refresh Every 30 Seconds (Smooth Background Refresh)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_mount_autorefresh")
except ImportError:
    pass

# Dynamic Theme CSS Configuration
if st.session_state['theme_mode'] == 'Dark':
    bg_app = "#06090e"
    bg_card = "#0f172a"
    border_clr = "#1e293b"
    txt_main = "#f8fafc"
    txt_muted = "#94a3b8"
    badge_bg = "#1e293b"
else:
    bg_app = "#f1f5f9"
    bg_card = "#ffffff"
    border_clr = "#cbd5e1"
    txt_main = "#0f172a"
    txt_muted = "#64748b"
    badge_bg = "#e2e8f0"

st.markdown(f"""
<style>
    .main .block-container {{
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.8rem !important;
    }}
    
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    
    /* Top Navigation Header */
    .top-bar-container {{
        background-color: {bg_card};
        padding: 8px 16px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {border_clr};
        margin-bottom: 15px;
    }}
    
    .brand-title {{ font-size: 20px; font-weight: 900; color: #00e5ff; letter-spacing: 0.5px; white-space: nowrap; }}
    
    .index-badge {{
        background: {badge_bg};
        color: {txt_muted};
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        text-decoration: none;
        border: 1px solid {border_clr};
        font-weight: 700;
        white-space: nowrap;
    }}
    
    /* Soft Dot Only Blink Animation */
    @keyframes dotGlow {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.3; transform: scale(0.9); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .dot-blink-green {{ display: inline-block; width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; animation: dotGlow 2s infinite; margin-right: 5px; }}
    .dot-blink-red {{ display: inline-block; width: 8px; height: 8px; background-color: #f43f5e; border-radius: 50%; animation: dotGlow 2s infinite; margin-right: 5px; }}

    /* KPI Summary Stat Boxes */
    .stat-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }}
    .stat-title {{ font-size: 11px; color: {txt_muted}; font-weight: bold; letter-spacing: 0.5px; }}
    
    /* Market Movers Card */
    .mover-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }}
    
    /* Table Column Header */
    .table-header-row {{
        display: flex;
        justify-content: space-between;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: 800;
        color: {txt_muted};
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }}

    /* Boxed Grid Trading Setups */
    .setup-card {{
        background-color: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .stock-title-link {{ font-size: 16px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: #7dd3fc; }}
    
    .qty-badge {{
        background-color: {badge_bg};
        border: 1px solid {border_clr};
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        color: {txt_main};
        display: inline-block;
    }}
    
    .tag-ready-bull {{ background-color: #065f46; color: #34d399; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }}
    .tag-ready-bear {{ background-color: #9f1239; color: #fecdd3; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 800; }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Timezone & Market Status Calculation
# ---------------------------------------------------------
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(ist)

market_open_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_ist.weekday() < 5
is_market_hours = market_open_time <= now_ist <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span style="background:#064e3b; color:#34d399; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-blink-green"></span>OPEN</span>'
else:
    market_status_html = '<span style="background:#881337; color:#fecdd3; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-blink-red"></span>CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")

# ---------------------------------------------------------
# 3. Top Navigation Header Layout
# ---------------------------------------------------------
col_top1, col_top_theme, col_top_ref = st.columns([10, 1, 1])

with col_top1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge">NIFTY 50: <b style="color:#10b981;">24,199.60 (+0.85%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge">BANK NIFTY: <b style="color:#10b981;">57,096.50 (+0.02%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge">SENSEX: <b style="color:#10b981;">79,486.20 (+0.78%)</b></a>
        {market_status_html}
        <span class="index-badge" style="color:#38bdf8;">🕒 {time_str}</span>
    </div>
    """, unsafe_allow_html=True)

with col_top_theme:
    theme_label = "☀️ Light" if st.session_state['theme_mode'] == 'Dark' else "🌙 Dark"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

with col_top_ref:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------
# 4. Strict 10-Min Pause Candle Breakout Screener Logic
# ---------------------------------------------------------
def run_pause_candle_screener():
    # Structural candles dataset (Simulating 5-min candles live feed)
    raw_market_feed = [
        # Stock 1: Valid Bullish Setup
        {
            "symbol": "ASHIKA", "price": 690.30, "change": 14.12, "qty": 101, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ASHIKA",
            "c1_close": 680, "ema20": 670, "ema200": 650, "c1_high": 682, "c1_low": 675, # Range: 7 Rs (< 1.5% of 680)
            "c2_open": 678, "c2_close": 680, "c2_high": 681, "c2_low": 676, # Inside Candle (No High/Low Break)
            "c3_high": 685, "c3_vol_surge": True, "trigger_time": "09:25", "type": "BULLISH"
        },
        # Stock 2: Valid Bullish Setup
        {
            "symbol": "KNEW", "price": 2724.80, "change": 12.23, "qty": 33, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:KNEW",
            "c1_close": 2700, "ema20": 2680, "ema200": 2600, "c1_high": 2710, "c1_low": 2695, # Range < 1.5%
            "c2_open": 2702, "c2_close": 2705, "c2_high": 2708, "c2_low": 2698, # Inside Candle
            "c3_high": 2715, "c3_vol_surge": True, "trigger_time": "09:25", "type": "BULLISH"
        },
        # Stock 3: Valid Bearish Setup
        {
            "symbol": "AURIONPRO", "price": 739.95, "change": -11.56, "qty": 67, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO",
            "c1_close": 750, "ema20": 760, "ema200": 780, "c1_high": 755, "c1_low": 748, # Below EMAs, Range < 1.5%
            "c2_open": 752, "c2_close": 750, "c2_high": 754, "c2_low": 749, # Inside Candle
            "c3_low": 745, "c3_vol_surge": True, "trigger_time": "09:25", "type": "BEARISH"
        },
        # Stock 4: Valid Bearish Setup
        {
            "symbol": "EVERESTIND", "price": 492.55, "change": -8.90, "qty": 141, "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:EVERESTIND",
            "c1_close": 500, "ema20": 510, "ema200": 530, "c1_high": 503, "c1_low": 498, # Range < 1.5%
            "c2_open": 501, "c2_close": 499, "c2_high": 502, "c2_low": 499, # Inside Candle
            "c3_low": 495, "c3_vol_surge": True, "trigger_time": "09:30", "type": "BEARISH"
        },
        # Invalid Stock Example (Filtered Out: First Candle > 1.5% Range)
        {
            "symbol": "INVALID_STOCK", "price": 100.0, "change": 5.0, "qty": 500, "tv_url": "",
            "c1_close": 100, "ema20": 90, "ema200": 80, "c1_high": 105, "c1_low": 98, # Range 7% (> 1.5%) -> FILTERED OUT
            "c2_open": 100, "c2_close": 101, "c2_high": 102, "c2_low": 99,
            "c3_high": 108, "c3_vol_surge": True, "trigger_time": "09:25", "type": "BULLISH"
        }
    ]

    filtered_list = []
    
    for item in raw_market_feed:
        # Check Candle 1 Range <= 1.5%
        c1_range_pct = ((item['c1_high'] - item['c1_low']) / item['c1_close']) * 100
        if c1_range_pct > 1.5:
            continue # Fail Rule 1
            
        # Check Candle 2 Inside Candle Rule
        c2_inside = (item['c2_high'] <= item['c1_high']) and (item['c2_low'] >= item['c1_low'])
        if not c2_inside:
            continue # Fail Rule 2
            
        # Check Bullish Rules
        if item['type'] == 'BULLISH':
            ema_valid = (item['c1_close'] > item['ema20']) and (item['c1_close'] > item['ema200'])
            breakout_valid = (item['c3_high'] > item['c1_high']) and item['c3_vol_surge']
            if ema_valid and breakout_valid:
                filtered_list.append(item)
                
        # Check Bearish Rules
        elif item['type'] == 'BEARISH':
            ema_valid = (item['c1_close'] < item['ema20']) and (item['c1_close'] < item['ema200'])
            breakout_valid = (item['c3_low'] < item['c1_low']) and item['c3_vol_surge']
            if ema_valid and breakout_valid:
                filtered_list.append(item)

    return pd.DataFrame(filtered_list)

df_filtered = run_pause_candle_screener()

# ---------------------------------------------------------
# 5. Top KPI Summary Cards
# ---------------------------------------------------------
bullish_df = df_filtered[df_filtered['type'] == 'BULLISH'] if not df_filtered.empty else pd.DataFrame()
bearish_df = df_filtered[df_filtered['type'] == 'BEARISH'] if not df_filtered.empty else pd.DataFrame()

top_gainer = bullish_df.iloc[0] if not bullish_df.empty else None
top_loser = bearish_df.iloc[0] if not bearish_df.empty else None

c1, c2, c3, c4 = st.columns(4)

with c1:
    sym = top_gainer['symbol'] if top_gainer is not None else "N/A"
    chg = f"+{top_gainer['change']}%" if top_gainer is not None else "0%"
    t_time = top_gainer['trigger_time'] if top_gainer is not None else "--:--"
    qty_val = top_gainer['qty'] if top_gainer is not None else 0
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <span class="stock-title-link" style="font-size:18px;">{sym}</span>
            <span style="font-size:18px; font-weight:900; color:#10b981;">{chg}</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {t_time}</span>
            <span class="qty-badge">{qty_val}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    sym = top_loser['symbol'] if top_loser is not None else "N/A"
    chg = f"{top_loser['change']}%" if top_loser is not None else "0%"
    t_time = top_loser['trigger_time'] if top_loser is not None else "--:--"
    qty_val = top_loser['qty'] if top_loser is not None else 0
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <span class="stock-title-link" style="font-size:18px; color:#f43f5e;">{sym}</span>
            <span style="font-size:18px; font-weight:900; color:#f43f5e;">{chg}</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {t_time}</span>
            <span class="qty-badge">{qty_val}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    is_bullish_sentiment = len(bullish_df) >= len(bearish_df)
    sent_text = "BULLISH" if is_bullish_sentiment else "BEARISH"
    sent_color = "#10b981" if is_bullish_sentiment else "#f43f5e"
    dot_class = "dot-blink-green" if is_bullish_sentiment else "dot-blink-red"
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">MARKET SENTIMENT</div>
        <div style="font-size:18px; font-weight:900; color:{sent_color}; margin-top:4px;">
            <span class="{dot_class}"></span>{sent_text}
        </div>
        <div style="margin-top:8px; font-size:12px; color:{txt_muted};">Bullish: {len(bullish_df)} | Bearish: {len(bearish_df)}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:18px; font-weight:900; color:#00e5ff; margin-top:4px;">500 Stocks</div>
        <div style="margin-top:8px; font-size:12px; color:#10b981; font-weight:700;">Active Setups: {len(df_filtered)}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 🔥 CENTERED MARKET MOVERS (4 Bullish + 4 Bearish Cards)
# ---------------------------------------------------------
st.markdown("<h3 style='text-align:center; margin-top:10px; margin-bottom:15px; font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)

m_cols = st.columns(8)

top_movers_df = pd.concat([bullish_df.head(4), bearish_df.head(4)]) if not df_filtered.empty else pd.DataFrame()

if not top_movers_df.empty:
    for idx, (_, item) in enumerate(top_movers_df.iterrows()):
        if idx < 8:
            with m_cols[idx]:
                clr = "#10b981" if item['change'] > 0 else "#f43f5e"
                sgn = "+" if item['change'] > 0 else ""
                st.markdown(f"""
                <div class="mover-box">
                    <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="font-size:14px;">{item['symbol']}</a><br>
                    <div style="font-size:13px; color:{clr}; font-weight:bold; margin-top:2px;">₹{item['price']}</div>
                    <div style="font-size:11px; color:{clr}; font-weight:bold;">({sgn}{item['change']}%)</div>
                    <div style="margin-top:4px;"><span class="qty-badge">{item['qty']}</span></div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. Bullish & Bearish Trading Setup Tables
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#10b981; margin-bottom:10px; font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not bullish_df.empty:
        for _, row in bullish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:18%;"><span class="tag-ready-bull">READY</span></div>
                <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['trigger_time']}</div>
                <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
                <div style="width:14%; font-size:15px; font-weight:bold; color:#10b981;">+{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("فلٹریشن کی کنڈیشنز کے مطابق فی الحال کوئی Bullish سیٹ اپ نہیں بنا ہے۔")

with t2:
    st.markdown("<h4 style='color:#f43f5e; margin-bottom:10px; font-weight:800;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="table-header-row">
        <div style="width:20%;">SYMBOL</div>
        <div style="width:18%;">STATUS</div>
        <div style="width:18%;">TRIGGER TIME</div>
        <div style="width:16%;">QTY</div>
        <div style="width:14%;">PRICE</div>
        <div style="width:14%;">CHANGE %</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not bearish_df.empty:
        for _, row in bearish_df.iterrows():
            st.markdown(f"""
            <div class="setup-card">
                <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
                <div style="width:18%;"><span class="tag-ready-bear">READY</span></div>
                <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['trigger_time']}</div>
                <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
                <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
                <div style="width:14%; font-size:15px; font-weight:bold; color:#f43f5e;">{row['change']}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("فلٹریشن کی کنڈیشنز کے مطابق فی الحال کوئی Bearish سیٹ اپ نہیں بنا ہے۔")
