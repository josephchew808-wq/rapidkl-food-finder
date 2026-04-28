import streamlit as st
import json
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="RapidKL Food Finder", page_icon="🚆", layout="wide")

# --- 2. CSS STYLING (THEME-FRIENDLY & CLEAN) ---
st.markdown("""
    <style>
    /* Global branding */
    :root { --st-primary-color: #888888; }

    /* Fix invisible text by letting Streamlit handle colors, only styling borders */
    div[data-baseweb="select"] { 
        border: 1px solid rgba(128, 128, 128, 0.3) !important; 
        border-radius: 4px !important; 
    }

    /* Remove expander styling clutter */
    [data-testid="stExpander"] { 
        border: none !important; 
        background: transparent !important; 
        box-shadow: none !important; 
    }

    summary { 
        border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important; 
        padding-bottom: 5px !important;
    }

    /* HIDE THE ANNOYING TOOLBAR (Download/Search) on all dataframes */
    [data-testid="stElementToolbar"] {
        display: none;
    }

    [data-testid="stExpander"] svg { display: none !important; }

    thead tr th { 
        text-transform: uppercase; 
        border-bottom: 1px solid rgba(128, 128, 128, 0.3) !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if not os.path.exists('data.json'): return pd.DataFrame()
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# --- 4. MAIN INTERFACE ---
st.sidebar.title("🚆 RapidKL Finder")
food_df = load_data()
LINE_MAP = {
    "Kelana Jaya Line": "🔴", "Kajang Line": "🟢", "Putrajaya Line": "🟡", 
    "Ampang Line": "🟠", "Sri Petaling Line": "🟤", "KL Monorail": "🟢"
}

if not food_df.empty:
    available_lines = sorted(list(food_df['line'].unique()))
    line_display = [f"{LINE_MAP.get(l, '🚇')} {l}" for l in available_lines]
    sel_line_raw = st.sidebar.radio("Select Line", line_display)
    sel_line = sel_line_raw.split(" ", 1)[1]

    filtered_df = food_df[food_df['line'] == sel_line]
    available_stations = sorted(list(filtered_df['station'].unique()))
    sel_station = st.selectbox(f"📍 Station ({sel_line})", available_stations)

    results = filtered_df[filtered_df['station'] == sel_station]

    for _, row in results.iterrows():
        header_text = f"🍴 **{row['name']}** | 🚶 {row['distance']}m | 💰 RM{row['price_min']}-{row['price_max']}"
        col_main, col_btn = st.columns([15, 1])

        with col_main:
            with st.expander(header_text):
                cuisine = row['food'] if isinstance(row['food'], str) and '[' not in str(row['food']) else "Local Cuisine"
                st.write(f"**Cuisine:** {cuisine} | **Hours:** {row['opening']} - {row['closing']}")

                if 'menu' in row and isinstance(row['menu'], list):
                    menu_df = pd.DataFrame(row['menu'])
                    if not menu_df.empty:
                        # Professional Table Config
                        st.dataframe(
                            menu_df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "item": st.column_config.TextColumn("ITEM"),
                                "price": st.column_config.NumberColumn("PRICE", format="RM %.2f")
                            }
                        )

        with col_btn:
            # Clipboard button inside a clean container
            btn_html = f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 35px;">
                <button onclick="navigator.clipboard.writeText('{row['name']}')" 
                        style="background:none; border:none; color:#888; cursor:pointer;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                </button>
            </div>
            """
            st.components.v1.html(btn_html, height=40)

        st.markdown("---")
else:
    st.info("The database is currently empty.")
