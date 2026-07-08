import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import asyncio
import edge_tts
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import base64
import requests
# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="DevaPath - AI Temple Guide",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="collapsed"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# Agar login nahi hua hai to Login page par bhejo
if not st.session_state.logged_in:
    st.switch_page("pages/Login.py")
    st.stop()
# ==========================================
# ENVIRONMENT & AI SETUP
# ==========================================
load_dotenv(override=True)
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

async def generate_voice(text):
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-IN-NeerjaNeural"
    )
    await communicate.save("guide.mp3")
#########################################
# Weather api key
#########################################
weather_api_key = os.getenv("OPENWEATHER_API_KEY")
@st.cache_data(ttl=1800)
def get_weather(lat, lon):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": weather_api_key, "units": "metric"}
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if res.status_code == 200:
            return {
                "temp": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "description": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"],
                "humidity": data["main"]["humidity"],
            }
        else:
            st.write("DEBUG ERROR:", data)  
        return None
    except Exception as e:
        st.write("DEBUG EXCEPTION:", e)  
        return None


def get_weather_emoji(main_condition, description):
    """Map weather condition to a clean flat icon (emoji) similar to reference design."""
    condition = (main_condition or "").lower()
    desc = (description or "").lower()
    if "thunder" in condition or "thunder" in desc:
        return "⛈️"
    if "rain" in condition or "drizzle" in condition:
        return "🌧️"
    if "snow" in condition:
        return "❄️"
    if "mist" in condition or "fog" in condition or "haze" in condition:
        return "🌫️"
    if "clear" in condition:
        return "☀️"
    if "cloud" in condition:
        return "☁️"
    return "☁️"


def get_rain_chance(description, humidity):
    """Heuristic rain-chance label since current-weather API has no 'pop' field."""
    desc = (description or "").lower()
    if "thunder" in desc or "rain" in desc or "drizzle" in desc:
        return "High"
    if "cloud" in desc and (humidity or 0) >= 65:
        return "Medium"
    return "Low"


def get_best_time(temp):
    """Heuristic best-visit-time based on current temperature."""
    if temp is None:
        return "Morning"
    if temp >= 35:
        return "Evening"
    if temp <= 15:
        return "Afternoon"
    return "Morning"


def get_travel_conditions(verdict):
    """Map safety verdict to a short travel-conditions label."""
    mapping = {
        "Safe": "Good",
        "Caution": "Moderate",
        "Not Recommended": "Poor",
    }
    return mapping.get(verdict, "Moderate")

##################################################
#NEWSAPI_KEY
###################################################
newsapi_key = os.getenv("NEWSAPI_KEY")

@st.cache_data(ttl=3600)  # 1 hour cache
def get_disaster_news(city, state):
    try:
        query = f'({city} OR {state}) AND (flood OR earthquake OR cyclone OR disaster OR landslide OR riot OR curfew OR accident)'
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": newsapi_key
        }
        res = requests.get(url, params=params, timeout=6)
        data = res.json()
        if res.status_code == 200 and data.get("articles"):
            return [a["title"] for a in data["articles"]]
        return []
    except Exception:
        return []


@st.cache_data(ttl=1800)
def get_safety_verdict(temple_name, city, state, weather_desc, news_headlines):
    headlines_text = "\n".join(f"- {h}" for h in news_headlines) if news_headlines else "No recent disaster-related news found."

    prompt = f"""
You are a travel safety advisor for DevaPath temple guide app.

Temple: {temple_name}
Location: {city}, {state}
Current weather: {weather_desc}

Recent news headlines related to disasters/incidents in this area:
{headlines_text}

Based on this information, give a safety verdict for someone planning to visit this temple RIGHT NOW.

Respond ONLY in this exact format:
VERDICT: [Safe / Caution / Not Recommended]
REASON: [1-2 short sentences explaining why, max 30 words]

Do not add any other text.
"""
    response = llm.invoke(prompt)
    return response.content

# CUSTOM CSS
# ==========================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap" rel="stylesheet">
""",unsafe_allow_html=True)
st.markdown("""
<style>
.stApp{
background:linear-gradient(180deg,#120B08,#1B120C,#22140D);
color:white;
}
/* Header Title */
.hero-title{

font-family:'Cinzel',serif;

font-size:58px;

font-weight:900;

color:#FFC107;

letter-spacing:1px;

text-shadow:

0 0 8px rgba(255,193,7,.45),

0 0 18px rgba(255,140,0,.35);

}
            
/*Cards*/
.card{

background:#2B1B11;

border:2px solid #F59E0B;

border-radius:20px;

padding:22px;

box-shadow:0 0 20px rgba(255,165,0,.18);

transition:.35s;

}

.card:hover{

transform:translateY(-4px);

box-shadow:0 0 35px rgba(255,165,0,.45);

}


/* Button Styles */
.login-btn {
    background: #F59E0B;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 8px;
    margin-right: 10px;
    font-weight: bold;
}
.signup-btn {
    background: #2563EB;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 8px;
    font-weight: bold;
}
            
.stButton>button{

background:linear-gradient(90deg,#F59E0B,#F97316);

color:white;

font-weight:bold;

border:none;

border-radius:12px;

height:48px;

transition:.3s;

}

.stButton>button:hover{

background:#FFD54F;

color:black;

transform:scale(1.03);
}   

/*sidebar*/              
section[data-testid="stSidebar"]{

background:#24140B;

border-right:2px solid #F59E0B;

}   

iframe{
    border-radius:20px !important;
    border:3px solid #F59E0B !important;
} 

.ai-avatar{
    width:140px;
    height:140px;
    border-radius:50%;
    border:5px solid #FFC107;
    box-shadow:0 0 35px rgba(255,165,0,0.7);
    object-fit:cover;
    margin-bottom:15px;
}

.guide-card{
    background:linear-gradient(145deg,#2B1B11,#3A2415);
    border:2px solid #F59E0B;
    border-radius:20px;
    padding:20px;
    text-align:center;
    box-shadow:0 0 25px rgba(255,165,0,.25);
    transition:.3s;
}
  .guide-card img{
    display:block;
    margin:auto;
    width:170px !important;
    height:170px !important;
    border-radius:50%;
    object-fit:cover;
    border:5px solid #FFC107;
    box-shadow:0 0 30px rgba(255,193,7,.6);
}

.guide-card:hover{
    transform:translateY(-5px);
    box-shadow:0 0 40px rgba(255,165,0,.5);
}

.guide-name{
    color:#FFC107;
    font-size:24px;
    font-weight:bold;
    margin-top:10px;
}

.guide-role{
    color:#FFD54F;
    font-size:15px;
}

.guide-tag{
    margin:8px 0;
    color:#F8FAFC;
    font-size:15px;
}            
.card{

animation:fadeIn .7s ease;

}

@keyframes fadeIn{

from{

opacity:0;

transform:translateY(20px);

}

to{

opacity:1;

transform:translateY(0);

}

}
            

/* Columns ko equal height banane ke liye — sirf sabse aakhri card ko stretch karo,
   map/weather apni natural (fixed) height me hi rahenge, isse koi black gap nahi banega */
div[data-testid="stHorizontalBlock"]{
    align-items:stretch;
}

div[data-testid="stColumn"]{
    display:flex;
    flex-direction:column;
}

div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]{
    display:flex;
    flex-direction:column;
    flex:1;
}

div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div:last-child{
    flex:1;
    display:flex;
    flex-direction:column;
    # justify-content:flex-end;        
}
.equal-height-card{
    display:flex;
    flex-direction:column;
    height:100%;
}

.bottom-fill{
    flex:1;
    display:flex;
    flex-direction:column;
    justify-content:center;
}            
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA LOADING & SESSION STATE
# ==========================================
@st.cache_data
def load_data():
    # Make sure your JSON file path is correct
    try:
        with open("data/processed/temples_master_fixed.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback dummy data if file is missing during testing
        return [{"id": "1", "name": "Kashi Vishwanath", "city": "Varanasi", "state": "UP", "deity": "Shiva", "lat": 25.3109, "lon": 83.0076, "opening_time": "3:00 AM", "closing_time": "11:00 PM", "entry_fee": "Free", "dress_code": "Traditional", "history": "Ancient temple of Lord Shiva..."}]

temples = load_data()

if "selected_temple" not in st.session_state:
    st.session_state.selected_temple = temples[0]


# ==========================================
# LOGO KO BASE64 ME CONVERT KARO (top par ek baar)
# ==========================================
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("assets/logo_temple_dark_bg.png")

# ==========================================
# TOP BAR
# ==========================================

top_col1, top_col2 = st.columns([5, 2])
with top_col1:
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;">

<div style="
    width:250px;
    height:250px;
    border-radius:50%;
    overflow:hidden;
    flex-shrink:0;
">
<img src="data:image/png;base64,{logo_base64}" style="width:120%;height:120%;object-fit:cover;">
</div>

<div class="hero-title">
DevaPath
<br>
<span style="font-size:32px;">
AI Temple Guide
</span>
</div>

</div>
""", unsafe_allow_html=True)
    
with top_col2:

    st.markdown(
        f"""
        <div style="text-align:right;">
            <h4>👤 {st.session_state.username}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🚪 Logout", use_container_width=True):

        # Session clear
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.email = ""

        # Login page par bhejo
        st.switch_page("pages/Login.py")

st.markdown("---")

# ==========================================
# INTERACTIVE MAP
# ==========================================

row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.markdown("### 🗺️ India Map")
    m = folium.Map(location=[21.5, 78.5], zoom_start=5, tiles="OpenStreetMap")
    for temple in temples:
        if temple.get("lat") is None or temple.get("lon") is None:
            continue
        folium.Marker(
            [temple["lat"], temple["lon"]],
            popup=temple["id"],
            tooltip=temple["name"],
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)
    map_data = st_folium(m, height=460, use_container_width=True, returned_objects=["last_object_clicked_popup"])

    # Card End
    st.markdown("""
<div style="background:#2B1B11;border:2px solid #F59E0B;border-radius:18px;padding:16px;margin-top:12px;text-align:center;flex:1;display:flex;flex-direction:column;justify-content:center;">
<h3 style="color:#FFC107; margin:0;">🛕 Select a Temple to Explore</h3>
</div>
""", unsafe_allow_html=True)

    if map_data and map_data.get("last_object_clicked_popup"):
        clicked = map_data["last_object_clicked_popup"]
        for temple in temples:
            if str(temple["id"]) == str(clicked):
                st.session_state.selected_temple = temple
                break

t_info = st.session_state.selected_temple


# ==========================================
# WEATHER INFO + SAFETY ADVISORY (Side Panel)
# ==========================================

with row1_col2:

    # ---------- WEATHER CARD ----------
    st.markdown("### 🌤️ Weather Info")

    weather = get_weather(t_info.get("lat"), t_info.get("lon"))

    if weather:
        weather_icon = get_weather_emoji(weather.get("main"), weather["description"])
        st.markdown(f"""
<div style="background:linear-gradient(145deg,#2B1B11,#3A2415);border:2px solid #F59E0B;border-radius:22px;padding:24px 20px;box-shadow:0 0 18px rgba(245,158,11,0.2);">
<div style="display:flex;align-items:center;justify-content:center;gap:18px;">
<span style="font-size:56px;line-height:1;filter:drop-shadow(0 0 10px rgba(255,255,255,.35));">{weather_icon}</span>
<h1 style="color:#FFC107;font-size:44px;margin:0;font-family:'Cinzel',serif;line-height:1;">{weather['temp']}°C</h1>
</div>
<p style="color:#F8FAFC;font-size:16px;font-weight:600;text-align:center;margin:14px 0 18px 0;">{weather['description']}</p>
<div style="display:flex;justify-content:space-around;border-top:1px solid rgba(245,158,11,.3);padding-top:14px;">
<div style="text-align:center;">
<p style="color:#94A3B8;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;">FEELS LIKE</p>
<p style="color:#FFC107;font-size:18px;font-weight:bold;margin:0;">{weather['feels_like']}°C</p>
</div>
<div style="text-align:center;">
<p style="color:#94A3B8;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;">HUMIDITY</p>
<p style="color:#FFC107;font-size:18px;font-weight:bold;margin:0;">{weather['humidity']}%</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        weather_desc = weather['description']
    else:
        st.markdown("""
<div style="background:#2B1B11;border:2px solid #F59E0B;border-radius:22px;padding:24px;text-align:center;color:#94A3B8;">
🌥️ Weather data abhi available nahi hai.
</div>
""", unsafe_allow_html=True)
        weather_desc = "Unknown"

    # Spacer between Weather card and Safety card
    st.markdown('<div style="margin-top:6px;"></div>', unsafe_allow_html=True)

    # ---------- SAFETY ALERT CARD ----------

    # st.markdown("### 🚨 Safety Advisory")
    st.markdown(
        '<h3 style="margin-bottom:6px; margin-top:16px;">🚨 Safety Advisory</h3>',
        unsafe_allow_html=True
    )
    news_headlines = get_disaster_news(t_info.get("city"), t_info.get("state"))

    with st.spinner("Checking safety status..."):
        verdict_raw = get_safety_verdict(
            t_info.get("name"), t_info.get("city"), t_info.get("state"),
            weather_desc, news_headlines
        )

    # Parse LLM verdict output
    verdict = "Safe"
    reason = "No major issues detected."
    for line in verdict_raw.split("\n"):
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip()
        if line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()

    color_map = {"Safe": "#22C55E", "Caution": "#F59E0B", "Not Recommended": "#EF4444"}
    icon_map = {"Safe": "✅", "Caution": "⚠️", "Not Recommended": "🚫"}
    badge_color = color_map.get(verdict, "#F59E0B")
    badge_icon = icon_map.get(verdict, "⚠️")

    # Derived quick-glance stats to match the reference design
    rain_chance = get_rain_chance(weather_desc, weather.get("humidity") if weather else None)
    best_time = get_best_time(weather.get("temp") if weather else None)
    travel_conditions = get_travel_conditions(verdict)

    st.markdown(f"""
<div style="background:linear-gradient(145deg,#2B1B11,#3A2415);border:2px solid {badge_color};border-radius:22px;padding:22px;box-shadow:0 0 18px {badge_color}55;">
<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
<span style="font-size:24px;">{badge_icon}</span>
<span style="color:{badge_color};font-size:19px;font-weight:bold;">{verdict}</span>
</div>
<p style="color:#E2E8F0;font-size:14px;margin:0 0 16px 0;">{reason}</p>
<div style="display:flex;justify-content:space-around;border-top:1px solid rgba(245,158,11,.3);padding-top:14px;">
<div style="text-align:center;">
<div style="font-size:20px;">🌧️</div>
<p style="color:#94A3B8;font-size:11px;letter-spacing:.5px;margin:6px 0 4px 0;">Rain Chance</p>
<p style="color:#F8FAFC;font-size:14px;font-weight:bold;margin:0;">{rain_chance}</p>
</div>
<div style="text-align:center;">
<div style="font-size:20px;">🕐</div>
<p style="color:#94A3B8;font-size:11px;letter-spacing:.5px;margin:6px 0 4px 0;">Best Time</p>
<p style="color:#F8FAFC;font-size:14px;font-weight:bold;margin:0;">{best_time}</p>
</div>
<div style="text-align:center;">
<div style="font-size:20px;">🚗</div>
<p style="color:#94A3B8;font-size:11px;letter-spacing:.5px;margin:6px 0 4px 0;">Travel Conditions</p>
<p style="color:#F8FAFC;font-size:14px;font-weight:bold;margin:0;">{travel_conditions}</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ==========================================
# ROW 2: TEMPLE VIEW + TEMPLE INFORMATION
# ==========================================
row3_col1, row3_col2 = st.columns([2, 1])

with row3_col1:
    st.markdown("### 📸 Temple View")

    selected_img = t_info.get("image")

    if selected_img:
        image_path = os.path.join("assets", "temples", selected_img)

        if os.path.exists(image_path):
            st.image(
                image_path,
                caption=f"🛕 {t_info['name']}",
                use_container_width=True
            )
        else:
            st.error(f"Image not found: {selected_img}")
    else:
        st.info("No image available for this temple.")

with row3_col2:
    st.markdown("### 🏛️ Temple Information")

    st.markdown(f"""
    <div style="
        background:linear-gradient(145deg,#2B1B11,#3A2415);
        border:2px solid #F59E0B;
        border-radius:18px;
        padding:22px;
        box-shadow:0 0 18px rgba(245,158,11,0.25);
    ">

    <h3 style="
        color:#FFC107;
        text-align:center;
        margin-bottom:20px;">
        🛕 {t_info.get('name')}
    </h3>

    <p style="font-size:16px;">
        📍 <b>Location</b><br>
        {t_info.get('city')}, {t_info.get('state')}
    </p>

    <hr>

    <p style="font-size:16px;">
        🙏 <b>Deity</b><br>
        {t_info.get('deity')}
    </p>

    <hr>

    <p style="font-size:16px;">
        🕒 <b>Timings</b><br>
        {t_info.get('opening_time')} - {t_info.get('closing_time')}
    </p>

    <hr>

    <p style="font-size:16px;">
        🎫 <b>Entry Fee</b><br>
        {t_info.get('entry_fee',"Free")}
    </p>

    <hr>

    <p style="font-size:16px;">
        👕 <b>Dress Code</b><br>
        {t_info.get('dress_code',"Traditional Indian Wear")}
    </p>

    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ==========================================
# ROW 3: AI GUIDE (Left) & DETAILS (Right)
# ==========================================
row2_col1, row2_col2 = st.columns([1, 2])

with row2_col1:
    st.markdown("### 🧠 AI Guide")

    image_path = os.path.join("assets", "shivangi_guide.png")

    # st.markdown('<div class="guide-card">', unsafe_allow_html=True)

    # Avatar
    if os.path.exists(image_path):
        st.image(image_path, width=180)
    else:
        st.warning("⚠️ Image not found: assets/shivangi_guide.png")

    # Guide Info
    st.markdown("""
    <div class="guide-name" style="font-size: 22px; font-weight: bold;">
        ✨Shivangi
    </div>

    <div class="guide-role" style="font-size: 16px;">
        Temple AI Guide
    </div>

    <hr style="border:1px solid rgba(255,193,7,.4);">

    <div class="guide-tag" style="font-size: 16px;">
        <p style="font-size: 16px;">🕉️ Your Divine Story Teller</p>
    </div>
    """, unsafe_allow_html=True)

    # st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button(
        f"🎤 Tell Story of {t_info.get('name','Temple')}",
        use_container_width=True,
    ):

        with st.spinner("🤖 Shivangi is telling the story..."):

            story = t_info.get(
                "story",
                "No story is available for this temple."
            )

            prompt = f"""
You are Shivangi, the AI Story Guide of DevaPath.

Narrate ONLY the famous story or legend of the selected temple.

Temple:
{t_info.get('name')}

Story:
{story}

Instructions:
- Start with: "Namaste! I am Shivangi, your AI guide."
- Narrate ONLY the story.
- Do NOT explain history.
- Do NOT explain architecture.
- Do NOT explain festivals.
- Do NOT explain aarti timings.
- Speak in simple English.
- Keep the narration engaging.
- Maximum 2 minutes.
"""

            response = llm.invoke(prompt)
            ai_text = response.content

        st.success("✅ Story Ready!")
        st.write(ai_text)

        asyncio.run(generate_voice(ai_text))

        with open("guide.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)

# ==========================================
# TEMPLE DETAILS
# ==========================================
with row2_col2:

    st.markdown("## 📖 Temple Details")

    history = t_info.get("history", {})

    if isinstance(history, dict):

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(f"""
            <div class="card">
            <h4 style="font-size: 19px;">🕉 Overview</h4>
            <p style="font-size: 16px; line-height: 1.5;">{history.get("overview","Not Available")}</p>
            </div>
            """,unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
            <h4 style="font-size: 19px;">🏛 Built By</h4>
            <p style="font-size: 16px; line-height: 1.5;">{history.get("built_by","Not Available")}</p>
            </div>
            """,unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
            <h4 style="font-size: 19px;">📍 Location</h4>
            <p style="font-size: 16px; line-height: 1.5;">{history.get("location","Not Available")}</p>
            </div>
            """,unsafe_allow_html=True)


        with col2:

            st.markdown(f"""
            <div class="card">
            <h4 style="font-size: 19px;">🏛 Architecture</h4>
            <p style="font-size: 16px; line-height: 1.5;">{history.get("architecture","Not Available")}</p>
            </div>
            """,unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
            <h4 style="font-size: 19px;">⭐ Importance</h4>
            <p style="font-size: 16px; line-height: 1.5;">{history.get("importance","Not Available")}</p>
            </div>
            """,unsafe_allow_html=True)

    else:

        st.markdown(f"""
        <div class="card">
        <p style="font-size: 16px; line-height: 1.5;">{history}</p>
        </div>
        """,unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🎉 Major Festivals")

    festivals = t_info.get("festivals", [])

    if isinstance(festivals, list):
        for festival in festivals:
            st.markdown(f"<p style='font-size:16px;'>🎊 {festival}</p>", unsafe_allow_html=True)
    else:
        st.write(festivals)

st.markdown("---")

# ==========================================
# ROW 4: AARTI SCHEDULE (CUSTOM DESIGN)
# ==========================================
st.markdown("### 🔔 Aarti Schedule")

# Selected temple ka aarti data nikalo
aarti_data = t_info.get("aarti", {})

if aarti_data:
    for aarti_name, details in aarti_data.items():
        # Aarti ke naam ko thoda saaf dikhane ke liye (e.g. 'mangala_aarti' -> 'Mangala')
        clean_name = aarti_name.replace("_aarti", "").replace("_alati", "").replace("_seva", "").replace("_", " ").title()
        time_str = details.get("time", "N/A")
        desc_str = details.get("description", "")
        
        # Exact image jaisa dark green bar design
        st.markdown(f"""
        <div style="
            background-color: #3B220E; 
            padding: 14px 20px; 
            border-radius: 8px; 
            margin-bottom: 10px; 
            border-left:8px solid #F59E0B;
            display: flex;
            align-items: center;
        ">
            <span style="font-size: 22px; margin-right: 15px;">🙏</span>
            <span style="color:#FFC107; font-weight: bold; font-size: 18px;">{clean_name} :</span>
            <span style="color: #E2E8F0; font-size: 18px; margin-left: 8px; font-weight: 600;">{time_str}</span>
            <span style="color: #CBD5E1; font-size: 16px; margin-left: auto; max-width: 55%; text-align: right; line-height: 1.4;">{desc_str}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Iss temple ki aarti timings abhi update nahi hui hain.")



# ==========================================
# CONTINUE EXPLORING BUTTON
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("Continue Exploring", use_container_width=True):
        # Selected temple ko Explore page ke liye save karo
        st.session_state.selected_temple = t_info

        # Explore page open karo
        st.switch_page("pages/Explore.py")

st.markdown("---")

# ==========================================
# ROW 5: REVIEWS
# ==========================================
st.markdown("### ❤️ Devotee Reviews")
st.markdown("""
<div class="card">

<h4>⭐⭐⭐⭐⭐ Divine Experience</h4>

<p>
"The temple was amazing. The atmosphere was peaceful and the aarti was unforgettable."
</p>

<b>- Rahul Sharma</b>

</div>

<br>

<div class="card">

<h4>⭐⭐⭐⭐ Peaceful Darshan</h4>

<p>
"Very beautiful temple with positive vibes. Highly recommended."
</p>

<b>- Priya Verma</b>

</div>
""",unsafe_allow_html=True)

# ==========================================
# ROW 6: FOOTER
# ==========================================

st.markdown("""
<div style="
    text-align:center;
    padding:20px 0;
    margin-top:40px;
    border-top:2px solid #F59E0B;
    color:#FFD54F;
    font-size:16px;
    font-weight:500;
">
    © 2026 <b>DevaPath</b> | Developed by <b>Team Synergy</b>
</div>
""", unsafe_allow_html=True)
