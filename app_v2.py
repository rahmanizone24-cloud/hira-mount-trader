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
query_params = st.query_params

if "theme" not in st.session_state:
  st.session_state.theme = query_params.get("theme", "dark")

st.query_params["theme"] = st.session_state.theme

if st.session_state.theme == "dark":
  bg_color = "#0b0e14"
  card_bg = "#161b22"
  sub_card_bg = "#0d1117"
  border_color = "#30363d"
  text_main = "#f0f6fc"
  text_sub = "#8b949e"
  accent_blue = "#58a6ff"
  btn_bg = "#21262d"
else:
  bg_color = "#f6f8fa"
  card_bg = "#ffffff"
  sub_card_bg = "#f3f4f6"
  border_color = "#d0d7de"
  text_main = "#1f2328"
  text_sub = "#656d76"
  accent_blue = "#0969da"
  btn_bg = "#eaeef2"

# --- CUSTOM ENHANCED CSS ---
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
        div[data-testid="stSpinner"], .stSpinner {{
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }}
        
        /* BUTTONS */
        .stButton>button {{
            background-color: {btn_bg} !important; color: {accent_blue} !important; border: 1px solid {border_color} !important;
            border-radius: 6px !important; font-weight: 800 !important; font-size: 12px !important; padding: 2px 6px !important;
            transition: all 0.2s !important; min-height: 0px !important; height: 36px !important; width: 100% !important;
        }}
        .stButton>button:hover {{ border-color: {accent_blue} !important; color: {text_main} !important; }}
        
        /* TOP HEADER ENHANCED ALIGNMENT & BIGGER TEXT */
        .brand-logo {{
            font-size: 19px; font-weight: 900; color: {accent_blue} !important; letter-spacing: 0.5px;
            font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; white-space: nowrap; line-height: 36px;
        }}
        .indices-bar-wrapper {{
            display: flex; align-items: center; justify-content: flex-start; gap: 6px; width: 100%; height: 36px; overflow-x: auto;
        }}
        .idx-pill {{
            display: inline-flex; align-items: center; gap: 5px; background-color: {sub_card_bg}; border: 1.5px solid {border_color};
            border-radius: 6px; padding: 4px 8px; text-decoration: none !important; font-size: 12px; white-space: nowrap;
        }}
        .idx-lbl {{ color: {text_sub}; font-weight: 800; font-size: 11px; text-transform: uppercase; }}
        .idx-num {{ color: {text_main}; font-weight: 900; font-size: 13px; }}
        .idx-up-p {{ color: #3fb950; font-weight: 900; font-size: 12px; }}
        .idx-down-p {{ color: #f85149; font-weight: 900; font-size: 12px; }}
        
        .header-status-box {{ display: flex; align-items: center; justify-content: center; height: 36px; white-space: nowrap; }}
        .header-time-box {{ display: flex; align-items: center; justify-content: center; height: 36px; font-size: 11px; color: {text_sub}; font-weight: 800; white-space: nowrap; }}

        .market-status-open {{ background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1.5px solid rgba(63, 185, 80, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 900; }}
        .market-status-closed {{ background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1.5px solid rgba(248, 81, 73, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 900; }}
        
        /* EQUAL 4 TOP METRIC CARDS */
        .metric-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 12px 14px; height: 100%; box-sizing: border-box; min-height: 82px; display: flex; flex-direction: column; justify-content: center; }}
        .card-label {{ font-size: 11px; color: {text_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-value-green {{ font-size: 18px; font-weight: 900; color: #3fb950; margin-top: 3px; }}
        .card-value-red {{ font-size: 18px; font-weight: 900; color: #f85149; margin-top: 3px; }}
        
        .box-container {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-top: 10px; margin-bottom: 8px; }}
        .box-title {{ font-size: 14px; font-weight: 900; color: {text_main}; letter-spacing: 0.5px; }}
        
        /* MARKET MOVERS CARDS */
        .stock-card {{ background-color: {sub_card_bg}; border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px 12px; text-align: left; }}
        .stock-card-top {{ display: flex; justify-content: space-between; align-items: center; }}
        .stock-symbol {{ font-size: 14px; font-weight: 900; color: {accent_blue}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .stock-card-body {{ display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }}
        .stock-price-up {{ font-size: 15px; font-weight: 900; color: #3fb950; }}
        .stock-price-down {{ font-size: 15px; font-weight: 900; color: #f85149; }}
        .stock-meta {{ font-size: 11px; color: {text_sub}; font-weight: 700; text-align: right; }}
        
        /* TABLES & ROWS */
        .setup-box {{ background-color: {card_bg}; border: 1.5px solid {border_color}; border-radius: 10px; padding: 12px; }}
        .setup-header-bull {{ font-size: 16px; font-weight: 900; color: #3fb950; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .setup-header-bear {{ font-size: 16px; font-weight: 900; color: #f85149; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        
        .row-header {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; font-size: 11px; font-weight: 900; color: {text_sub}; text-transform: uppercase; border-bottom: 1px solid {border_color}; margin-bottom: 8px; }}
        .stock-row-item {{ display: flex; justify-content: space-between; align-items: center; background-color: {sub_card_bg}; border: 1px solid {border_color}; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; text-decoration: none !important; }}
        .sym-btn-box {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 5px; padding: 3px 8px; color: {accent_blue}; font-weight: 900; font-size: 13px; display: inline-block; }}
        
        .status-ready-bull {{ background-color: #006400; color: #FFFFFF; border: 1px solid #004d00; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .status-ready-bear {{ background-color: #8B0000; color: #FFFFFF; border: 1px solid #660000; border-radius: 5px; padding: 3px 8px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .vol-box {{ background-color: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); border-radius: 5px; padding: 2px 6px; font-weight: 900; font-size: 11px; display: inline-block; }}
        .qty-box {{ background-color: rgba(88, 166, 255, 0.15); color: {accent_blue}; border: 1px solid rgba(88, 166, 255, 0.4); border-radius: 5px; padding: 2px 6px; font-weight: 900; font-size: 11px; display: inline-block; }}

        .live-blink {{ animation: pulseBlink 6.0s ease-in-out infinite; display: inline-block; }}
        @keyframes pulseBlink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    </style>
""",
    unsafe_allow_html=True,
)

# ETF Exclusions
ETF_KEYWORDS = [
    "BEES",
    "ETF",
    "GOLD",
    "SILVER",
    "LIQUID",
    "IWIN",
    "SETF",
    "HDFCMF",
    "ICICIMFC",
    "GILT",
    "NIFTY100",
    "MID150",
    "MOM50",
    "NIF100",
]


# --- 🚀 STRICT NIFTY 500 LOADER ---
@st.cache_data(ttl=86400)
def load_nifty500_stocks():
  try:
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    df_web = pd.read_csv(url)
    if "Symbol" in df_web.columns:
      syms = df_web["Symbol"].dropna().astype(str).str.strip().unique().tolist()
      filtered_syms = [
          f"{s.upper()}.NS"
          for s in syms
          if not any(kw in s.upper() for kw in ETF_KEYWORDS)
      ]
      if len(filtered_syms) >= 400:
        return filtered_syms
  except Exception:
    pass

  nifty_500_exact = [
      "3MINDIA.NS",
      "ABB.NS",
      "ACC.NS",
      "AIAENG.NS",
      "APLAPOLLO.NS",
      "AUBANK.NS",
      "AARTIIND.NS",
      "AAVAS.NS",
      "ABBOTINDIA.NS",
      "ACE.NS",
      "ADANIENSOL.NS",
      "ADANIENT.NS",
      "ADANIGREEN.NS",
      "ADANIPORTS.NS",
      "ADANIPOWER.NS",
      "ATGL.NS",
      "AWL.NS",
      "ABCAPITAL.NS",
      "ABFRL.NS",
      "AEGISCHEM.NS",
      "AETHER.NS",
      "AFFLE.NS",
      "AJANTPHARM.NS",
      "APLLTD.NS",
      "ALKEM.NS",
      "ALKYLAMINE.NS",
      "ALLCARGO.NS",
      "ALOKINDS.NS",
      "ARE&M.NS",
      "AMBER.NS",
      "AMBUJACEM.NS",
      "ANANDRATHI.NS",
      "ANGELONE.NS",
      "ANURAS.NS",
      "APARINDS.NS",
      "APOLLOHOSP.NS",
      "APOLLOTYRE.NS",
      "APTUS.NS",
      "ACI.NS",
      "ASAHIINDIA.NS",
      "ASHOKLEY.NS",
      "ASIANPAINT.NS",
      "ASTERDM.NS",
      "ASTRAL.NS",
      "ATUL.NS",
      "AUROPHARMA.NS",
      "AVANTIFEED.NS",
      "DMART.NS",
      "AXISBANK.NS",
      "BASF.NS",
      "BSE.NS",
      "BAJAJ-AUTO.NS",
      "BAJAJFINSV.NS",
      "BAJFINANCE.NS",
      "BAJAJHLDNG.NS",
      "BALAMINES.NS",
      "BALKRISIND.NS",
      "BALRAMCHIN.NS",
      "BANDHANBNK.NS",
      "BANKBARODA.NS",
      "BANKINDIA.NS",
      "MAHABANK.NS",
      "BATAINDIA.NS",
      "BAYERCROP.NS",
      "BERGEPAINT.NS",
      "BDL.NS",
      "BEL.NS",
      "BHARATFORG.NS",
      "BHEL.NS",
      "BPCL.NS",
      "BHARTIARTL.NS",
      "BIOCON.NS",
      "BIRLACORPN.NS",
      "BSOFT.NS",
      "BLISSGVS.NS",
      "BLSTARCO.NS",
      "BBTC.NS",
      "BORORENEW.NS",
      "BOSCHLTD.NS",
      "BHARATWIRE.NS",
      "BRIGADE.NS",
      "BRITANNIA.NS",
      "MAPMYINDIA.NS",
      "CESC.NS",
      "CGPOWER.NS",
      "CRISIL.NS",
      "CSBBANK.NS",
      "CAMPUS.NS",
      "CANFINHOME.NS",
      "CANBK.NS",
      "CAPLIPOINT.NS",
      "CGCL.NS",
      "CARBORUNIV.NS",
      "CASTROLIND.NS",
      "CEATLTD.NS",
      "CENTRALBK.NS",
      "CDSL.NS",
      "CENTURYPLY.NS",
      "CENTURYTEX.NS",
      "CERA.NS",
      "CHALET.NS",
      "CHAMBLFERT.NS",
      "CHEMAXX.NS",
      "CHMEDICARE.NS",
      "CHOLAFIN.NS",
      "CHOLAHLDNG.NS",
      "CIPLA.NS",
      "CUB.NS",
      "CLEAN.NS",
      "COALINDIA.NS",
      "COCHINSHIP.NS",
      "COFORGE.NS",
      "COLPAL.NS",
      "CAMS.NS",
      "CONCOR.NS",
      "COROMANDEL.NS",
      "CRAFTSMAN.NS",
      "CREDITACC.NS",
      "CROMPTON.NS",
      "CUMMINSIND.NS",
      "CYIENT.NS",
      "DCMSHRIRAM.NS",
      "DLF.NS",
      "DABUR.NS",
      "DALBHAT.NS",
      "DEEPAKFERT.NS",
      "DEEPAKNTR.NS",
      "DELHIVERY.NS",
      "DELTACORP.NS",
      "DEVYANI.NS",
      "DIVISLAB.NS",
      "DIXON.NS",
      "LALPATHLAB.NS",
      "DRREDDY.NS",
      "EIDPARRY.NS",
      "EIHOTEL.NS",
      "EPL.NS",
      "EASEMYTRIP.NS",
      "EICHERMOT.NS",
      "ELECON.NS",
      "ELGIEQUIP.NS",
      "EMAMILTD.NS",
      "ENDURANCE.NS",
      "ENGINERSIN.NS",
      "EQUIX.NS",
      "EQUITASBNK.NS",
      "ERIS.NS",
      "ESCORTS.NS",
      "EXIDEIND.NS",
      "FDC.NS",
      "NYKAA.NS",
      "FEDERALBNK.NS",
      "FACT.NS",
      "FINEORG.NS",
      "FINCABLES.NS",
      "FINPIPE.NS",
      "FSL.NS",
      "FIVESTAR.NS",
      "FORTIS.NS",
      "GRINFRA.NS",
      "GAIL.NS",
      "GMMPFAUDLR.NS",
      "GMRINFRA.NS",
      "GSS.NS",
      "GLAND.NS",
      "GLAXO.NS",
      "GLENMARK.NS",
      "MEDANTA.NS",
      "GOCOLORS.NS",
      "GODFRYPHLP.NS",
      "GODREJCP.NS",
      "GODREJPROP.NS",
      "GRANULES.NS",
      "GRAPHITE.NS",
      "GRASIM.NS",
      "GESHIP.NS",
      "GRINDWELL.NS",
      "GUJGASLTD.NS",
      "GMDCLTD.NS",
      "GNFC.NS",
      "GPPL.NS",
      "GSFC.NS",
      "GSPL.NS",
      "HEG.NS",
      "HCLTECH.NS",
      "HDFCAMC.NS",
      "HDFCBANK.NS",
      "HDFCLIFE.NS",
      "HFCL.NS",
      "HLEGLAS.NS",
      "HAL.NS",
      "HAPPSTMNDS.NS",
      "HAVELLS.NS",
      "HEROMOTOCO.NS",
      "HIMATSEIDE.NS",
      "HINDALCO.NS",
      "HAL.NS",
      "HINDCOPPER.NS",
      "HINDPETRO.NS",
      "HINDUNILVR.NS",
      "HINDZINC.NS",
      "POWERINDIA.NS",
      "HOMEFIRST.NS",
      "HONAUT.NS",
      "HUDCO.NS",
      "ICICIBANK.NS",
      "ICICIGI.NS",
      "ICICIPRULI.NS",
      "ISEC.NS",
      "IDBI.NS",
      "IDFCFIRSTB.NS",
      "IFCI.NS",
      "IIFL.NS",
      "IRB.NS",
      "IRCON.NS",
      "ITC.NS",
      "ITI.NS",
      "INDIACEM.NS",
      "INDIAMART.NS",
      "INDIANB.NS",
      "IEX.NS",
      "INDHOTEL.NS",
      "IOC.NS",
      "IRCTC.NS",
      "IRFC.NS",
      "INDIGOPNTS.NS",
      "IGL.NS",
      "INDUSTOWER.NS",
      "INDUSINDBK.NS",
      "INFIBEAM.NS",
      "NAUKRI.NS",
      "INFY.NS",
      "INOXWIND.NS",
      "INTELLECT.NS",
      "INDIGO.NS",
      "IPCALAB.NS",
      "JBCHEPHARM.NS",
      "JKCEMENT.NS",
      "JBMA.NS",
      "JKPAPER.NS",
      "JMFINANCIL.NS",
      "JSWENERGY.NS",
      "JSWSTEEL.NS",
      "JAIBALAJI.NS",
      "J&KBANK.NS",
      "JINDALSAW.NS",
      "JINDALSTEL.NS",
      "JIOFIN.NS",
      "JUBLFOOD.NS",
      "JUBLPHARMA.NS",
      "JUBLINGREA.NS",
      "KFINTECH.NS",
      "KEI.NS",
      "KNRCON.NS",
      "KPITTECH.NS",
      "KRBL.NS",
      "KSB.NS",
      "KAJARIACER.NS",
      "KPIL.NS",
      "KALYANKJIL.NS",
      "KANSAINER.NS",
      "KARURVYSYA.NS",
      "KAYNES.NS",
      "KEC.NS",
      "KENNAMET.NS",
      "KIRLOSENG.NS",
      "KOTAKBANK.NS",
      "KIMS.NS",
      "L&TFH.NS",
      "LTTS.NS",
      "LICHSGFIN.NS",
      "LTIM.NS",
      "LT.NS",
      "LATENTVIEW.NS",
      "LAURUSLABS.NS",
      "LXCHEM.NS",
      "LEMONTREE.NS",
      "LICI.NS",
      "LINDEINDIA.NS",
      "LUPIN.NS",
      "LUXIND.NS",
      "MMTC.NS",
      "MOIL.NS",
      "MRF.NS",
      "MGL.NS",
      "MAZDOCK.NS",
      "M&MFIN.NS",
      "M&M.NS",
      "MHRIL.NS",
      "MAHSEAMLES.NS",
      "MANAPPURAM.NS",
      "MRPL.NS",
      "MARICO.NS",
      "MARUTI.NS",
      "MASTEK.NS",
      "MFSL.NS",
      "MAXHEALTH.NS",
      "MAZDOCK.NS",
      "METROPOLIS.NS",
      "MINDACORP.NS",
      "MSUMI.NS",
      "MOTILALOFS.NS",
      "MPHASIS.NS",
      "MCX.NS",
      "MUTHOOTFIN.NS",
      "NATCOPHARM.NS",
      "NATIONALUM.NS",
      "NAVINFLUOR.NS",
      "NESTLEIND.NS",
      "NETWORK18.NS",
      "NHPC.NS",
      "NLCINDIA.NS",
      "NMDC.NS",
      "NTPC.NS",
      "OBEROIRLTY.NS",
      "ONGC.NS",
      "OIL.NS",
      "PAYTM.NS",
      "OFSS.NS",
      "PBFINTECH.NS",
      "PIIND.NS",
      "PNB.NS",
      "PFC.NS",
      "PVRINOX.NS",
      "PAGEIND.NS",
      "PATANJALI.NS",
      "PERSISTENT.NS",
      "PETRONET.NS",
      "PIDILITIND.NS",
      "POLYCAB.NS",
      "PFC.NS",
      "POWERGRID.NS",
      "PRAJIND.NS",
      "PRESTIGE.NS",
      "PRINCEPIPE.NS",
      "PGHH.NS",
      "PNB.NS",
      "QUESS.NS",
      "RBLBANK.NS",
      "RECLTD.NS",
      "RHIM.NS",
      "RITES.NS",
      "RADICO.NS",
      "RVNL.NS",
      "RAILTEL.NS",
      "RAIN.NS",
      "RAJESHEXPO.NS",
      "RALLIS.NS",
      "RAMCOCEM.NS",
      "RAMCOSYS.NS",
      "RATNAMANI.NS",
      "RAYMOND.NS",
      "REDINGTON.NS",
      "RELIANCE.NS",
      "RELIGARE.NS",
      "RITES.NS",
      "ROSSARI.NS",
      "ROUTE.NS",
      "SBFC.NS",
      "SBICARD.NS",
      "SBILIFE.NS",
      "SJVN.NS",
      "SKFINDIA.NS",
      "SRF.NS",
      "SAFARI.NS",
      "SAMVARDHANA.NS",
      "SANOFI.NS",
      "SANSERA.NS",
      "SAPPHIRE.NS",
      "SAREGAMA.NS",
      "SCHAEFFLER.NS",
      "SCHNEIDER.NS",
      "SEAMEC.NS",
      "SHARDACROP.NS",
      "SHOPERSTOP.NS",
      "SHREERENUK.NS",
      "SHRIRAMFIN.NS",
      "SIEMENS.NS",
      "SOBHA.NS",
      "SOLARINDS.NS",
      "SONACOMS.NS",
      "SONATSOFTW.NS",
      "SOUTHBANK.NS",
      "STARHEALTH.NS",
      "SBIN.NS",
      "SAIL.NS",
      "SVRAT.NS",
      "SUMICHEM.NS",
      "SUNPHARMA.NS",
      "SUNTV.NS",
      "SUNDARMFIN.NS",
      "SUNDRMFAST.NS",
      "SUNTECK.NS",
      "SUPRAJIT.NS",
      "SUPREMEIND.NS",
      "SUVENPHAR.NS",
      "SUZLON.NS",
      "SWANENERGY.NS",
      "SYMPHONY.NS",
      "SYNGENE.NS",
      "TVSMOTOR.NS",
      "TATACHEM.NS",
      "TATACOMM.NS",
      "TCS.NS",
      "TATAELXSI.NS",
      "TATAGLOBAL.NS",
      "TATAMTRDVR.NS",
      "TATAMOTORS.NS",
      "TATAPOWER.NS",
      "TATASTEEL.NS",
      "TATATECH.NS",
      "TTML.NS",
      "TECHM.NS",
      "TEJASNET.NS",
      "NIACL.NS",
      "RAMCOIND.NS",
      "THERMAX.NS",
      "THYROCARE.NS",
      "TIMKEN.NS",
      "TITAN.NS",
      "TORNTPHARM.NS",
      "TORNTPOWER.NS",
      "TRENT.NS",
      "TRIDENT.NS",
      "TRIVENI.NS",
      "TRITURBINE.NS",
      "TIINDIA.NS",
      "UCOBANK.NS",
      "UNOMINDA.NS",
      "UPL.NS",
      "UTIAMC.NS",
      "ULTRACEMCO.NS",
      "UNIONBANK.NS",
      "UBL.NS",
      "MCDOWELL-N.NS",
      "VGUARD.NS",
      "VMART.NS",
      "VIPIND.NS",
      "VAIBHAVGBL.NS",
      "VBL.NS",
      "VEDL.NS",
      "VIJAYA.NS",
      "VINATIORGA.NS",
      "IDEA.NS",
      "VOLTAS.NS",
      "WELCORP.NS",
      "WELSPUNLIV.NS",
      "WESTLIFE.NS",
      "WHIRLPOOL.NS",
      "WIPRO.NS",
      "WOCKPHARMA.NS",
      "YESBANK.NS",
      "ZFCVINDIA.NS",
      "ZEEL.NS",
      "ZENSARTECH.NS",
      "ZOMATO.NS",
      "ZYDUSLIFE.NS",
      "ECLERX.NS",
  ]
  return list(set(nifty_500_exact))


ALL_HIRA_SYMBOLS = load_nifty500_stocks()
TOTAL_SCANNED_STOCKS = len(ALL_HIRA_SYMBOLS)

# --- MARKET TIME DETECTOR ---
ist_tz = pytz.timezone("Asia/Kolkata")
now_dt = datetime.datetime.now(ist_tz)
market_open_time = now_dt.replace(hour=9, minute=15, second=0, microsecond=0)
market_close_time = now_dt.replace(hour=15, minute=30, second=0, microsecond=0)
is_market_open = (now_dt.weekday() < 5) and (
    market_open_time <= now_dt <= market_close_time
)

cache_ttl_seconds = 15 if is_market_open else 300


@st.cache_data(ttl=cache_ttl_seconds)
def fetch_indices():
  indices = {
      "NIFTY 50": ("^NSEI", "NSE:NIFTY"),
      "BANK NIFTY": ("^NSEBANK", "NSE:BANKNIFTY"),
      "SENSEX": ("^BSESN", "BSE:SENSEX"),
      "MIDCAP": ("NIFTY_MID_SELECT.NS", "NSE:NIFTY_MID_SELECT"),
  }
  symbols = [v[0] for v in indices.values()]
  res = {}
  try:
    data = yf.download(
        symbols, period="5d", interval="1d", progress=False, group_by="ticker"
    )
    for name, (sym, tv_sym) in indices.items():
      tv_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
      try:
        df = data[sym].dropna() if len(symbols) > 1 else data.dropna()
        if len(df) >= 2:
          curr, prev = df["Close"].iloc[-1], df["Close"].iloc[-2]
          change = curr - prev
          res[name] = {
              "val": round(float(curr), 2),
              "change": round(float(change), 2),
              "pct": round(float((change / prev) * 100), 2),
              "url": tv_url,
          }
        else:
          res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
      except Exception:
        res[name] = {"val": 0.0, "change": 0.0, "pct": 0.0, "url": tv_url}
  except Exception:
    for name, (sym, tv_sym) in indices.items():
      res[name] = {
          "val": 0.0,
          "change": 0.0,
          "pct": 0.0,
          "url": f"https://www.tradingview.com/chart/?symbol={tv_sym}",
      }
  return res


def calculate_vwap(df):
  tp = (df["High"] + df["Low"] + df["Close"]) / 3
  return (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()


@st.cache_data(ttl=cache_ttl_seconds)
def run_market_scanner():
  bullish_list, bearish_list, all_stocks = [], [], []
  per_trade_cap = 10000

  chunk_size = 100
  symbol_chunks = [
      ALL_HIRA_SYMBOLS[i : i + chunk_size]
      for i in range(0, len(ALL_HIRA_SYMBOLS), chunk_size)
  ]

  for chunk in symbol_chunks:
    try:
      bulk_5m = yf.download(
          chunk,
          period="2d",
          interval="5m",
          progress=False,
          group_by="ticker",
          threads=True,
      )
      bulk_1d = yf.download(
          chunk,
          period="5d",
          interval="1d",
          progress=False,
          group_by="ticker",
          threads=True,
      )
    except Exception:
      continue

    if bulk_5m is None or bulk_1d is None:
      continue

    for symbol in chunk:
      try:
        clean_symbol = symbol.replace(".NS", "").upper()
        df_5m = bulk_5m[symbol].dropna() if len(chunk) > 1 else bulk_5m.dropna()
        df_daily = (
            bulk_1d[symbol].dropna() if len(chunk) > 1 else bulk_1d.dropna()
        )

        if len(df_5m) < 15 or len(df_daily) < 2:
          continue

        df_5m["VWAP"] = calculate_vwap(df_5m)

        latest_trading_date = df_5m.index[-1].date()
        today_df = df_5m[df_5m.index.date == latest_trading_date].copy()

        if len(today_df) < 3:  # Need at least C1, C2, and C3
          continue

        valid_closes = today_df["Close"].dropna()
        if valid_closes.empty:
          continue
        curr_price = float(valid_closes.iloc[-1])

        # --- 🎯 PREVIOUS DAY HIGH & LOW (PDH / PDL) ---
        valid_daily = df_daily.dropna()
        if len(valid_daily) >= 2:
          prev_day_row = valid_daily.iloc[-2]
          pdh = float(prev_day_row["High"])
          pdl = float(prev_day_row["Low"])
          prev_close = float(prev_day_row["Close"])
        else:
          continue

        if curr_price <= 0:
          continue

        day_change_pct = float(((curr_price - prev_close) / prev_close) * 100)
        change_pts = float(curr_price - prev_close)
        tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
        calc_qty = max(1, int((per_trade_cap * 5) / curr_price))

        # --- 🎯 C1 (09:15 CANDLE) - STRICT 1.0% MAX RANGE ---
        c1 = today_df.iloc[0]
        c1_high, c1_low, c1_open, c1_close = (
            float(c1["High"]),
            float(c1["Low"]),
            float(c1["Open"]),
            float(c1["Close"]),
        )
        c1_range = c1_high - c1_low

        if c1_range == 0:
          continue

        c1_range_pct = (c1_range / c1_close) * 100

        # STRICT FILTER: Reject C1 if candle range > 1.0%
        if c1_range_pct > 1.0:
          continue

        gap_pct = abs(c1_open - prev_close) / prev_close * 100

        upper_wick_ratio = (c1_high - max(c1_open, c1_close)) / c1_range
        lower_wick_ratio = (min(c1_open, c1_close) - c1_low) / c1_range

        max_base_vol = max(
            float(c1["Volume"]), float(today_df.iloc[1]["Volume"])
        )
        if max_base_vol < 1000:
          continue

        # --- 🎯 C2 (09:20 PAUSE CANDLE) ---
        c2 = today_df.iloc[1]
        c2_high, c2_low, c2_open, c2_close = (
            float(c2["High"]),
            float(c2["Low"]),
            float(c2["Open"]),
            float(c2["Close"]),
        )
        c2_range = c2_high - c2_low

        # 🟢 STRICT BULLISH INITIAL CONDITIONS
        c1_bull_cond = (
            (c1_range_pct <= 1.0)
            and (gap_pct <= 1.0)
            and (upper_wick_ratio <= 0.35)
            and (lower_wick_ratio <= 0.35)
        )

        c2_bull_pause_cond = (
            (c2_close < c2_open)
            and (c2_high <= c1_high)
            and (c2_low >= c1_low)
            and (c2_range <= c1_range * 0.85)
        )

        # 🔴 STRICT BEARISH INITIAL CONDITIONS
        c1_bear_cond = (
            (c1_range_pct <= 1.0)
            and (gap_pct <= 1.0)
            and (upper_wick_ratio <= 0.35)
            and (lower_wick_ratio <= 0.35)
        )

        c2_bear_pause_cond = (
            (c2_close > c2_open)
            and (c2_high <= c1_high)
            and (c2_low >= c1_low)
            and (c2_range <= c1_range * 0.85)
        )

        # --- 🎯 ULTRA-STRICT EVALUATION ---
        signal_bullish, signal_bearish = False, False
        status_state, signal_time, vol_multiple = "READY", "-", 1.0

        if c1_bull_cond and c2_bull_pause_cond:
          for i in range(2, len(today_df)):
            c_curr = today_df.iloc[i]
            curr_close, curr_vwap = float(c_curr["Close"]), float(
                c_curr["VWAP"]
            )
            curr_vol = float(c_curr["Volume"])
            calc_vol_mult = (
                float(round(curr_vol / max_base_vol, 2))
                if max_base_vol > 0
                else 1.0
            )

            if (
                (curr_close > max(c1_high, c2_high))
                and (curr_close > curr_vwap)
                and (curr_close > pdh)
                and (calc_vol_mult >= 1.2)
            ):
              signal_bullish = True
              signal_time = c_curr.name.strftime("%H:%M")
              vol_multiple = calc_vol_mult
              break

        elif c1_bear_cond and c2_bear_pause_cond:
          for i in range(2, len(today_df)):
            c_curr = today_df.iloc[i]
            curr_close, curr_vwap = float(c_curr["Close"]), float(
                c_curr["VWAP"]
            )
            curr_vol = float(c_curr["Volume"])
            calc_vol_mult = (
                float(round(curr_vol / max_base_vol, 2))
                if max_base_vol > 0
                else 1.0
            )

            if (
                (curr_close < min(c1_low, c2_low))
                and (curr_close < curr_vwap)
                and (curr_close < pdl)
                and (calc_vol_mult >= 1.2)
            ):
              signal_bearish = True
              signal_time = c_curr.name.strftime("%H:%M")
              vol_multiple = calc_vol_mult
              break

        res = {
            "Symbol": str(clean_symbol),
            "Price": float(curr_price),
            "ChangePct": float(day_change_pct),
            "ChangePts": float(round(change_pts, 2)),
            "SignalTime": str(signal_time),
            "VolMultiple": float(vol_multiple),
            "IsBullish": bool(signal_bullish),
            "IsBearish": bool(signal_bearish),
            "StatusState": "READY",
            "TVUrl": str(tv_url),
            "Qty": int(calc_qty),
        }
        all_stocks.append(res)

        if signal_bullish:
          bullish_list.append(res)
        if signal_bearish:
          bearish_list.append(res)
      except Exception:
        continue

  all_df = pd.DataFrame(all_stocks)

  top_gainer, top_loser, balanced_movers = None, None, []

  if not all_df.empty:
    try:
      top_gainer = (
          all_df.sort_values(by="ChangePct", ascending=False).iloc[0].to_dict()
      )
      top_loser = (
          all_df.sort_values(by="ChangePct", ascending=True).iloc[0].to_dict()
      )

      gainers_4 = (
          all_df.sort_values(by="ChangePct", ascending=False)
          .head(4)
          .to_dict("records")
      )
      losers_4 = (
          all_df.sort_values(by="ChangePct", ascending=True)
          .head(4)
          .to_dict("records")
      )
      balanced_movers = gainers_4 + losers_4
    except Exception:
      pass

  # SORTING
  sorted_bullish = sorted(
      bullish_list,
      key=lambda x: (x.get("VolMultiple", 0), x.get("ChangePct", 0)),
      reverse=True,
  )
  sorted_bearish = sorted(
      bearish_list,
      key=lambda x: (x.get("VolMultiple", 0), abs(x.get("ChangePct", 0))),
      reverse=True,
  )

  top_bullish = sorted_bullish[:10]
  top_bearish = sorted_bearish[:10]

  return (
      top_bullish,
      top_bearish,
      top_gainer,
      top_loser,
      balanced_movers,
      len(bullish_list),
      len(bearish_list),
      all_stocks,
  )


# --- MARKET STATUS & HEADER HTML ---
status_html = (
    '<span class="market-status-open"><span class="live-blink">🟢</span>'
    ' OPEN</span>'
    if is_market_open
    else (
        '<span class="market-status-closed"><span'
        ' class="live-blink">🔴</span> CLOSED</span>'
    )
)

top_idx = fetch_indices()
now_time = now_dt.strftime("%d %b | %I:%M %p")

# --- 🎯 PERFECT BALANCED TOP HEADER ---
head_c1, head_c2, head_c3, head_c4, head_c5, head_c6 = st.columns(
    [0.16, 0.51, 0.07, 0.10, 0.08, 0.08]
)

with head_c1:
  st.markdown(
      '<div class="brand-logo">HIRA MOUNT TRADER</div>', unsafe_allow_html=True
  )

with head_c2:
  idx_pills_html = '<div class="indices-bar-wrapper">'
  for name, data in top_idx.items():
    pct = data.get("pct", 0)
    cls = "idx-up-p" if pct >= 0 else "idx-down-p"
    arrow = "▲" if pct >= 0 else "▼"
    idx_pills_html += (
        f'<a class="idx-pill" href="{data.get("url", "#")}"'
        f' target="_blank"><span class="idx-lbl">{name}:</span> <span'
        f' class="idx-num">{data.get("val", 0):,.2f}</span> <span'
        f' class="{cls}">{arrow}{pct:+.2f}%</span></a>'
    )
  idx_pills_html += "</div>"
  st.markdown(idx_pills_html, unsafe_allow_html=True)

with head_c3:
  st.markdown(
      f'<div class="header-status-box">{status_html}</div>',
      unsafe_allow_html=True,
  )

with head_c4:
  st.markdown(
      f'<div class="header-time-box">🕒 {now_time}</div>', unsafe_allow_html=True
  )

with head_c5:
  if st.button("🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"):
    st.session_state.theme = (
        "light" if st.session_state.theme == "dark" else "dark"
    )
    st.query_params["theme"] = st.session_state.theme
    st.rerun()

with head_c6:
  if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

st.markdown(
    f"<hr style='margin-top: 4px; margin-bottom: 10px; border-color:"
    f" {border_color}; opacity: 0.5;'>",
    unsafe_allow_html=True,
)

# --- EXECUTE SCANNER ---
(
    bullish_signals,
    bearish_signals,
    top_gainer,
    top_loser,
    market_movers,
    total_bull_cnt,
    total_bear_cnt,
    all_scanned_stocks,
) = run_market_scanner()
sideways_cnt = TOTAL_SCANNED_STOCKS - (total_bull_cnt + total_bear_cnt)
sentiment_label = "Bullish" if total_bull_cnt >= total_bear_cnt else "Bearish"
sentiment_color = "#3fb950" if total_bull_cnt >= total_bear_cnt else "#f85149"
sentiment_blink = "🟢" if total_bull_cnt >= total_bear_cnt else "🔴"
sentiment_arrow = "▲" if total_bull_cnt >= total_bear_cnt else "▼"

# --- 🎯 EQUAL SIZE 4 METRIC CARDS ---
c1, c2, c3, c4 = st.columns(4)

with c1:
  if top_gainer and isinstance(top_gainer, dict):
    st.markdown(
        f"""
            <div class="metric-container">
                <div class="card-label">TOP GAINER</div>
                <a href="{top_gainer.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 900; color: {accent_blue}; margin-top:2px; overflow:hidden; text-overflow:ellipsis;">{top_gainer.get('Symbol', '-')}</div>
                    <div class="card-value-green">+{top_gainer.get('ChangePct', 0):.2f}% <span style="font-size:12px; font-weight:700;">(+₹{top_gainer.get('ChangePts', 0)})</span></div>
                </a>
            </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
  if top_loser and isinstance(top_loser, dict):
    st.markdown(
        f"""
            <div class="metric-container">
                <div class="card-label">TOP LOSER</div>
                <a href="{top_loser.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div style="font-size: 15px; font-weight: 900; color: {accent_blue}; margin-top:2px; overflow:hidden; text-overflow:ellipsis;">{top_loser.get('Symbol', '-')}</div>
                    <div class="card-value-red">{top_loser.get('ChangePct', 0):.2f}% <span style="font-size:12px; font-weight:700;">(₹{top_loser.get('ChangePts', 0)})</span></div>
                </a>
            </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
  st.markdown(
      f"""
        <div class="metric-container">
            <div class="card-label">MARKET SENTIMENT</div>
            <div style="font-size: 17px; font-weight: 900; color: {sentiment_color}; margin-top:2px; display:flex; align-items:center; gap:6px;">
                <span class="live-blink">{sentiment_blink}</span>
                <span>{sentiment_label}</span>
                <span style="font-size:13px;">{sentiment_arrow}</span>
            </div>
            <div style="font-size: 11px; color: {text_sub}; margin-top: 2px; font-weight: 800;">
                <span style="color:#3fb950;">▲ {total_bull_cnt}</span> | 
                <span style="color:#f85149;">▼ {total_bear_cnt}</span> | 
                <span>⚪ {sideways_cnt}</span>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with c4:
  st.markdown(
      f"""
        <div class="metric-container">
            <div class="card-label">SCANNED STOCKS</div>
            <div style="font-size: 17px; font-weight: 900; color: {accent_blue}; margin-top:2px;">
                {TOTAL_SCANNED_STOCKS} Stocks
            </div>
            <div style="font-size: 11px; color: #3fb950; font-weight: 800; margin-top: 2px;">Active: {total_bull_cnt + total_bear_cnt}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown(
    """<div class="box-container"><div class="box-title">🔥 MARKET MOVERS</div></div>""",
    unsafe_allow_html=True,
)

if market_movers:
  m_cols = st.columns(len(market_movers))
  for i, m in enumerate(market_movers):
    with m_cols[i]:
      p_class = (
          "stock-price-up"
          if m.get("ChangePct", 0) >= 0
          else "stock-price-down"
      )
      sign = "+" if m.get("ChangePct", 0) >= 0 else ""
      time_str = (
          m.get("SignalTime", "09:20")
          if m.get("SignalTime") != "-"
          else "09:20"
      )
      st.markdown(
          f"""
                <a href="{m.get('TVUrl', '#')}" target="_blank" style="text-decoration:none;">
                    <div class="stock-card">
                        <div class="stock-card-top">
                            <span class="stock-symbol">{m.get('Symbol', '-')}</span>
                            <div style="display:flex; gap:3px;">
                                <span class="qty-box">{m.get('Qty', 1)}</span>
                                <span class="vol-box">{m.get('VolMultiple', 1.0):.1f}x</span>
                            </div>
                        </div>
                        <div class="stock-card-body">
                            <div>
                                <span class="{p_class} live-blink">₹{m.get('Price', 0):.2f}</span>
                                <span style="font-size: 12px; font-weight: 900; color: {'#3fb950' if m.get('ChangePct', 0)>=0 else '#f85149'};">{sign}{m.get('ChangePct', 0):.2f}%</span>
                            </div>
                            <div class="stock-meta">🕒 {time_str}</div>
                        </div>
                    </div>
                </a>
            """,
          unsafe_allow_html=True,
      )

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- 🎯 BULLISH & BEARISH SETUPS ---
tb_col1, tb_col2 = st.columns(2)

with tb_col1:
  st.markdown(
      """
        <div class="setup-box">
            <div class="setup-header-bull"><span class="live-blink">🟢</span> BULLISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span><span style="width: 15%;">STATUS</span><span style="width: 15%;">ALERT TIME</span><span style="width: 15%;">VOL SURGE</span><span style="width: 12%;">QTY</span><span style="width: 11%; text-align:right;">PRICE</span><span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  if bullish_signals:
    for s in bullish_signals[:10]:
      status_btn = '<span class="status-ready-bull">READY</span>'
      st.markdown(
          f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box">{s.get('Symbol')}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
                    <div style="width: 15%; font-size:12px; color:{text_sub}; font-weight:800;">🕒 {s.get('SignalTime')}</div>
                    <div style="width: 15%;"><span class="vol-box">{s.get('VolMultiple', 1.0):.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s.get('Qty', 1)}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:14px;" class="live-blink">₹{s.get('Price', 0):.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#3fb950; font-size:13px;">▲{s.get('ChangePct', 0):.2f}%</div>
                </a>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.markdown(
        f'<div style="text-align:center; color:{text_sub}; padding:25px;'
        ' font-weight:700; font-size:13px;">Searching for High-Volume'
        ' Bullish breakouts...</div>',
        unsafe_allow_html=True,
    )

with tb_col2:
  st.markdown(
      """
        <div class="setup-box">
            <div class="setup-header-bear"><span class="live-blink">🔴</span> BEARISH SETUPS</div>
            <div class="row-header">
                <span style="width: 20%;">SYMBOL</span><span style="width: 15%;">STATUS</span><span style="width: 15%;">ALERT TIME</span><span style="width: 15%;">VOL SURGE</span><span style="width: 12%;">QTY</span><span style="width: 11%; text-align:right;">PRICE</span><span style="width: 12%; text-align:right;">CHANGE</span>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  if bearish_signals:
    for s in bearish_signals[:10]:
      status_btn = '<span class="status-ready-bear">READY</span>'
      st.markdown(
          f"""
                <a href="{s.get('TVUrl', '#')}" target="_blank" class="stock-row-item">
                    <div style="width: 20%;"><span class="sym-btn-box" style="color:#f85149;">{s.get('Symbol')}</span></div>
                    <div style="width: 15%;">{status_btn}</div>
                    <div style="width: 15%; font-size:12px; color:{text_sub}; font-weight:800;">🕒 {s.get('SignalTime')}</div>
                    <div style="width: 15%;"><span class="vol-box">{s.get('VolMultiple', 1.0):.2f}x</span></div>
                    <div style="width: 12%;"><span class="qty-box">{s.get('Qty', 1)}</span></div>
                    <div style="width: 11%; text-align:right; font-weight:900; color:{text_main}; font-size:14px;" class="live-blink">₹{s.get('Price', 0):.2f}</div>
                    <div style="width: 12%; text-align:right; font-weight:900; color:#f85149; font-size:13px;">▼{s.get('ChangePct', 0):.2f}%</div>
                </a>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.markdown(
        f'<div style="text-align:center; color:{text_sub}; padding:25px;'
        ' font-weight:700; font-size:13px;">Searching for High-Volume Bearish'
        ' breakdowns...</div>',
        unsafe_allow_html=True,
    )

# --- 🎯 NIFTY 500 EXACT TREEMAP HEATMAP (MATCHING YOUR PHOTO PERFECTLY) ---
st.markdown(
    """<div class="box-container"><div class="box-title">🗺️ NIFTY 500 MARKET HEATMAP (TOP 10 GAINERS & TOP 10 LOSERS)</div></div>""",
    unsafe_allow_html=True,
)

if all_scanned_stocks:
  df_hm = pd.DataFrame(all_scanned_stocks)
  if not df_hm.empty and "ChangePct" in df_hm.columns:
    top_10_gainers = (
        df_hm.sort_values(by="ChangePct", ascending=False)
        .head(10)
        .to_dict("records")
    )
    top_10_losers = (
        df_hm.sort_values(by="ChangePct", ascending=True)
        .head(10)
        .to_dict("records")
    )

    hm_css_html = """
        <style>
            .treemap-grid-box {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 6px;
                background-color: #161b22;
                padding: 12px;
                border-radius: 8px;
                border: 1.5px solid #30363d;
            }
            .tm-tile-box {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 14px 6px;
                border-radius: 4px;
                border: 2px solid #000000;
                text-decoration: none !important;
                transition: transform 0.15s ease, filter 0.15s ease;
                min-height: 80px;
            }
            .tm-tile-box:hover {
                transform: scale(1.04);
                filter: brightness(1.2);
                z-index: 10;
            }
            .tm-sym-text {
                font-size: 13px;
                font-weight: 900;
                color: #ffffff;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                text-align: center;
            }
            .tm-pct-text {
                font-size: 14px;
                font-weight: 900;
                color: #ffffff;
                margin-top: 4px;
            }
        </style>
        <div class="treemap-grid-box">
        """

    # Green Tiles (Top Gainers)
    for g in top_10_gainers:
      pct = g.get("ChangePct", 0)
      sym = g.get("Symbol", "")
      url = g.get("TVUrl", "#")
      bg_color_tile = (
          "#00c853" if pct >= 3.0 else "#00e676" if pct >= 1.5 else "#00a843"
      )
      hm_css_html += f"""
            <a href="{url}" target="_blank" class="tm-tile-box" style="background-color: {bg_color_tile};">
                <span class="tm-sym-text">{sym}</span>
                <span class="tm-pct-text">+{pct:.2f}%</span>
            </a>
            """

    # Red Tiles (Top Losers)
    for l in top_10_losers:
      pct = l.get("ChangePct", 0)
      sym = l.get("Symbol", "")
      url = l.get("TVUrl", "#")
      abs_pct = abs(pct)
      bg_color_tile = (
          "#ff1744"
          if abs_pct >= 3.0
          else "#d50000"
          if abs_pct >= 1.5
          else "#c62828"
      )
      hm_css_html += f"""
            <a href="{url}" target="_blank" class="tm-tile-box" style="background-color: {bg_color_tile};">
                <span class="tm-sym-text">{sym}</span>
                <span class="tm-pct-text">{pct:.2f}%</span>
            </a>
            """

    hm_css_html += "</div>"
    st.markdown(hm_css_html, unsafe_allow_html=True)

# --- 🚀 POWERFUL LIVE AUTO REFRESH SYSTEM ---
refresh_time_ms = 15000 if is_market_open else 300000
st.markdown(
    f"<script>setTimeout(function(){{ window.location.reload(); }},"
    f" {refresh_time_ms});</script>",
    unsafe_allow_html=True,
)
