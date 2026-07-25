import streamlit as st
import pandas as pd
import yfinance as yf
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hira Mount Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR EXACT ORIGINAL DASHBOARD UI ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e1e3e6; }
    
    /* Top Index Cards */
    .index-card {
        background-color: #141824;
        border: 1px solid #232838;
        border-radius: 6px;
        padding: 8px 12px;
        text-align: center;
        transition: 0.2s;
    }
    .index-card:hover { border-color: #3b82f6; }
    .index-title { color: #8b949e; font-size: 11px; font-weight: 600; }
    .index-price { font-size: 15px; font-weight: bold; color: #ffffff; }
    .price-up { color: #10b981; font-size: 11px; font-weight: 600; }
    .price-down { color: #ef4444; font-size: 11px; font-weight: 600; }
    
    /* Summary Metric Cards */
    .metric-card {
        background-color: #141824;
        border: 1px solid #232838;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 11px; color: #8b949e; font-weight: 700; text-transform: uppercase; }
    .metric-val { font-size: 18px; font-weight: bold; margin-top: 4px; }
    
    /* Table & Container Styling */
    .setup-box {
        background-color: #141824;
        border: 1px solid #232838;
        border-radius: 8px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- STRICT F&O BLACKLIST ---
FNO_STOCKS = {
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS",
    "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL",
    "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE",
    "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT",
    "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BSOFT", "BPCL", "BRITANNIA", "CANBK",
    "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL",
    "CONCOR", "COROMANDEL", "CROMPTON", "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR",
    "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK",
    "FACT", "FORMAPHC", "GAIL", "GLENMARK", "GMMPFAUDLR", "GMRINFRA", "GNFC", "GODREJPROP",
    "GRANULES", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK",
    "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR",
    "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL",
    "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC",
    "IRFC", "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KALYANKJIL", "KEI",
    "KOTAKBANK", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LTIM", "LT", "LTF", "LTSH",
    "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCX", "METROPOLIS",
    "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI",
    "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "OIL", "ONGC",
    "PAGEIND", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB",
    "POWERGRID", "PRESTIGE", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE",
    "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SJS",
    "SRF", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACOMM", "TATACONSUM", "TATEL", "TATAMOTORS",
    "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT",
    "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "YESBANK", "ZEEL"
}

# --- HEADER TITLE & CLICKABLE INDICES ---
st.markdown("### 📈 HIRA MOUNT TRADER")

@st.cache_data(ttl=120)
def fetch_indices():
    indices = {
        "NIFTY 50": {"ticker": "^NSEI", "tv": "NSE:NIFTY"},
        "BANK NIFTY": {"ticker": "^NSEBANK", "tv": "NSE:BANKNIFTY"},
        "SENSEX": {"ticker": "^BSESN", "tv": "BSE:SENSEX"},
        "NIFTY MIDCAP": {"ticker": "NIFTY_MIDCAP_100.NS", "tv": "NSE:NIFTY_MIDCAP_100"}
    }
    data = {}
    for name, info in indices.items():
        try:
            t = yf.Ticker(info["ticker"])
            hist = t.history(period="2d")
            if len(hist) >= 2:
                curr = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = curr - prev
                p_change = (change / prev) * 100
                data[name] = {
                    "price": f"{curr:,.2f}",
                    "change": f"{change:+,.2f}",
                    "p_change": f"{p_change:+.2f}%",
                    "is_up": change >= 0,
                    "tv_link": f"https://www.tradingview.com/chart/?symbol={info['tv']}"
                }
            else: data[name] = None
        except: data[name] = None
    return data

indices_data = fetch_indices()
idx_cols = st.columns(4)

for idx, (name, details) in enumerate(indices_data.items()):
    with idx_cols[idx]:
        if details:
            cls = "price-up" if details["is_up"] else "price-down"
            arrow = "▲" if details["is_up"] else "▼"
            st.markdown(f"""
            <a href="{details['tv_link']}" target="_blank" style="text-decoration: none;">
                <div class="index-card">
                    <div class="index-title">{name} 🔗</div>
                    <div class="index-price">{details['price']}</div>
                    <div class="{cls}">{arrow} {details['change']} ({details['p_change']})</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='index-card'><div class='index-title'>{name}</div><div class='index-price'>--</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- FILE INPUT / CSV PROCESSING ---
CSV_FILE = "Stock Screener.csv"
if not os.path.exists(CSV_FILE):
    CSV_FILE = "Hira Stocks.csv"

df_raw = None
if os.path.exists(CSV_FILE):
    df_raw = pd.read_csv(CSV_FILE)
else:
    uploaded = st.file_uploader("Upload Chartink CSV File", type=["csv"])
    if uploaded:
        df_raw = pd.read_csv(uploaded)

if df_raw is not None:
    df_raw.columns = df_raw.columns.str.strip()
    
    # Identify symbol column
    sym_col = [c for c in ['Symbol', 'NSE Symbol', 'Ticker', 'Stock Name'] if c in df_raw.columns]
    symbol_col = sym_col[0] if sym_col else df_raw.columns[0]
    
    df_raw['Clean_Symbol'] = df_raw[symbol_col].astype(str).str.upper().str.strip()
    
    # 🚫 Pure Cash Filter (F&O Removal)
    pure_cash = df_raw[~df_raw['Clean_Symbol'].isin(FNO_STOCKS)].copy()
    
    # Standardize column names for UI
    close_col = [c for c in df_raw.columns if 'close' in c.lower() or 'price' in c.lower()]
    chg_col = [c for c in df_raw.columns if 'change' in c.lower() or 'return' in c.lower()]
    
    p_col = close_col[0] if close_col else df_raw.columns[1]
    c_col = chg_col[0] if chg_col else df_raw.columns[2]

    # Calculate Top Metrics
    top_gainer = pure_cash.sort_values(by=c_col, ascending=False).iloc[0] if len(pure_cash) > 0 else None
    top_loser = pure_cash.sort_values(by=c_col, ascending=True).iloc[0] if len(pure_cash) > 0 else None
    bullish_count = len(pure_cash[pure_cash[c_col] > 0])
    bearish_count = len(pure_cash[pure_cash[c_col] < 0])

    # --- TOP METRICS CARDS (EXACT MATCH TO PHOTO) ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TOP GAINER</div>
            <div class="metric-val" style="color: #10b981;">{top_gainer['Clean_Symbol'] if top_gainer is not None else '--'}</div>
            <div class="price-up">+{top_gainer[c_col]}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TOP LOSER</div>
            <div class="metric-val" style="color: #ef4444;">{top_loser['Clean_Symbol'] if top_loser is not None else '--'}</div>
            <div class="price-down">{top_loser[c_col]}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        sentiment = "🟢 Bullish" if bullish_count >= bearish_count else "🔴 Bearish"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MARKET SENTIMENT</div>
            <div class="metric-val">{sentiment}</div>
            <div style="font-size: 11px; color: #8b949e;">Bullish: {bullish_count} | Bearish: {bearish_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">SCANNED STOCKS</div>
            <div class="metric-val" style="color: #3b82f6;">{len(pure_cash)} Pure Cash</div>
            <div style="font-size: 11px; color: #10b981;">F&O Excluded Automatically</div>
        </div>
        """, unsafe_allow_html=True)

    # --- BULLISH & BEARISH TABLES (SIDE BY SIDE LAYOUT) ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_bull, col_bear = st.columns(2)

    with col_bull:
        st.markdown("<h4 style='color: #10b981;'>🟢 BULLISH SETUPS</h4>", unsafe_allow_html=True)
        bull_df = pure_cash[pure_cash[c_col] >= 0].sort_values(by=c_col, ascending=False).drop(columns=['Clean_Symbol'])
        st.dataframe(bull_df, use_container_width=True, hide_index=True, height=450)

    with col_bear:
        st.markdown("<h4 style='color: #ef4444;'>🔴 BEARISH SETUPS</h4>", unsafe_allow_html=True)
        bear_df = pure_cash[pure_cash[c_col] < 0].sort_values(by=c_col, ascending=True).drop(columns=['Clean_Symbol'])
        st.dataframe(bear_df, use_container_width=True, hide_index=True, height=450)

else:
    st.info(" Please place `Stock Screener.csv` or `Hira Stocks.csv` in the folder or upload it above.")
