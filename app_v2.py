import streamlit as st
import pandas as pd
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hira Mount Trader Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR HIGH PERFORMANCE & MODERN UI ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .index-card {
        background-color: #1a1c24;
        border: 1px solid #2d313e;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
        text-decoration: none !important;
        display: block;
        margin-bottom: 10px;
    }
    .index-card:hover {
        border-color: #00d47e;
        transform: translateY(-2px);
    }
    .index-title { color: #8a8f9d; font-size: 13px; font-weight: 600; margin-bottom: 2px; }
    .index-price { font-size: 16px; font-weight: bold; color: #ffffff; }
    .price-up { color: #00d47e; font-weight: 600; font-size: 13px; }
    .price-down { color: #ff4b4b; font-weight: 600; font-size: 13px; }
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

# --- FETCH INDEX DATA ---
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
            hist = t.history(period="5d")
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
            else:
                data[name] = None
        except Exception as e:
            data[name] = None
    return data

# --- HEADER INDEX CARDS ---
indices_data = fetch_indices()

col1, col2, col3, col4 = st.columns(4)
cols = [col1, col2, col3, col4]

for idx, (name, details) in enumerate(indices_data.items()):
    with cols[idx]:
        if details:
            cls = "price-up" if details["is_up"] else "price-down"
            arrow = "▲" if details["is_up"] else "▼"
            html_code = f"""
            <a href="{details['tv_link']}" target="_blank" style="text-decoration: none;">
                <div class="index-card">
                    <div class="index-title">{name} 🔗</div>
                    <div class="index-price">{details['price']}</div>
                    <div class="{cls}">{arrow} {details['change']} ({details['p_change']})</div>
                </div>
            </a>
            """
            st.markdown(html_code, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <a href="https://www.tradingview.com/chart/" target="_blank" style="text-decoration: none;">
                <div class="index-card">
                    <div class="index-title">{name} 🔗</div>
                    <div class="index-price">Market Live</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

st.divider()

# --- MAIN TERMINAL ---
st.title("⚡ HIRA MOUNT TRADER")
st.caption("Pure Cash Momentum Screener Terminal")

# --- FILE UPLOADER & PROCESSING ---
uploaded_file = st.file_uploader("📥 Upload your Chartink CSV File (Stock Screener.csv)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        
        symbol_col = None
        for col in ['Symbol', 'NSE Symbol', 'Ticker', 'Stock Name']:
            if col in df.columns:
                symbol_col = col
                break
                
        if symbol_col is None:
            symbol_col = df.columns[0]
            
        df['Clean_Symbol'] = df[symbol_col].astype(str).str.upper().str.strip()
        
        # Filter F&O
        pure_cash_df = df[~df['Clean_Symbol'].isin(FNO_STOCKS)].copy()
        fno_count = len(df) - len(pure_cash_df)
        
        st.success(f"📊 Total Stocks in File: **{len(df)}** | ❌ F&O Removed: **{fno_count}** | ✅ **Pure Cash Active: {len(pure_cash_df)}**")
        
        # Manual Dismiss Box
        stocks_list = pure_cash_df['Clean_Symbol'].tolist()
        dismissed = st.multiselect("🚫 Remove any stock manually from list:", stocks_list)
        
        final_df = pure_cash_df[~pure_cash_df['Clean_Symbol'].isin(dismissed)].drop(columns=['Clean_Symbol'])
        
        st.dataframe(
            final_df,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👆 Please upload your downloaded `Stock Screener.csv` file using the button above to load the terminal data.")
