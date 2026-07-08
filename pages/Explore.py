import streamlit as st



st.set_page_config(
    page_title="Explore Around Temple",
    page_icon="🗺️",
    layout="wide"
)

# -----------------------------
# Check if temple is selected
# -----------------------------
if "selected_temple" not in st.session_state:
    st.warning("Please select a temple first.")
    st.switch_page("app.py")

temple = st.session_state.selected_temple

# -----------------------------
# Fonts (same as app.py)
# -----------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# -----------------------------
# Theme CSS (matches app.py)
# -----------------------------
st.markdown("""
<style>

.stApp{
    background:linear-gradient(180deg,#120B08,#1B120C,#22140D);
    color:white;
}

/* Page Header */
.explore-hero{
    font-family:'Cinzel',serif !important;
    font-size:80px !important;
    line-height:1.1 !important;
    font-weight:900 !important;
    color:#FFC107 !important;
    text-align:center !important;
    letter-spacing:1px;
    text-shadow:0 0 8px rgba(255,193,7,.45),0 0 18px rgba(255,140,0,.35);
    margin-bottom:0 !important;
}

.explore-subhero{
    font-family:'Cinzel',serif !important;
    text-align:center !important;
    color:#FFD54F !important;
    font-size:38px !important;
    line-height:1.2 !important;
    font-weight:700 !important;
    margin-top:12px !important;
}

.explore-tagline{
    text-align:center;
    color:#CBD5E1;
    font-size:19px;
    margin-top:10px;
}

/* Category Buttons */
.stButton>button{
    background:linear-gradient(90deg,#F59E0B,#F97316);
    color:white;
    font-weight:bold;
    border:none;
    border-radius:12px;
    height:50px;
    transition:.3s;
    box-shadow:0 0 12px rgba(245,158,11,.25);
}

.stButton>button:hover{
    background:#FFD54F;
    color:black;
    transform:scale(1.03);
    box-shadow:0 0 20px rgba(255,193,7,.5);
}

/* Nearby Cards */
.explore-card{
    background:linear-gradient(145deg,#2B1B11,#3A2415);
    padding:18px 22px;
    border-radius:16px;
    border:2px solid #F59E0B;
    margin-bottom:15px;
    box-shadow:0 0 18px rgba(245,158,11,.18);
    transition:.3s;
    animation:fadeIn .5s ease;
}

.explore-card:hover{
    transform:translateY(-4px);
    box-shadow:0 0 28px rgba(255,165,0,.4);
}

.explore-title{
    color:#FFC107;
    font-size:20px;
    font-weight:bold;
    font-family:'Cinzel',serif;
}

.explore-distance{
    color:#CBD5E1;
    font-size:15px;
    margin-top:6px;
}

@keyframes fadeIn{
    from{opacity:0;transform:translateY(15px);}
    to{opacity:1;transform:translateY(0);}
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown(f"""<p class="explore-hero">🛕 Explore Around</p>
<p class="explore-subhero">{temple['name']}</p>
<p class="explore-tagline">Discover nearby attractions, restaurants, hotels and essential services around the temple.</p>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Category Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📍 Nearby Attractions", use_container_width=True):
        st.session_state.category = "attractions"

with col2:
    if st.button("🍽 Restaurants", use_container_width=True):
        st.session_state.category = "restaurants"

with col3:
    if st.button("🏨 Hotels", use_container_width=True):
        st.session_state.category = "hotels"

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🚌 Transport", use_container_width=True):
        st.session_state.category = "transport"

with col5:
    if st.button("🚑 Emergency", use_container_width=True):
        st.session_state.category = "emergency"

with col6:
    if st.button("🛍 Shopping", use_container_width=True):
        st.session_state.category = "shopping"

st.markdown("---")

# -----------------------------
# Category Content
# -----------------------------
category = st.session_state.get("category", None)

if category == "attractions":

    st.markdown("### 📍 Nearby Attractions")

    attractions = temple.get("nearby", {}).get("attractions", [])

    if attractions:

        for place in attractions:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">📍 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No nearby attractions available.")

#########################################################
elif category == "restaurants":

    st.markdown("### 🍽 Nearby Restaurants")

    restaurants = temple.get("nearby", {}).get("restaurants", [])

    if restaurants:

        for place in restaurants:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">🍽 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No nearby restaurants available.")
# **************************************************

elif category == "hotels":

    st.markdown("### 🏨 Nearby Hotels")

    hotels = temple.get("nearby", {}).get("hotels", [])

    if hotels:

        for place in hotels:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">🏨 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No nearby hotels available.")
# ************************************************************************************************************************
elif category == "transport":

    st.markdown("### 🚌 Nearby Transport")

    transport = temple.get("nearby", {}).get("transport", [])

    if transport:

        for place in transport:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">🚌 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No transport information available.")
#*************************************************
elif category == "emergency":

    st.markdown("### 🚑 Emergency Services")

    emergency = temple.get("nearby", {}).get("emergency", [])

    if emergency:

        for place in emergency:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">🚑 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No emergency services available.")

#*************************************************
elif category == "shopping":

    st.markdown("### 🛍 Nearby Shopping")

    shopping = temple.get("nearby", {}).get("shopping", [])

    if shopping:

        for place in shopping:

            st.markdown(f"""<div class="explore-card">
<div class="explore-title">🛍 {place['name']}</div>
<div class="explore-distance">📏 Distance : {place['distance']}</div>
</div>""", unsafe_allow_html=True)

    else:

        st.warning("No shopping places available.")

#****************************************************

else:

    st.markdown("""
<div style="background:linear-gradient(145deg,#2B1B11,#3A2415);border:2px solid #F59E0B;border-radius:18px;padding:20px;text-align:center;box-shadow:0 0 18px rgba(245,158,11,0.2);">
<h3 style="color:#FFC107;margin:0;">👆 Select a category above</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("⬅ Back to Temple Details", use_container_width=True):
    st.switch_page("app.py")
