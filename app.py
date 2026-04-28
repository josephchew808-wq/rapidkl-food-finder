import streamlit as st
import json
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="RapidKL Food Finder", page_icon="🚆", layout="wide")

# --- 2. CSS STYLING (THEME-FRIENDLY & CLEAN) ---
st.markdown("""
    <style>
    :root { --st-primary-color: #888888; }

    div[data-baseweb="select"] { 
        border: 1px solid rgba(128, 128, 128, 0.3) !important; 
        border-radius: 4px !important; 
    }

    [data-testid="stExpander"] { 
        border: none !important; 
        background: transparent !important; 
        box-shadow: none !important; 
    }

    summary { 
        border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important; 
        padding-bottom: 5px !important;
    }

    [data-testid="stElementToolbar"] { display: none; }
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
        # Using .get() for safer data access during presentation
        header_text = f"🍴 **{row.get('name', 'Unknown')}** | 🚶 {row.get('distance', 0)}m | 💰 RM{row.get('price_min', 0)}-{row.get('price_max', 0)}"
        col_main, col_btn = st.columns([15, 1])

        with col_main:
            with st.expander(header_text):
                cuisine = row.get('food', 'Local Cuisine')
                if not isinstance(cuisine, str) or '[' in str(cuisine):
                    cuisine = "Local Cuisine"
                
                st.write(f"**Cuisine:** {cuisine} | **Hours:** {row.get('opening', 'N/A')} - {row.get('closing', 'N/A')}")

                if 'menu' in row and isinstance(row['menu'], list):
                    menu_df = pd.DataFrame(row['menu'])
                    if not menu_df.empty:
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
            btn_html = f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 35px;">
                <button onclick="navigator.clipboard.writeText('{row.get('name', '')}')" 
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

# --- 5. TECHNICAL INFO (DISCRETE SECTION) ---
st.sidebar.markdown("---") 
with st.sidebar.expander("🛠️ Technical Architecture"):
    st.info("""
    **Core Concept:**
    LLM-automated transit-food database.
    
    **Backend Logic:**
    - **Scouting:** `update_data.py` uses Gemini 2.0 & Llama 3.1 APIs to source real-time eatery data.
    - **Validation:** Python logic filters AI hallucinations and formats data into JSON.
    - **Architecture:** Decoupled local-to-cloud pipeline using GitHub CI/CD.
    """)
