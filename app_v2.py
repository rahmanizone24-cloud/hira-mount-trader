# ZERO MARGIN & FIT TO SCREEN CSS
st.markdown(
    f"""
<style>
    /* 1. Remove Top Header Bar Extra Space */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    
    /* 2. Main Container Full Width & Height Stretch */
    .main .block-container {{
        max-width: 100% !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        margin: 0 !important;
    }}
    
    /* 3. Global Reset & App Background */
    .stApp {{
        background-color: {bg_app};
        color: {txt_main};
        font-family: 'Inter', sans-serif;
    }}

    /* 4. Column Gap Reduction for Perfect Desktop Fit */
    [data-testid="column"] {{
        padding: 0px 3px !important;
    }}

    /* Integrated Header Bar */
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
    
    .mover-box {{
        background: {bg_card};
        border: 1px solid {border_clr};
        border-radius: 8px;
        padding: 6px;
        text-align: center;
    }}
    
    .stock-title-link {{ font-size: 14px; font-weight: 800; color: #38bdf8; text-decoration: none; }}
    .stock-title-link:hover {{ text-decoration: underline; color: #7dd3fc; }}
    
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

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
</style>
""",
    unsafe_allow_html=True,
)
