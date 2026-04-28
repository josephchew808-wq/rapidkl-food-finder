import streamlit as st
import json
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="RapidKL Food Finder", page_icon="🚆", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    :root { --st-primary-color: #888888 !important; }
    div[data-baseweb="select"] { border: 1px solid #444 !important; border-radius: 4px !important; background-color: #262730 !important; }
    [data-testid="stExpander"] { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0px !important; }
    summary { border: none !important; padding: 0px !important; color: white !important; }
    [data-testid="stExpander"] svg { display: none !important; }
    thead tr th { text-transform: uppercase; color: #888888 !important; border-bottom: 1px solid #333 !important; }
    hr { border-top: 1px solid #333 !important; margin: 15px 0 !important; }
    </style>
""", unsafe_allow_html=True)


# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if not os.path.exists('data.json'): return pd.DataFrame()
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data: return pd.DataFrame()
            return pd.DataFrame(data)
    except:
        return pd.DataFrame()


# --- 4. MAIN INTERFACE ---
st.sidebar.title("🚆 RapidKL Finder")
food_df = load_data()
LINE_MAP = {"Kelana Jaya Line": "🔴", "Kajang Line": "🟢", "Putrajaya Line": "🟡", "Ampang Line": "🟠",
            "Sri Petaling Line": "🟤", "KL Monorail": "🟢"}

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
                # We clean 'food' here just in case the JSON has old messy data
                cuisine = row['food'] if isinstance(row['food'], str) and '[' not in str(
                    row['food']) else "Local Cuisine"
                st.write(f"**Cuisine:** {cuisine} | **Hours:** {row['opening']} - {row['closing']}")

                if 'menu' in row and isinstance(row['menu'], list):
                    menu_df = pd.DataFrame(row['menu'])
                    if not menu_df.empty:
                        menu_df.columns = [str(c).upper() for c in menu_df.columns]
                        if 'PRICE' in menu_df.columns:
                            menu_df['PRICE'] = menu_df['PRICE'].apply(lambda x: f"RM {float(x):.2f}")
                        st.dataframe(menu_df, use_container_width=True, hide_index=True)

        with col_btn:
            btn_html = f"""<div style="display: flex; justify-content: center; align-items: center; height: 28px; padding-top: 2px;"><button onclick="navigator.clipboard.writeText('{row['name']}')" style="background: none; border: none; color: #555; cursor: pointer; padding: 0;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></button></div>"""
            st.components.v1.html(btn_html, height=35)

        st.markdown("---")
else:
    st.info("The database is currently empty.")