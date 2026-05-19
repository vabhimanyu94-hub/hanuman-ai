import streamlit as st
import google.generativeai as genai
import os
import asyncio
import edge_tts
import time

st.set_page_config(page_title="Hanuman AI", page_icon="🔱", layout="wide")

# Custom CSS for Premium Theme & Transparent Minimalist Bottom Layout
st.markdown("""
<style>
    /* Saare unnecessary elements hide karne ke liye */
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stMainMenuGitHubIcon"] {display: none !important;}
    [data-testid="stViewerStatus"] {display: none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}
    footer {display: none !important;}
    
    /* Layout Container alignment */
    div.block-container {
        max-width: 700px !important;
        margin: 0 auto !important;
    }
    
    .stAppViewMain > div > div {
        padding-top: 3rem !important;
        padding-bottom: 240px !important; /* Fixed components spacing */
    }
    
    /* ULTRA FIX: Uploader ka dabba, boundary, shadow sab hatakar sirf plain text rakhne ke liye */
    [data-testid="stFileUploader"] {
        position: fixed !important;
        bottom: 110px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        max-width: fit-content !important;
        width: auto !important;
        z-index: 999999 !important;
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }
    
    /* Drag and drop wrapper block ko bhi clear transparent karne ke liye */
    [data-testid="stFileUploader"] > section {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }
    
    /* Inside box alignment to vertical stack */
    [data-testid="stFileUploader"] > section > div {
        flex-direction: column !important;
        align-items: center !important;
        gap: 0px !important;
    }
    
    /* Format label settings (Text ke just neeche nested) */
    [data-testid="stFileUploaderDropzoneCaption"] {
        font-size: 11px !important;
        color: #888888 !important;
        text-align: center !important;
        margin-top: -2px !important;
    }
    
    /* Chat input position lock */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        max-width: 700px !important;
        width: calc(100% - 2rem) !important;
        z-index: 1000000 !important;
    }
    
    /* Sidebar styling */
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

# Fix: Ensure messages list is initialized before rendering history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
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

    # --- SIDEBAR SUPPORT SECTION ---
    st.markdown("---")
    st.subheader("🔱 Support This Project")
    with st.sidebar.expander("💸 Click here to Scan & Pay"):
        st.markdown(":white[Agar aapko Hanuman AI pasand aaya, toh aap support kar sakte hain!]")
        try:
            st.image("qr.jpg", width=200)
        except:
            pass

# Main Screen Heading (Centered via Streamlit Layout)
st.markdown("<h1 style='text-align: center;'>🔱 Hanuman AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a3a8b4;'>Gyan, Buddhi, Vision aur Voice ke sath — Aapke har sawaal aur kaam ka saathi</p>", unsafe_allow_html=True)
st.write("---")

# --- DISPLAY CHAT HISTORY ---
# Fix: Purani chat screen par load rahegi
for message in st.session_state.messages:
    avatar = "🔱" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio" in message and os.path.exists(message["audio"]):
            st.audio(message["audio"], format="audio/mp3")

# --- LOWER CHAT & ATTACHMENT SYSTEM (ChatGPT Style) ---

# 1. File Uploader
uploaded_file = st.file_uploader("➕ Attach Image/File for Hanuman AI", type=["png", "jpg", "jpeg", "txt", "py"], label_visibility="collapsed")

if uploaded_file is not None:
    st.success(f"📎 Attached: {uploaded_file.name}")

# 2. Premium Voice Function
async def generate_premium_voice(text, filename):
    voice = "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+10%")
    await communicate.save(filename)

# 3. User Input Box
if prompt := st.chat_input("Hanuman Ji se kuch bhi poochhein..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_instruction = (
        "Aapka naam Hanuman AI hai. Aap ek bohot hi gyaani, helpful, polite aur sankat-mochan AI hain. "
        "Aap user ki har kaam me madad karte hain chahe wo coding ho, media editing ho, stock market gyan ho, ya koi gyaan ki baat. "
        "Hamesha humble aur respectful rahein aur 'Jai Shree Ram' ka aadar karein."
    )

    with st.chat_message("assistant", avatar="🔱"):
        message_placeholder = st.empty()
        
        response = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                contents_payload = [prompt]
                if uploaded_file is not None:
                    file_bytes = uploaded_file.read()
                    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                        contents_payload.append({"data": file_bytes, "mime_type": uploaded_file.type})
                    else:
                        file_text = file_bytes.decode("utf-8")
                        contents_payload.append(f"\n\n[Uploaded File Content:\n{file_text}]")
                
                # Fix: Correct client initialization mapping for correct API config
                model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
                response = model.generate_content(contents_payload)
                break
           except Exception as e:
                if "503" in str(e) and attempt < max_retries - 1:
                    message_placeholder.warning("Server busy hai, fir se koshish kar raha hoon...")
                    time.sleep(2)
                else:
                    # Fix: Quota ya bade error par purana galat message history se turant saaf karo
                    if "messages" in st.session_state and len(st.session_state.messages) > 0:
                        st.session_state.messages.pop()
                    st.error(f"Kuch galti hui: {e}")
                    break

        if response is not None:
            try:
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                
                # --- PREMIUM DESI VOICE GENERATION ---
                clean_text = ai_response.replace("*", "").replace("#", "")
                audio_filename = f"response_{int(time.time())}.mp3"
                
                asyncio.run(generate_premium_voice(clean_text, audio_filename))
                time.sleep(0.5)
                
                if os.path.exists(audio_filename) and os.path.getsize(audio_filename) > 0:
                    st.audio(audio_filename, format="audio/mp3")
                    st.session_state.messages.append({"role": "assistant", "content": ai_response, "audio": audio_filename})
                else:
                    st.error("Audio file write error.")
            except Exception as voice_err:
                st.error(f"Text aa gaya par audio me dikkat: {voice_err}")