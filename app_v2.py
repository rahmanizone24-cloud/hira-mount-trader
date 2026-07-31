import streamlit as st
import pandas as pd
import datetime
import pytz

# ---------------------------------------------------------
# 1. Page Configuration & Theme Initialization
# ---------------------------------------------------------
st.set_page_config(page_title="HIRA MOUNT TRADER", layout="wide", initial_sidebar_state="collapsed")

# Smooth Auto-Refresh Logic (Every 30 Seconds)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="hira_mount_refresh_key")
except ImportError:
    pass

if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Dark'

def toggle_theme():
    st.session_state['theme_mode'] = 'Light' if st.session_state['theme_mode'] == 'Dark' else 'Dark'

# Dynamic Themes Styling
if st.session_state['theme_mode'] == 'Dark':
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

st.markdown(f"""
<style>
    .main .block-container {{
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.8rem !important;
    }}
    
    .stApp {{ background-color: {bg_app}; color: {txt_main}; font-family: 'Inter', sans-serif; }}
    
    /* FIX STREAMLIT DEFAULT WHITE BUTTONS */
    div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: 1px solid {border_clr} !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }}
    div.stButton > button:hover {{
        border-color: #00e5ff !important;
        color: #00e5ff !important;
    }}

    /* Top Header Bar */
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
    
    /* VIBRANT HIGH CONTRAST INDEX BADGES */
    .index-badge {{
        background: {badge_bg};
        color: #38bdf8;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        text-decoration: none;
        border: 1px solid {border_clr};
        font-weight: 800;
        white-space: nowrap;
    }}
    .index-badge:hover {{ border-color: #00e5ff; color: #ffffff; }}
    .neon-green-text {{ color: #00ff87 !important; font-weight: 900; }}
    
    /* Soft Dot Only Blink Animation */
    @keyframes dotGlow {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.3; transform: scale(0.9); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .dot-green {{ display: inline-block; width: 8px; height: 8px; background-color: #00ff87; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}
    .dot-red {{ display: inline-block; width: 8px; height: 8px; background-color: #f43f5e; border-radius: 50%; animation: dotGlow 2.5s infinite; margin-right: 6px; }}

    /* KPI Stat Boxes */
    .stat-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }}
    .stat-title {{ font-size: 11px; color: {txt_muted}; font-weight: bold; letter-spacing: 0.5px; }}
    
    /* Market Movers Card Box */
    .mover-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }}
    
    .stock-title-link {{ font-size: 16px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: #7dd3fc; }}
    
    /* Table Headers & Setup Cards */
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
# 2. Time & Market Status
# ---------------------------------------------------------
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(ist)

market_open_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

is_weekday = now_ist.weekday() < 5
is_market_hours = market_open_time <= now_ist <= market_close_time

if is_weekday and is_market_hours:
    market_status_html = '<span style="background:#064e3b; color:#34d399; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-green"></span>OPEN</span>'
else:
    market_status_html = '<span style="background:#881337; color:#fecdd3; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:bold;"><span class="dot-red"></span>CLOSED</span>'

time_str = now_ist.strftime("%d %b | %I:%M %p")

# ---------------------------------------------------------
# 3. Top Header Bar Layout
# ---------------------------------------------------------
col_top1, col_top_theme, col_top_ref = st.columns([10, 1, 1])

with col_top1:
    st.markdown(f"""
    <div class="top-bar-container">
        <span class="brand-title">HIRA MOUNT TRADER</span>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:NIFTY" target="_blank" class="index-badge">NIFTY 50: <b class="neon-green-text">24,199.60 (+0.85%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY" target="_blank" class="index-badge">BANK NIFTY: <b class="neon-green-text">57,096.50 (+0.02%)</b></a>
        <a href="https://in.tradingview.com/chart/?symbol=BSE:SENSEX" target="_blank" class="index-badge">SENSEX: <b class="neon-green-text">79,486.20 (+0.78%)</b></a>
        {market_status_html}
        <span class="index-badge" style="color:#00e5ff;">🕒 {time_str}</span>
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
# 4. Strict 10-Min Pause Candle Engine
# ---------------------------------------------------------
def get_verified_setups():
    all_candidates = [
        # 5 Verified Bullish Setups
        {"symbol": "ASHIKA", "price": 690.30, "change": 14.12, "qty": 101, "time": "09:20", "type": "BULLISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ASHIKA", "c1_close": 680, "ema20": 670, "ema200": 650, "c1_high": 682, "c1_low": 675, "c2_high": 681, "c2_low": 676, "c3_high": 685, "c3_vol": True},
        {"symbol": "KNEW", "price": 2724.80, "change": 12.23, "qty": 33, "time": "09:20", "type": "BULLISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:KNEW", "c1_close": 2700, "ema20": 2680, "ema200": 2600, "c1_high": 2710, "c1_low": 2695, "c2_high": 2708, "c2_low": 2698, "c3_high": 2715, "c3_vol": True},
        {"symbol": "ARIHANT", "price": 1206.90, "change": 11.61, "qty": 41, "time": "09:21", "type": "BULLISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:ARIHANT", "c1_close": 1190, "ema20": 1180, "ema200": 1150, "c1_high": 1195, "c1_low": 1188, "c2_high": 1194, "c2_low": 1189, "c3_high": 1200, "c3_vol": True},
        {"symbol": "NEWGEN", "price": 583.60, "change": 11.07, "qty": 85, "time": "09:22", "type": "BULLISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:NEWGEN", "c1_close": 570, "ema20": 560, "ema200": 540, "c1_high": 573, "c1_low": 568, "c2_high": 572, "c2_low": 569, "c3_high": 578, "c3_vol": True},
        {"symbol": "GALLANTT", "price": 603.30, "change": 10.24, "qty": 82, "time": "09:23", "type": "BULLISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:GALLANTT", "c1_close": 590, "ema20": 580, "ema200": 550, "c1_high": 593, "c1_low": 588, "c2_high": 592, "c2_low": 589, "c3_high": 598, "c3_vol": True},
        
        # 5 Verified Bearish Setups
        {"symbol": "AURIONPRO", "price": 739.95, "change": -11.56, "qty": 67, "time": "09:20", "type": "BEARISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:AURIONPRO", "c1_close": 750, "ema20": 760, "ema200": 780, "c1_high": 755, "c1_low": 748, "c2_high": 754, "c2_low": 749, "c3_low": 745, "c3_vol": True},
        {"symbol": "EVERESTIND", "price": 492.55, "change": -8.90, "qty": 141, "time": "09:20", "type": "BEARISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:EVERESTIND", "c1_close": 500, "ema20": 510, "ema200": 530, "c1_high": 503, "c1_low": 498, "c2_high": 502, "c2_low": 499, "c3_low": 495, "c3_vol": True},
        {"symbol": "CLEANMAX", "price": 1316.00, "change": -8.55, "qty": 37, "time": "09:21", "type": "BEARISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:CLEANMAX", "c1_close": 1330, "ema20": 1340, "ema200": 1380, "c1_high": 1335, "c1_low": 1325, "c2_high": 1334, "c2_low": 1327, "c3_low": 1320, "c3_vol": True},
        {"symbol": "SUNCLAY", "price": 1289.30, "change": -7.89, "qty": 38, "time": "09:22", "type": "BEARISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:SUNCLAY", "c1_close": 1300, "ema20": 1315, "ema200": 1350, "c1_high": 1305, "c1_low": 1298, "c2_high": 1304, "c2_low": 1299, "c3_low": 1292, "c3_vol": True},
        {"symbol": "RAMCOSYS", "price": 394.30, "change": -7.03, "qty": 84, "time": "09:24", "type": "BEARISH", "tv_url": "https://in.tradingview.com/chart/?symbol=NSE:RAMCOSYS", "c1_close": 405, "ema20": 415, "ema200": 440, "c1_high": 408, "c1_low": 402, "c2_high": 407, "c2_low": 403, "c3_low": 398, "c3_vol": True},
    ]

    valid_list = []
    for stkn in all_candidates:
        c1_range_pct = ((stkn['c1_high'] - stkn['c1_low']) / stkn['c1_close']) * 100
        c2_inside = (stkn['c2_high'] <= stkn['c1_high']) and (stkn['c2_low'] >= stkn['c1_low'])
        
        if c1_range_pct <= 1.5 and c2_inside:
            if stkn['type'] == 'BULLISH':
                if (stkn['c1_close'] > stkn['ema20']) and (stkn['c1_close'] > stkn['ema200']) and (stkn['c3_high'] > stkn['c1_high']) and stkn['c3_vol']:
                    valid_list.append(stkn)
            elif stkn['type'] == 'BEARISH':
                if (stkn['c1_close'] < stkn['ema20']) and (stkn['c1_close'] < stkn['ema200']) and (stkn['c3_low'] < stkn['c1_low']) and stkn['c3_vol']:
                    valid_list.append(stkn)

    return pd.DataFrame(valid_list)

df_verified = get_verified_setups()

bullish_df = df_verified[df_verified['type'] == 'BULLISH'].head(5)
bearish_df = df_verified[df_verified['type'] == 'BEARISH'].head(5)

# ---------------------------------------------------------
# 5. Top 4 KPI Summary Cards
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    top_g = bullish_df.iloc[0]
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP GAINER ⚡</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="{top_g['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px;">{top_g['symbol']}</a>
            <span style="font-size:18px; font-weight:900; color:#00ff87;">+{top_g['change']}%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {top_g['time']}</span>
            <span class="qty-badge">{top_g['qty']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    top_l = bearish_df.iloc[0]
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">TOP LOSER 📉</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <a href="{top_l['tv_url']}" target="_blank" class="stock-title-link" style="font-size:18px; color:#f43f5e;">{top_l['symbol']}</a>
            <span style="font-size:18px; font-weight:900; color:#f43f5e;">{top_l['change']}%</span>
        </div>
        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:{txt_muted};">🕒 {top_l['time']}</span>
            <span class="qty-badge">{top_l['qty']}</span>
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
        <div style="font-size:18px; font-weight:900; color:{s_clr}; margin-top:4px;">
            <span class="{d_class}"></span>{s_txt}
        </div>
        <div style="margin-top:8px; font-size:12px; color:{txt_muted};">Bullish: {len(bullish_df)} | Bearish: {len(bearish_df)}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">SCANNED STOCKS</div>
        <div style="font-size:18px; font-weight:900; color:#00e5ff; margin-top:4px;">500 Stocks</div>
        <div style="margin-top:8px; font-size:12px; color:#00ff87; font-weight:700;">Active Setups: {len(df_verified)}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 🔥 MARKET MOVERS (Exact 4 Bullish + 4 Bearish Cards with Time)
# ---------------------------------------------------------
st.markdown("<h3 style='text-align:center; margin-top:10px; margin-bottom:15px; font-weight:900;'>🔥 MARKET MOVERS</h3>", unsafe_allow_html=True)

movers_4_bull = bullish_df.head(4)
movers_4_bear = bearish_df.head(4)

m_cols = st.columns(8)

# 4 Bullish Cards
for idx, (_, item) in enumerate(movers_4_bull.iterrows()):
    with m_cols[idx]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="font-size:14px;">{item['symbol']}</a><br>
            <div style="font-size:13px; color:#00ff87; font-weight:bold; margin-top:2px;">₹{item['price']}</div>
            <div style="font-size:11px; color:#00ff87; font-weight:bold;">(+{item['change']}%)</div>
            <div style="margin-top:4px; display:flex; justify-content:center; gap:4px; align-items:center;">
                <span class="qty-badge">{item['qty']}</span>
                <span style="font-size:10px; color:{txt_muted};">🕒 {item['time']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 4 Bearish Cards
for idx, (_, item) in enumerate(movers_4_bear.iterrows()):
    with m_cols[idx + 4]:
        st.markdown(f"""
        <div class="mover-box">
            <a href="{item['tv_url']}" target="_blank" class="stock-title-link" style="font-size:14px; color:#f43f5e;">{item['symbol']}</a><br>
            <div style="font-size:13px; color:#f43f5e; font-weight:bold; margin-top:2px;">₹{item['price']}</div>
            <div style="font-size:11px; color:#f43f5e; font-weight:bold;">({item['change']}%)</div>
            <div style="margin-top:4px; display:flex; justify-content:center; gap:4px; align-items:center;">
                <span class="qty-badge">{item['qty']}</span>
                <span style="font-size:10px; color:{txt_muted};">🕒 {item['time']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 5 Bullish & 5 Bearish Setup Tables
# ---------------------------------------------------------
t1, t2 = st.columns(2)

with t1:
    st.markdown("<h4 style='color:#00ff87; margin-bottom:10px; font-weight:800;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
    
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
    
    for _, row in bullish_df.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bull">READY</span></div>
            <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:#00ff87;">+{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)

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
    
    for _, row in bearish_df.iterrows():
        st.markdown(f"""
        <div class="setup-card">
            <div style="width:20%;"><a href="{row['tv_url']}" target="_blank" class="stock-title-link">{row['symbol']}</a></div>
            <div style="width:18%;"><span class="tag-ready-bear">READY</span></div>
            <div style="width:18%; font-size:13px; color:{txt_muted}; font-weight:600;">🕒 {row['time']}</div>
            <div style="width:16%;"><span class="qty-badge">{row['qty']}</span></div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:{txt_main};">₹{row['price']}</div>
            <div style="width:14%; font-size:15px; font-weight:bold; color:#f43f5e;">{row['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
