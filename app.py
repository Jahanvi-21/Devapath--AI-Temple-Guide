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
load_dotenv()
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

# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
.stApp{
    background:#0F172A;
    color:white;
}
/* Header Title */
.hero-title {
    color: #F59E0B;
    font-size: 48px;
    font-weight: 900;
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
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
# TOP BAR
# ==========================================

top_col1, top_col2 = st.columns([5, 2])
with top_col1:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:18px;">
            <div style="font-size:60px;">🛕</div>
            <div class="hero-title">DevaPath – AI Temple Guide</div>
        </div>
        """,
        unsafe_allow_html=True
    )
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

row1_col1,row1_col2=st.columns([2,1])

with row1_col1:
    st.markdown("### 🗺️ India Map")
    m=folium.Map(location=[21.5,78.5],zoom_start=5,tiles="OpenStreetMap")
    for temple in temples:
        if temple.get("lat") is None or temple.get("lon") is None:
            continue
        folium.Marker([temple["lat"],temple["lon"]],popup=temple["id"],tooltip=temple["name"],icon=folium.Icon(color="orange",icon="star")).add_to(m)
    map_data=st_folium(m,height=460,use_container_width=True,returned_objects=["last_object_clicked_popup"])
    if map_data and map_data.get("last_object_clicked_popup"):
        clicked=map_data["last_object_clicked_popup"]
        for temple in temples:
            if str(temple["id"])==str(clicked):
                st.session_state.selected_temple=temple
                break

t_info=st.session_state.selected_temple

with row1_col2:
    st.markdown("### 🏛️ Temple Information")
    st.markdown(f"""
    <div class="card">
    <h4 style="color:#F59E0B;">{t_info.get('name')}</h4>
    <p><b>📍 Location:</b> {t_info.get('city')}, {t_info.get('state')}</p>
    <p><b>🙏 Deity:</b> {t_info.get('deity')}</p>
    <p><b>🕐 Timings:</b> {t_info.get('opening_time')} - {t_info.get('closing_time')}</p>
    </div>
    """,unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# ROW 2: AI GUIDE (Left) & DETAILS (Right)
# ==========================================
row2_col1, row2_col2 = st.columns([1, 2])
with row2_col1:
    st.markdown("### 👩 Shivangi AI Guide")
    
    # Helper to load local image into HTML
    def get_image_as_base64(path):
        try:
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            return "" # Fallback if image is missing

    guide_img_base64 = get_image_as_base64("assets/shivangi_guide.png")
    img_src = f"data:image/png;base64,{guide_img_base64}" if guide_img_base64 else "https://api.dicebear.com/7.x/bottts/svg?seed=Shivangi&backgroundColor=F59E0B"
    
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <img src="{img_src}" width="120" style="border-radius: 50%; object-fit: cover; height: 120px;">
        <h4 style="color:#f59e0b; margin-bottom:5px;">Shivangi</h4>
        <p style="font-size: 14px;">Your AI Audio Guide</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button(f"🎤 Explain {t_info.get('name', 'Temple')}", use_container_width=True):

        with st.spinner("🤖 Shivangi is generating audio..."):

            aarti = ""
            if t_info.get("aarti"):
               for name, info in t_info["aarti"].items():
                clean = (
                    name.replace("_aarti", "")
                        .replace("_seva", "")
                        .replace("_", " ")
                        .title()
                )
                aarti += f"{clean}: {info.get('time','N/A')}. "

        # ✅ PROMPT (OUTSIDE LOOP)
        prompt = f"""
You are Shivangi, the AI Guide of DevaPath.

Start like:
"Namaste and welcome to DevaPath. I am Shivangi, Your personaL AI guide..."

Temple: {t_info.get('name')}
City: {t_info.get('city')}
State: {t_info.get('state')}
Deity: {t_info.get('deity')}

History:
{t_info.get("history","Not available")}

Architecture:
{t_info.get("architecture","Not available")}

Festivals:
{t_info.get("festivals","Not available")}

Aarti:
{aarti if aarti else "Not available"}

Rules:
- Only use given data
- Do not invent anything
"""

        response = llm.invoke(prompt)
        ai_text = response.content

        st.success("✅ Explanation Ready!")
        st.write(ai_text)

        asyncio.run(generate_voice(ai_text))

        with open("guide.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)


with row2_col2:
    st.markdown("### 📖 Temple Details")
    tab1, tab2, tab3 = st.tabs(["📖 History", "🏛️ Architecture", "🎉 Festivals"])
    
    with tab1:
        st.write(t_info.get("history", "History details not available."))
    with tab2:
        st.write(t_info.get("architecture", "Architecture details are not available for this temple yet."))
    with tab3:
        festivals = t_info.get("festivals", [])

        if isinstance(festivals, list):
            for festival in festivals:
                st.markdown(f"🎉 {festival}")
        else:
            st.write(festivals)
st.markdown("---")

# ==========================================
# ROW 3: TEMPLE VIEW
# ==========================================
st.markdown("### 📸 Temple View")

selected_img = t_info.get("image")

c1, c2, c3 = st.columns([1, 2.5, 1])

with c2:
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
            background-color: #0F3D3E; 
            padding: 12px 20px; 
            border-radius: 8px; 
            margin-bottom: 10px; 
            border: 1px solid #145A5B;
            display: flex;
            align-items: center;
        ">
            <span style="font-size: 18px; margin-right: 15px;">🙏</span>
            <span style="color: #4ADE80; font-weight: bold; font-size: 15px;">{clean_name} :</span>
            <span style="color: #E2E8F0; font-size: 15px; margin-left: 8px; font-weight: 600;">{time_str}</span>
            <span style="color: #94A3B8; font-size: 13px; margin-left: auto;">{desc_str}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Iss temple ki aarti timings abhi update nahi hui hain.")

st.markdown("---")

# ==========================================
# ROW 5: REVIEWS
# ==========================================
st.markdown("### ❤️ Devotee Reviews")
st.markdown("""
<div class="card" style="margin-bottom: 10px;">
    <b>⭐⭐⭐⭐⭐ Beautiful temple experience</b><br>
    <span style="color:#CBD5E1; font-size:14px;">"The aarti was mesmerizing and the premises were very clean. Must visit!" - Rahul D.</span>
</div>
<div class="card">
    <b>⭐⭐⭐⭐ Peaceful and divine</b><br>
    <span style="color:#CBD5E1; font-size:14px;">"Very crowded on weekends, but the darshan was very fulfilling." - Priya S.</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ROW 6: FOOTER
# ==========================================
st.markdown("""
<div style="
    text-align:center;
    color:#94A3B8;
    padding:20px;
    margin-top:30px;
    font-size:14px;
    border-top:1px solid rgba(255,255,255,0.12);
">
    © 2026 <b style="color:#F59E0B;">DevaPath</b> | JSL Works Summer Internship Project
</div>
""", unsafe_allow_html=True)