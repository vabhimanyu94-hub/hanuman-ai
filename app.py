import streamlit as st
import google.generativeai as genai
import os
import asyncio
import edge_tts
import time

st.set_page_config(page_title="Hanuman AI", page_icon="🔱", layout="wide")

# --- CUSTOM CSS FOR FIXED UNIFIED BOTTOM BAR DESIGN ---
st.markdown("""
<style>
    /* Saare unnecessary components hide karne ke liye */
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stMainMenuGitHubIcon"] {display: none !important;}
    [data-testid="stViewerStatus"] {display: none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}
    footer {display: none !important;}
    
    /* Layout Container Settings */
    div.block-container {
        max-width: 750px !important;
        margin: 0 auto !important;
    }
    
    .stAppViewMain > div > div {
        padding-top: 3rem !important;
        padding-bottom: 260px !important; /* Space for fixed unified bar */
    }
    
    /* 🔱 MASTER FIX: Dynamic Bottom Container Jo Input aur Upload dono ko merge karega */
    .unified-bottom-bar {
        position: fixed !important;
        bottom: 30px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        max-width: 750px !important;
        width: calc(100% - 2rem) !important;
        background-color: #262730 !important; /* Premium unified slate background */
        border-radius: 28px !important; /* Rounded pill effect */
        padding: 8px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
        z-index: 1000000 !important;
        border: 1px solid #3f404a !important;
    }
    
    /* Default inputs ke transparent overrides taaki wrapper layout kharab na kare */
    [data-testid="stChatInput"] {
        position: static !important;
        width: 100% !important;
        max-width: unset !important;
        background: transparent !important;
        background-color: transparent !important;
        padding: 0 !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding-left: 10px !important;
    }
    
    /* File uploader ko structural alignment container ke right me shrink karne ke liye */
    .upload-btn-container {
        max-width: fit-content !important;
        display: flex !important;
        align-items: center !important;
    }
    
    [data-testid="stFileUploader"] {
        width: auto !important;
        max-width: fit-content !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    [data-testid="stFileUploader"] > section {
        background: #1e1e24 !important;
        border: 1px solid #4a4b57 !important;
        border-radius: 20px !important;
        padding: 4px 14px !important;
    }
    
    [data-testid="stFileUploader"] > section > div {
        flex-direction: row !important;
        gap: 8px !important;
        align-items: center !important;
    }
    
    [data-testid="stFileUploaderDropzoneCaption"] {
        font-size: 10px !important;
        color: #a3a8b4 !important;
        display: inline-block !important;
    }

    /* Sidebar buttons theme adjustments */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    .stButton>button {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# SECURITY UPGRADE - API KEY
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = "AIzaSyC38ARVgx_CclzYSDO7SyRJeLQcCvCsNBs"

# Initialization
genai.configure(api_key=API_KEY)

# Ensure session state is active
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/trident.png", width=80)
    st.title("Hanuman AI Control")
    st.write("Sankat Mochan Dashboard")
    st.write("---")
    
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    st.caption("Developed with ❤️ by Abhimanyu")

    # Support Section
    st.markdown("---")
    st.subheader("🔱 Support This Project")
    with st.sidebar.expander("💸 Click here to Scan & Pay"):
        st.markdown(":white[Agar aapko Hanuman AI pasand aaya, toh aap support kar sakte hain!]")
        try:
            st.image("qr.jpg", width=200)
        except:
            pass

# Main Interface Header
st.markdown("<h1 style='text-align: center;'>🔱 Hanuman AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a3a8b4;'>Gyan, Buddhi, Vision aur Voice ke sath — Aapke har sawaal aur kaam ka saathi</p>", unsafe_allow_html=True)
st.write("---")

# --- DISPLAY STREAMING CHAT HISTORY ---
for message in st.session_state.messages:
    avatar = "🔱" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio" in message and os.path.exists(message["audio"]):
            st.audio(message["audio"], format="audio/mp3")

# --- UNIFIED INPUT LAYER EXECUTION ---
# Empty references for late initialization placeholders
uploaded_file = None
prompt = None

# Injecting HTML components wrapper container for fixed flexbox layout matching your draw frame
st.markdown('<div class="unified-bottom-bar">', unsafe_allow_html=True)

# Container column splits inside Streamlit to hold input elements inside the flex wrapper
col1, col2 = st.columns([0.75, 0.25])

with col1:
    prompt = st.chat_input("Type a message...")

with col2:
    st.markdown('<div class="upload-btn-container">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("➕ Upload", type=["png", "jpg", "jpeg", "txt", "py"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    st.info(f"📎 Attached file active: {uploaded_file.name}")

# --- AI LOGIC AND RESPONSE PIPELINE ---
async def generate_premium_voice(text, filename):
    voice = "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+10%")
    await communicate.save(filename)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()  # Instantly flush UI changes cleanly