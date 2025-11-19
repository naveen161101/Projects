import streamlit as st
import os
from google import genai
import speech_recognition as sr
from gtts import gTTS
import base64
import tempfile
import io

# ------------------------------
# Page Layout
# ------------------------------
st.set_page_config(page_title="Voice Bot", page_icon="🤖", layout="wide")
st.title("🤖 Voice Chat Bot (Streamlit Cloud Compatible)")

st.sidebar.header("How to Use")
st.sidebar.write("""
1. Upload recorded audio OR click the mic icon in Streamlit to record.
2. Bot converts speech → text → AI → speech.
3. Chat history is shown below.
""")

# ------------------------------
# Load API key from Secrets
# ------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("GEMINI_API_KEY is not set in Streamlit Secrets!")
    st.stop()

# ------------------------------
# Initialize Gemini API Client
# ------------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------
# Chat History
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------------------------------
#  REPLACED FUNCTION: Record User Voice (Cloud Safe)
# ---------------------------------------------------
def record_voice_streamlit(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_file as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.warning("Could not understand audio")
        return None
    except Exception as e:
        st.error(f"Speech recognition error: {e}")
        return None


# ------------------------------
# Generate Bot Response
# ------------------------------
def get_bot_reply(user_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Respond in a short, fun tone with mild humor: {user_text}"
        )
        return response.text
    except Exception:
        st.warning("Bot is busy or API error. Please try later.")
        return None


# ---------------------------------------------------
#  REPLACED FUNCTION: Convert Text → Speech
# ---------------------------------------------------
def text_to_speech(bot_reply):
    tts = gTTS(bot_reply, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)

    audio_bytes = open(temp_audio.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


# ------------------------------
# Chat Interface
# ------------------------------
st.subheader("🎙 Record Your Voice")
audio_file = st.audio_input("Click to record or upload audio")

if audio_file is not None:
    audio_bytes = audio_file.read()

    user_text = record_voice_streamlit(audio_bytes)

    if user_text:
        st.session_state.chat_history.append(("You", user_text))

        bot_reply = get_bot_reply(user_text)

        if bot_reply:
            st.session_state.chat_history.append(("Bot", bot_reply))
            text_to_speech(bot_reply)

# ------------------------------
# Display Chat History
# ------------------------------
st.subheader("💬 Chat History")
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 Bot:** {message}")
