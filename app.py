import streamlit as st
import requests
import json
import os
import random

WARDROBE_FILE = "my_wardrobe.json"
API_KEY = os.environ.get("OPENWEATHER_API_KEY")

# Weather category -> accent color + icon. Reused for result boxes, badges and outfit cards.
ACCENT = {
    "Hot":  {"color": "#E2703A", "icon": "☀️"},
    "Mild": {"color": "#7FA65C", "icon": "🌤️"},
    "Cold": {"color": "#5B8AA6", "icon": "❄️"},
    "Rain": {"color": "#7C6FA6", "icon": "🌧️"},
}

CATEGORY_ICON = {"tops": "👕", "bottoms": "👖", "shoes": "👟", "outerwear": "🧥"}


def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        with open(WARDROBE_FILE, "r") as f:
            return json.load(f)
    return {"tops": [], "bottoms": [], "shoes": [], "outerwear": []}


def save_wardrobe(data):
    with open(WARDROBE_FILE, "w") as f:
        json.dump(data, f)


def weather_tag_for(temp, weather_main):
    if weather_main == "Rain":
        return "Rain"
    if temp < 15:
        return "Cold"
    if temp <= 25:
        return "Mild"
    return "Hot"


def pick_outfit(wardrobe, tag):
    """Pick a top, then try to match shoes to it and contrast the bottoms (basic sandwich rule)."""
    tops = [i for i in wardrobe["tops"] if i["weather"] == tag]
    bottoms = [i for i in wardrobe["bottoms"] if i["weather"] == tag]
    shoes = [i for i in wardrobe["shoes"] if i["weather"] == tag]
    outerwear = [i for i in wardrobe["outerwear"] if i["weather"] == tag]

    outfit = {k: {"name": None, "color": None} for k in ["tops", "bottoms", "shoes", "outerwear"]}
    if not tops:
        return outfit

    top = random.choice(tops)
    outfit["tops"] = {"name": top["name"], "color": top["color"]}

    matching_shoes = [s for s in shoes if s["color"] == top["color"]]
    chosen_shoes = random.choice(matching_shoes) if matching_shoes else (random.choice(shoes) if shoes else None)
    if chosen_shoes:
        outfit["shoes"] = {"name": chosen_shoes["name"], "color": chosen_shoes["color"]}

    contrasting_bottoms = [b for b in bottoms if b["color"] != top["color"]]
    chosen_bottom = random.choice(contrasting_bottoms) if contrasting_bottoms else (random.choice(bottoms) if bottoms else None)
    if chosen_bottom:
        outfit["bottoms"] = {"name": chosen_bottom["name"], "color": chosen_bottom["color"]}

    if outerwear and tag != "Hot":
        piece = random.choice(outerwear)
        outfit["outerwear"] = {"name": piece["name"], "color": piece["color"]}

    return outfit


# ---------- rendering helpers ----------

def swatch(color):
    """A small colored dot for a garment's color. Falls back to a hollow dot for unknown colors."""
    if not color:
        return '<span class="swatch swatch-empty"></span>'
    return f'<span class="swatch" style="background:{color.lower()}"></span>'


def render_chips(items):
    if not items:
        return '<p class="empty-note">Nothing added yet.</p>'
    chips = "".join(
        f'<div class="chip">{swatch(i.get("color"))}<span>{i["name"]}</span>'
        f'<span class="chip-tag">{i["weather"]}</span></div>'
        for i in items
    )
    return f'<div class="chip-row">{chips}</div>'


def render_outfit_card(category, piece):
    icon = CATEGORY_ICON[category]
    label = category.capitalize()
    if piece["name"]:
        body = f'{swatch(piece["color"])}<span class="card-item">{piece["name"]}</span>'
    else:
        body = '<span class="card-item card-empty">Nothing saved for this yet</span>'
    return f'''
    <div class="outfit-card">
        <div class="outfit-card-label">{icon} {label}</div>
        <div class="outfit-card-body">{body}</div>
    </div>
    '''


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg: #F0EFEC;
    --surface: #FAF9F7;
    --surface-2: #E9E7E2;
    --text: #2B2822;
    --text-muted: #7C7669;
    --gold: #B8863A;
    --border: #DEDAD1;
}

.stApp { background: var(--bg); color: var(--text); }

h1, h2, h3 { font-family: 'Fraunces', serif !important; color: var(--text) !important; letter-spacing: -0.01em; }
h1 { font-weight: 700 !important; }
p, span, label, li { font-family: 'Inter', sans-serif; }

[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
}

[data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.stButton > button, [data-testid="stFormSubmitButton"] button {
    background: var(--gold) !important;
    color: #201A10 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.08); }

/* closet chips */
.chip-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.4rem 0 1.2rem 0; }
.chip {
    display: flex; align-items: center; gap: 0.4rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 0.35rem 0.8rem 0.35rem 0.5rem;
    font-family: 'Inter', sans-serif; font-size: 0.85rem; color: var(--text);
}
.chip-tag { color: var(--text-muted); font-size: 0.72rem; border-left: 1px solid var(--border); padding-left: 0.4rem; margin-left: 0.1rem; }
.swatch { width: 12px; height: 12px; border-radius: 50%; display: inline-block; border: 1px solid rgba(0,0,0,0.15); }
.swatch-empty { background: transparent; border: 1px dashed var(--text-muted); }
.empty-note { color: var(--text-muted); font-size: 0.85rem; font-style: italic; }

/* weather result box */
.weather-box {
    background: var(--surface); border-radius: 14px; padding: 1.2rem 1.5rem;
    border-left: 5px solid var(--accent, var(--gold)); margin: 0.8rem 0 1.2rem 0;
}
.weather-temp { font-family: 'JetBrains Mono', monospace; font-size: 2.4rem; font-weight: 700; color: var(--text); line-height: 1; }
.weather-sub { color: var(--text-muted); font-family: 'Inter', sans-serif; font-size: 0.9rem; margin-top: 0.3rem; }

/* advice + tips */
.advice-box {
    background: var(--surface); border: 1px solid var(--border); border-left: 5px solid var(--gold);
    border-radius: 10px; padding: 1rem 1.3rem; font-family: 'Inter', sans-serif; color: var(--text);
}
.tip-line { color: var(--text-muted); font-family: 'Inter', sans-serif; font-size: 0.9rem; margin: 0.15rem 0; }

/* outfit cards */
.outfit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; margin-top: 0.6rem; }
.outfit-card {
    background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--accent, var(--gold));
    border-radius: 12px; padding: 0.9rem 1rem;
}
.outfit-card-label { font-family: 'Inter', sans-serif; font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.3rem; }
.outfit-card-body { display: flex; align-items: center; gap: 0.5rem; font-family: 'Inter', sans-serif; font-weight: 500; }
.card-empty { color: var(--text-muted); font-weight: 400; font-style: italic; font-size: 0.85rem; }
</style>
"""

st.set_page_config(page_title="MyOutfit", page_icon="🧵", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

st.title("MyOutfit")
st.header("My Digital Wardrobe")

wardrobe = load_wardrobe()

with st.form("add_clothes_form"):
    st.subheader("Add a New Item")
    item_name = st.text_input("What is it? (e.g., Black Hoodie, Blue Jeans)")
    category = st.selectbox("Category", ["tops", "bottoms", "shoes", "outerwear"])
    weather_tag = st.selectbox("Best for weather:", ["Hot", "Mild", "Cold", "Rain"])
    color = st.text_input("Main Color (e.g., Black, White, Blue)")

    submitted = st.form_submit_button("Save to Wardrobe")
    if submitted and item_name and color:
        wardrobe[category].append({
            "name": item_name,
            "weather": weather_tag,
            "color": color.strip().title(),
        })
        save_wardrobe(wardrobe)
        st.success(f"Added {color.strip().title()} {item_name}!")

st.subheader("Current Closet")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**{CATEGORY_ICON['tops']} Tops**", unsafe_allow_html=True)
    st.markdown(render_chips(wardrobe["tops"]), unsafe_allow_html=True)
    st.markdown(f"**{CATEGORY_ICON['bottoms']} Bottoms**", unsafe_allow_html=True)
    st.markdown(render_chips(wardrobe["bottoms"]), unsafe_allow_html=True)
with col2:
    st.markdown(f"**{CATEGORY_ICON['shoes']} Shoes**", unsafe_allow_html=True)
    st.markdown(render_chips(wardrobe["shoes"]), unsafe_allow_html=True)
    st.markdown(f"**{CATEGORY_ICON['outerwear']} Outerwear**", unsafe_allow_html=True)
    st.markdown(render_chips(wardrobe["outerwear"]), unsafe_allow_html=True)

result_box = st.empty()

city = st.text_input("City name")

if city:
    region = st.selectbox("Optimize recommendations for:", ["Indian", "Global"])
    generate = st.button("Recommend an Outfit")

    if generate:
        result_box.empty()

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
        )

        if response.status_code == 200 and response.text:
            data = response.json()
            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]
            weather_main = data["weather"][0]["main"]
            tag = weather_tag_for(temp, weather_main)
            accent = ACCENT[tag]["color"]

            with result_box.container():
                st.markdown(
                    f'''<div class="weather-box" style="--accent:{accent}">
                        <div class="weather-temp">{temp}°C</div>
                        <div class="weather-sub">{ACCENT[tag]["icon"]} {weather_main} in {city} &nbsp;·&nbsp; {humidity}% humidity</div>
                    </div>''',
                    unsafe_allow_html=True,
                )

            tips = []
            if weather_main == "Rain":
                tips += ["Carry an umbrella or raincoat", "Avoid suede or fancy footwear", "Watch out for your hair in the rain"]
            if humidity >= 70:
                tips.append("High humidity - go for breathable fabric")

            if region == "Indian":
                if temp < -1:
                    outfit_advice = "Freezing. Stay indoors if you can, wear fleece or wool, snow boots."
                elif temp < 12:
                    outfit_advice = "Chilly. Layer up (3 layers), heavy jacket, closed shoes."
                elif temp < 19:
                    outfit_advice = "Cold-ish. Two layers, long sleeves, bring a jacket."
                elif temp < 29:
                    outfit_advice = "Pretty warm. One layer, cotton, t-shirts are fine."
                elif temp < 35:
                    outfit_advice = "Hot. Loose cotton, breathable fabric."
                else:
                    outfit_advice = "Heat wave. Stay hydrated, wear sunscreen, avoid dark colors."
                st.caption("Optimized for Indian conditions")
            else:
                if temp < -1:
                    outfit_advice = "Freezing. Heavy coat, thermal wear, stay warm."
                elif temp < 6:
                    outfit_advice = "Chilly. Heavy winter coat, thermal wear, snow boots."
                elif temp < 16:
                    outfit_advice = "Slightly cold. Jacket or sweater, closed shoes."
                elif temp < 26:
                    outfit_advice = "Comfortable. Light, casual clothes."
                else:
                    outfit_advice = "Hot. Light, breathable clothing."
                st.caption("Using global comfort standards")

            st.subheader("General Advice")
            st.markdown(f'<div class="advice-box">{outfit_advice}</div>', unsafe_allow_html=True)

            if tips:
                st.subheader("Extra Tips")
                for t in tips:
                    st.markdown(f'<div class="tip-line">• {t}</div>', unsafe_allow_html=True)

            st.header("Your Personal Wardrobe Recommendation")
            st.markdown(
                f'<span style="color:var(--text-muted)">Looking for <b style="color:{accent}">{tag}</b> weather clothes...</span>',
                unsafe_allow_html=True,
            )

            outfit = pick_outfit(wardrobe, tag)
            cards = "".join(render_outfit_card(cat, outfit[cat]) for cat in ["tops", "bottoms", "shoes", "outerwear"])
            st.markdown(f'<div class="outfit-grid" style="--accent:{accent}">{cards}</div>', unsafe_allow_html=True)
        else:
            st.error("Failed to fetch weather data")
