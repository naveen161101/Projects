import streamlit as st
import os
from google import genai
import speech_recognition as sr
from gtts import gTTS
import base64
import tempfile

# ------------------------------
# Page Layout
# ------------------------------
st.set_page_config(page_title="Voice Bot", page_icon="🤖", layout="wide")
st.title("🤖 Voice Chat Bot")
st.sidebar.header("How to Use")
st.sidebar.write("""
1. Click **Start Listening** to ask a question.
2. Allow microphone access.
3. Wait for bot to respond with audio.
4. Chat is stored in history.
""")

# ------------------------------
# Load API key from Secrets
# ------------------------------
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
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

# ------------------------------
# Record User Voice
# ------------------------------
def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        audio = r.listen(source, phrase_time_limit=10)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"Speech Recognition error; {e}")
            return None

# ------------------------------
# Generate Bot Response
# ------------------------------
def get_bot_reply(user_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Respond briefly and in a fun, friendly tone with a little humor: {user_text}"
        )
        return response.text
    except Exception as e:
        st.warning("Bot is busy or API error. Please try again later.")
        return None

# ------------------------------
# Convert Text to Speech
# ------------------------------
def text_to_speech(bot_reply):
    tts = gTTS(bot_reply, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    audio_bytes = open(temp_audio.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio tag.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ------------------------------
# Chat Interface
# ------------------------------
if st.button("Start Listening"):
    user_text = record_voice()
    if user_text:
        st.session_state.chat_history.append(("You", user_text))
        bot_reply = get_bot_reply(user_text)
        if bot_reply:
            st.session_state.chat_history.append(("Bot", bot_reply))
            text_to_speech(bot_reply)

# ------------------------------
# Display Chat History
# ------------------------------
st.subheader("Chat History")
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")
