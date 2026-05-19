import streamlit as st
import google.generativeai as genai
import os
import asyncio
import edge_tts
import time

st.set_page_config(page_title="Hanuman AI", page_icon="🔱", layout="wide")

# Custom CSS for Premium Theme & Hiding GitHub/Streamlit Elements
st.markdown("""
<style>
    /* GitHub Icon aur Fork button hide karne ke liye */
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stMainMenuGitHubIcon"] {display: none !important;}
    
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

# Updated initialization format
genai.configure(api_key=API_KEY)

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
# Main Screen Heading
st.title("🔱 Hanuman AI")
st.caption("Gyan, Buddhi, Vision aur Voice ke sath — Aapke har sawaal aur kaam ka saathi")
st.write("---")

# Chat history initialize karna
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chat screen par dikhane ke liye
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🔱" if message["role"]=="assistant" else None):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "audio" in message:
            if os.path.exists(message["audio"]):
                st.audio(message["audio"], format="audio/mp3")

# FILE / IMAGE UPLOADER
uploaded_file = st.file_uploader("📁 Koi bhi Image ya File upload karein aur uske baare me poochhein:", type=["png", "jpg", "jpeg", "txt", "py"])

if uploaded_file is not None:
    st.success(f"Successfully Uploaded: {uploaded_file.name}")

# Function to generate premium voice
async def generate_premium_voice(text, filename):
    voice = "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+10%")
    await communicate.save(filename)

# User Input Box
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
                        contents_payload.append(f"\\n\\n[Uploaded File Content:\\n{file_text}]")
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents_payload,
                    config={"system_instruction": system_instruction}
                )
                break
            except Exception as e:
                if "503" in str(e) and attempt < max_retries - 1:
                    message_placeholder.warning("Server busy hai, fir se koshish kar raha hoon...")
                    time.sleep(2)
                else:
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
                    st.error("Audio block write error.")
            except Exception as voice_err:
                st.error(f"Text aa gaya par audio me dikkat: {voice_err}")