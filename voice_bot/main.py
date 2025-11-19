import streamlit as st
import os
from google import genai
import speech_recognition as sr
from gtts import gTTS
import base64
import io
import tempfile

# ------------------------------
# Page Layout
# ------------------------------
st.set_page_config(page_title="Voice Bot", page_icon="🤖", layout="wide")
st.title("🤖 Voice Chat Bot")

st.sidebar.header("How to Use")
st.sidebar.write("""
1. Click **Record Voice** and speak.
2. Wait for speech-to-text to convert.
3. Bot replies with voice.
4. You can record again ANY number of times.
""")

# ------------------------------
# Load API Key
# ------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("GEMINI_API_KEY is missing in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------
# Chat History
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "audio_trigger" not in st.session_state:
    st.session_state.audio_trigger = 0  # Forces re-render of audio widget

# ------------------------------
# Speech-to-Text
# ------------------------------
def audio_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
    with audio_file as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception:
        return None

# ------------------------------
# Gemini Bot Response
# ------------------------------
def get_bot_reply(user_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Reply conversationally, short, friendly, slight humor: {user_text}"
        )
        return response.text
    except:
        return "Sorry, I'm unable to respond right now."

# ------------------------------
# Text-To-Speech
# ------------------------------
def play_audio(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)

    audio_bytes = open(temp_file.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ------------------------------
# Voice Recording Widget
# ------------------------------
st.subheader("🎤 Record Your Voice")

audio_input = st.audio_input(
    f"Click to Speak (Recording #{st.session_state.audio_trigger + 1})"
)

if st.button("Process Recording"):
    if audio_input:
        audio_bytes = audio_input.getvalue()

        # Convert speech -> text
        user_text = audio_to_text(audio_bytes)

        if not user_text:
            st.warning("Couldn't understand audio. Try again.")
        else:
            st.success(f"You said: **{user_text}**")
            st.session_state.chat_history.append(("You", user_text))

            # Bot Reply
            bot_reply = get_bot_reply(user_text)
            st.session_state.chat_history.append(("Bot", bot_reply))

            # Text-to-speech
            play_audio(bot_reply)

        # IMPORTANT → Reset widget so user can record again
        st.session_state.audio_trigger += 1
        st.rerun()

    else:
        st.warning("Please record your voice first.")

# ------------------------------
# Chat History
# ------------------------------
st.subheader("💬 Chat History")
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
