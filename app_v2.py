import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List

import pandas as pd
import pytz
import streamlit as st

# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HiraMountTrader")

# Fyers API
try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None
    logger.warning("fyers_apiv3 not installed")

# ---------------------------------------------------------
# 1. Page Config & Theme
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

st.markdown(f"""
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
        0% {{ opacity: 1; }} 50% {{ opacity: 0.35; }} 100% {{ opacity: 1; }}
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
    #MainMenu, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=
