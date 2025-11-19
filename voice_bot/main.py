import streamlit as st
import os
import base64
import tempfile
import speech_recognition as sr
from gtts import gTTS
from google import genai

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI VoiceBot",
    page_icon="🎤",
    layout="centered",
)

st.markdown("""
<style>
.big-title {
    font-size: 42px !important;
    text-align: center;
    font-weight: 700;
    color: #4A90E2;
}
.sub {
    text-align:center;
    font-size:18px;
    color:#5f6368;
}
.chat-bubble-user {
    background: #DCF8C6;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    font-size: 16px;
}
.chat-bubble-bot {
    background: #E8EAF6;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🎤 AI Voice Personality Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Ask using Voice or Text. The bot replies in speech & chat.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Load API KEY
# ---------------------------------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("❌ Missing GEMINI_API_KEY in Streamlit Secrets")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# Session State Init
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "reset_input" not in st.session_state:
    st.session_state.reset_input = False

# ---------------------------------------------------------
# Reset input BEFORE widget renders (Fixes your error)
# ---------------------------------------------------------
if st.session_state.reset_input:
    st.session_state["typed_question"] = ""
    st.session_state.reset_input = False

# ---------------------------------------------------------
# Chat Input Box
# ---------------------------------------------------------
user_text = st.text_input(
    "Type your question here...",
    key="typed_question",
    placeholder="Ask anything like— What's your superpower?",
)

# ---------------------------------------------------------
# Voice Recording
# ---------------------------------------------------------
def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source, phrase_time_limit=7)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        st.warning("❗ Sorry, could not understand your voice.")
        return None

# ---------------------------------------------------------
# AI Response
# ---------------------------------------------------------
def ask_ai(text):
    prompt = f"""
You are an AI personality bot answering questions about yourself —
as if YOU are ChatGPT.

Keep responses:
• short
• friendly
• personal
• slightly humorous

User asked: {text}
"""

    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return res.text
    except Exception as e:
        st.error("API Error. Try again.")
        return None

# ---------------------------------------------------------
# Text → Speech
# ---------------------------------------------------------
def speak(text):
    tts = gTTS(text, lang="en")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp.name)

    audio_bytes = open(temp.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio autoplay controls>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# BUTTONS
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Ask by Voice"):
        spoken = record_voice()
        if spoken:
            st.session_state.history.append(("You", spoken))
            reply = ask_ai(spoken)
            if reply:
                st.session_state.history.append(("Bot", reply))
                speak(reply)

with col2:
    if st.button("💬 Ask by Text"):
        if user_text.strip() != "":
            st.session_state.history.append(("You", user_text))
            reply = ask_ai(user_text)
            if reply:
                st.session_state.history.append(("Bot", reply))
                speak(reply)
            st.session_state.reset_input = True   # will reset text safely next run

# ---------------------------------------------------------
# Chat History UI
# ---------------------------------------------------------
st.markdown("### 💬 Conversation")

for sender, msg in st.session_state.history:
    if sender == "You":
        st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'><b>Bot:</b> {msg}</div>", unsafe_allow_html=True)
