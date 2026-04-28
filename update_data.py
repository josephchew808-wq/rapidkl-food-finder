import json
import os
import time
import re
from google import genai
from groq import Groq

# ==========================================
# 1. API CONFIGURATION
# ==========================================
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# ==========================================
# 2. FULL INTEGRATED TRANSIT NETWORK
# ==========================================
LINES = {
    "Kelana Jaya Line": [
        "Gombak", "Taman Melati", "Wangsa Maju", "Sri Rampai", "Setiawangsa", "Jelatek",
        "Dato' Keramat", "Damai", "Ampang Park", "KLCC", "Kampung Baru", "Dang Wangi",
        "Masjid Jamek", "Pasar Seni", "KL Sentral", "Bangsar", "Abdullah Hukum", "Kerinchi",
        "Universiti", "Taman Jaya", "Asia Jaya", "Taman Paramount", "Taman Bahagia",
        "Kelana Jaya", "Lembah Subang", "Ara Damansara", "Glenmarie", "Subang Jaya",
        "SS15", "SS18", "USJ 7", "Taipan", "Wawasan", "USJ 21", "Alam Megah",
        "Subang Alam", "Putra Heights"
    ],
    "Ampang Line": [
        "Sentul Timur", "Sentul", "Titiwangsa", "PWTC", "Sultan Ismail", "Bandaraya",
        "Masjid Jamek", "Plaza Rakyat", "Hang Tuah", "Pudu", "Chan Sow Lin", "Miharja",
        "Maluri", "Pandan Jaya", "Pandan Indah", "Cempaka", "Cahaya", "Ampang"
    ],
    "Sri Petaling Line": [
        "Sentul Timur", "Sentul", "Titiwangsa", "PWTC", "Sultan Ismail", "Bandaraya",
        "Masjid Jamek", "Plaza Rakyat", "Hang Tuah", "Pudu", "Chan Sow Lin", "Cheras",
        "Bandar Tun Razak", "Bandar Tasik Selatan", "Sungai Besi", "Bukit Jalil",
        "Sri Petaling", "Awan Besar", "Muhibbah", "Alam Sutera", "Kinrara BK5",
        "IOI Puchong Jaya", "Pusat Bandar Puchong", "Taman Perindustrian Puchong",
        "Bandar Puteri", "Puchong Perdana", "Puchong Prima", "Putra Heights"
    ],
    "Kajang Line": [
        "Kwasa Damansara", "Kwasa Sentral", "Kota Damansara", "Surian", "Mutiara Damansara",
        "Bandar Utama", "TTDI", "Phileo Damansara", "Pusat Bandar Damansara", "Semantan",
        "Muzium Negara", "Pasar Seni", "Merdeka", "Bukit Bintang", "Tun Razak Exchange",
        "Cochrane", "Maluri", "Taman Pertama", "Taman Midah", "Taman Mutiara",
        "Taman Connaught", "Taman Suntex", "Sri Raya", "Bandar Tun Hussein Onn",
        "Batu 11 Cheras", "Bukit Dukung", "Sungai Jernih", "Stadium Kajang", "Kajang"
    ],
    "Putrajaya Line": [
        "Kwasa Damansara", "Kampung Selamat", "Sungai Buloh", "Damansara Damai",
        "Sri Damansara Barat", "Sri Damansara Sentral", "Sri Damansara Timur",
        "Metro Prima", "Kepong Baru", "Jinjang", "Sri Delima", "Kampung Batu",
        "Kentonmen", "Jalan Ipoh", "Sentul Barat", "Titiwangsa", "Hospital Kuala Lumpur",
        "Raja Uda", "Ampang Park", "Persiaran KLCC", "Conlay", "Tun Razak Exchange",
        "Chan Sow Lin", "Kuchai", "Taman Naga Emas", "Sungai Besi", "Serdang Raya Utara",
        "Serdang Raya Selatan", "Serdang Jaya", "UPM", "Taman Equine", "Putra Permai",
        "16 Sierra", "Cyberjaya Utara", "Cyberjaya City Centre", "Putrajaya Sentral"
    ],
    "KL Monorail": [
        "KL Sentral", "Tun Sambanthan", "Maharajalela", "Hang Tuah", "Imbi",
        "Bukit Bintang", "Raja Chulan", "Bukit Nanas", "Medan Tuanku", "Chow Kit", "Titiwangsa"
    ]
}


# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def clean_station_name(name):
    mapping = {"Asian Jaya": "Asia Jaya", "Kuala Lumpur Sentral": "KL Sentral", "KLCC Station": "KLCC"}
    return mapping.get(name, name)


def clean_menu(menu_data, avg_price=15):
    cleaned = []
    banned_terms = {"signature dish", "main course", "food item", "dish", "special", "placeholder"}
    if isinstance(menu_data, list):
        for entry in menu_data:
            item_name = ""
            price = avg_price
            if isinstance(entry, str):
                item_name = entry.strip()
            elif isinstance(entry, dict):
                # AI sometimes uses 'name' instead of 'item', let's handle both
                item_name = str(entry.get("item", entry.get("name", ""))).strip()
                price = entry.get("price", avg_price)

            if item_name and item_name.lower() not in banned_terms:
                try:
                    price = float(str(price).replace('RM', '').strip())
                except:
                    price = avg_price
                cleaned.append({"ITEM": item_name, "PRICE": price})  # Uppercase keys for Streamlit
    return cleaned if cleaned else [{"ITEM": "Nasi Lemak Ayam", "PRICE": avg_price}]


def format_time_12h(time_str):
    time_str = str(time_str).upper().strip()
    if "AM" in time_str or "PM" in time_str: return time_str
    match = re.search(r"(\d{1,2})[:.]?(\d{2})?", time_str)
    if match:
        hr = int(match.group(1))
        mn = match.group(2) if match.group(2) else "00"
        period = "AM"
        if hr >= 12:
            period = "PM"
            if hr > 12: hr -= 12
        if hr == 0: hr = 12
        return f"{hr}:{mn} {period}"
    return time_str


def clean_numeric(value, default=0):
    if isinstance(value, (int, float)): return int(value)
    text = str(value).lower()
    multiplier = 1000 if 'km' in text else 1
    clean_str = "".join(c for c in text if c.isdigit() or c == '.')
    try:
        return int(float(clean_str) * multiplier)
    except:
        return default


def find_list_in_json(data):
    if isinstance(data, list): return data
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                return value
    return []


# ==========================================
# 4. STORAGE LOGIC
# ==========================================
def save_data(db_dict):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(list(db_dict.values()), f, separators=(',', ':'))
    if not os.path.exists('lines'): os.makedirs('lines')
    line_groups = {}
    for item in db_dict.values():
        line_key = item['line'].lower().replace(' ', '_')
        if line_key not in line_groups: line_groups[line_key] = []
        line_groups[line_key].append(item)
    for line_key, data in line_groups.items():
        with open(f'lines/{line_key}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))


# ==========================================
# 5. MAIN SYNC LOGIC (ANTI-HALLUCINATION)
# ==========================================
def auto_scout():
    db_dict = {}
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try:
                existing_list = json.load(f)
                db_dict = {item['name']: item for item in existing_list if 'name' in item}
            except:
                pass

    print(f"🚀 Starting Mega-Sync (Corrected Logic Mode)...")

    SYSTEM_INSTRUCTION = (
        "You are a Malaysian food database bot. Output ONLY raw JSON. "
        "STRICT: 'food' must be a simple string (e.g., 'Chinese', 'Mamak', 'Cafe'). "
        "STRICT: 'menu' must be a list of around 12 objects with 'item' and 'price'. "
        "DO NOT dump the menu list into the 'food' field."
        "STRICT: NO PLACEHOLDERS like 'Signature Dish'."
    )

    for line_name, station_list in LINES.items():
        print(f"\n--- Processing: {line_name} ---")
        for station in station_list:
            existing_count = sum(1 for s in db_dict.values() if s.get('station') == station)
            if existing_count >= 10:
                print(f"   ⏩ Skipping {station}")
                continue

            prompt = (
                f"Find 5 REAL popular eateries near {station} station ({line_name}), Malaysia. "
                "Provide: 'name', 'station', 'line', 'distance' (meters), 'price_min' (of food, not drinks prices), 'price_max', "
                "'food' (Short cuisine type ONLY), 'opening', 'closing'. "
                "The 'menu' field MUST be a JSON list of around 12 real unique dishes. "
                "Return ONLY a raw JSON array [{},{},...]."
            )

            scouted_spots = []
            try:
                print(f"🔍 [Gemini] {station}...")
                resp = gemini_client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                raw_text = resp.text.replace("```json", "").replace("```", "").strip()
                scouted_spots = find_list_in_json(json.loads(raw_text))
            except Exception:
                print(f"   ⚠️ Gemini Limit. Trying Groq...")
                try:
                    completion = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    scouted_spots = find_list_in_json(json.loads(completion.choices[0].message.content))
                except Exception as groq_err:
                    print(f"   ❌ API Failure: {groq_err}")
                    time.sleep(5)
                    continue

            if scouted_spots:
                for spot in scouted_spots:
                    if not isinstance(spot, dict) or 'name' not in spot: continue
                    spot['station'] = clean_station_name(station)
                    spot['line'] = line_name
                    spot['distance'] = clean_numeric(spot.get('distance', 0))
                    p_min = clean_numeric(spot.get('price_min', 10))
                    p_max = clean_numeric(spot.get('price_max', 30))
                    spot['price_min'], spot['price_max'] = p_min, p_max
                    spot['opening'] = format_time_12h(spot.get('opening', '10:00 AM'))
                    spot['closing'] = format_time_12h(spot.get('closing', '10:00 PM'))

                    # Fix the 'food' field if the AI dumped a list there
                    if isinstance(spot.get('food'), list):
                        spot['food'] = "Local Eatery"

                    spot['menu'] = clean_menu(spot.get('menu'), avg_price=(p_min + p_max) // 2)
                    db_dict[spot['name']] = spot

                save_data(db_dict)
                print(f"   ✅ {station} synchronized correctly.")

            time.sleep(4)

    print(f"\n✨ MEGA SYNC COMPLETE. Total records: {len(db_dict)}")


if __name__ == "__main__":
    auto_scout()