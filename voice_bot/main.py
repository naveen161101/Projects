# app.py
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import base64
import tempfile
import io
import uuid
from google import genai

# ------------------------------
# App config + styling
# ------------------------------
st.set_page_config(page_title="VoiceBot — Personal Voice Assistant", page_icon="🤖", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
  color: #e6eef8;
  font-family: "Inter", sans-serif;
}
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 30px rgba(2,6,23,0.6);
}
.stButton>button {
  background: linear-gradient(90deg,#06b6d4,#60a5fa);
  color: #061224;
  font-weight: 600;
  border-radius: 10px;
  padding: 8px 12px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Load API Key
# ------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets!")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------
# Sidebar: Profile Editor
# ------------------------------
with st.sidebar:
    st.header("Bot Personality")
    st.write("Customize the bot to reply in your voice/personality.")
    default_profile = {
        "life_story": "I grew up loving coding and building fun tools.",
        "superpower": "Solving complex problems with simple solutions.",
        "growth_areas": "Leadership, public speaking, and creativity.",
        "coworker_misconception": "They think I'm quiet but I observe carefully.",
        "how_i_push_limits": "I take on slightly uncomfortable challenges to grow fast."
    }
    if "profile" not in st.session_state:
        st.session_state.profile = default_profile.copy()

    for key in default_profile:
        if len(default_profile[key]) > 50:
            st.session_state.profile[key] = st.text_area(key.replace("_"," ").capitalize(), value=st.session_state.profile[key], height=80)
        else:
            st.session_state.profile[key] = st.text_input(key.replace("_"," ").capitalize(), value=st.session_state.profile[key])

    st.markdown("---")
    st.checkbox("Auto play audio responses", key="auto_play", value=True)
    st.write("Try sample questions or type/speak your own below!")

# ------------------------------
# Initialize session state
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_trigger" not in st.session_state:
    st.session_state.audio_trigger = 0

# ------------------------------
# Helper: Speech-to-text
# ------------------------------
def audio_bytes_to_text(audio_bytes: bytes):
    r = sr.Recognizer()
    try:
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_file as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text
    except Exception:
        return None

# ------------------------------
# Helper: Call LLM
# ------------------------------
def get_llm_reply(user_question: str, profile: dict):
    """
    Prompt the LLM to answer in a fun, friendly, slightly humorous way,
    integrating bot personality from profile.
    """
    prompt = f"""
You are a fun, friendly, and slightly humorous assistant.
Your personality is:
- Life Story: {profile['life_story']}
- Superpower: {profile['superpower']}
- Growth Areas: {profile['growth_areas']}
- Coworker Misconception: {profile['coworker_misconception']}
- How you push limits: {profile['how_i_push_limits']}

User asked: "{user_question}"

Answer the user in a friendly, engaging, and fun tone. Keep it brief.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Oops! I couldn't think of a response. ({e})"

# ------------------------------
# Helper: Text-to-speech
# ------------------------------
def speak_and_render(text: str, autoplay=True):
    tts = gTTS(text, lang="en")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp.name)
    audio_bytes = open(temp.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    autoplay_attr = "autoplay" if autoplay else ""
    audio_html = f"""
        <audio controls {autoplay_attr} style="width:100%;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ------------------------------
# Main UI: Chat
# ------------------------------
left, right = st.columns([2,1])

with left:
    st.subheader("🎙 Ask the VoiceBot — speak or type")
    audio_input = st.audio_input(f"Click to record (Recording #{st.session_state.audio_trigger + 1})")
    typed = st.text_input("Type question here", key="typed_question")
    colp1, colp2 = st.columns([1,1])
    process_btn = colp1.button("Send Question")
    clear_btn = colp2.button("Clear Chat")

    if clear_btn:
        st.session_state.chat_history = []
        st.session_state.audio_trigger = 0

    if process_btn:
        user_question = None
        if audio_input is not None and audio_input.getbuffer().nbytes > 0:
            audio_bytes = audio_input.getvalue()
            text = audio_bytes_to_text(audio_bytes)
            if text:
                user_question = text
            else:
                st.warning("Couldn't transcribe audio. Try typing your question.")
        if not user_question and typed:
            user_question = typed

        if user_question:
            st.session_state.chat_history.append(("You", user_question))
            reply = get_llm_reply(user_question, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, autoplay=st.session_state.auto_play)
            st.session_state.audio_trigger += 1
            st.session_state["typed_question"] = ""  # reset input

with right:
    st.subheader("✨ Sample Questions")
    samples = [
        "What should we know about your life story in a few sentences?",
        "What’s your #1 superpower?",
        "What are the top 3 areas you’d like to grow in?",
        "What misconception do your coworkers have about you?",
        "How do you push your boundaries and limits?"
    ]
    for s in samples:
        if st.button(s, key=f"sample_{uuid.uuid4()}"):
            st.session_state.chat_history.append(("You", s))
            reply = get_llm_reply(s, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, autoplay=st.session_state.auto_play)

# ------------------------------
# Chat History display
# ------------------------------
st.markdown("---")
st.subheader("💬 Chat History")
if not st.session_state.chat_history:
    st.info("No conversation yet — record or type a question to start.")
else:
    for who, msg in st.session_state.chat_history[::-1]:
        if who == "You":
            st.markdown(f"<div class='card'><strong>🧑 You:</strong> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card'><strong>🤖 Bot:</strong> {msg}</div>", unsafe_allow_html=True)
