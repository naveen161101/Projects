# app.py
import streamlit as st
import speech_recognition as sr
import io
from gtts import gTTS
import base64
import tempfile
import uuid
from google import genai

# ------------------------------
# App config + styling
# ------------------------------
st.set_page_config(page_title="VoiceBot — Personal Voice Assistant", page_icon="🤖", layout="wide")
st.markdown("""
<style>
/* Page background */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
  color: #e6eef8;
  font-family: "Inter", sans-serif;
}

/* Card */
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 30px rgba(2,6,23,0.6);
}

/* Title */
h1 {
  font-weight: 700;
  color: #fff;
}

/* Buttons */
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
# Gemini API Key
# ------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("GEMINI_API_KEY is not set in Streamlit Secrets!")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------
# Profile editor (sidebar)
# ------------------------------
with st.sidebar:
    st.header("Bot Personality (editable)")
    st.write("Fill these so the bot replies *as you* — anyone can test without coding.")
    default_profile = {
        "life_story": "I grew up in a small town, studied computer science, and love building useful tools that help people.",
        "superpower": "Seeing simple solutions for complicated problems.",
        "growth_areas": "Leadership, public speaking, and deep systems design.",
        "coworker_misconception": "They think I'm quiet — but I just prefer listening first.",
        "how_i_push_limits": "I take on projects slightly outside my comfort zone and iterate fast."
    }
    if "profile" not in st.session_state:
        st.session_state.profile = default_profile.copy()

    st.session_state.profile["life_story"] = st.text_area("1) Life story", value=st.session_state.profile["life_story"], height=100)
    st.session_state.profile["superpower"] = st.text_input("2) #1 Superpower", value=st.session_state.profile["superpower"])
    st.session_state.profile["growth_areas"] = st.text_input("3) Top 3 areas to grow in", value=st.session_state.profile["growth_areas"])
    st.session_state.profile["coworker_misconception"] = st.text_input("4) Coworker misconception", value=st.session_state.profile["coworker_misconception"])
    st.session_state.profile["how_i_push_limits"] = st.text_area("5) How you push boundaries", value=st.session_state.profile["how_i_push_limits"], height=100)

    st.markdown("---")
    st.checkbox("Auto play audio responses", key="auto_play", value=True)

# ------------------------------
# Session state
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_trigger" not in st.session_state:
    st.session_state.audio_trigger = 0

# ------------------------------
# Helpers
# ------------------------------
def audio_bytes_to_text(audio_bytes: bytes) -> str | None:
    r = sr.Recognizer()
    try:
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_file as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        st.error(f"Speech -> text failed: {e}")
        return None

def generate_reply_llm(user_question: str, profile: dict) -> str:
    """
    Use Gemini LLM to respond in a fun, friendly way.
    """
    prompt = f"""
    You are a fun and friendly assistant that answers like a person. 
    Use the following profile to respond to user questions naturally and playfully:

    Life story: {profile['life_story']}
    Superpower: {profile['superpower']}
    Growth areas: {profile['growth_areas']}
    Coworker misconception: {profile['coworker_misconception']}
    How they push limits: {profile['how_i_push_limits']}

    User question: {user_question}
    Reply in a short, friendly, slightly humorous way.
    """
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        st.warning("LLM is busy or API error. Please try again later.")
        return "Oops! I couldn't think of a reply right now 😅"

def speak_and_render(text: str, autoplay: bool = True):
    tts = gTTS(text, lang="en")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp.name)
    audio_bytes = open(temp.name, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    autoplay_attr = "autoplay" if autoplay else ""
    audio_html = f"""
        <audio controls {autoplay_attr} style="width:100%;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ------------------------------
# Main UI
# ------------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("🎙 Ask the VoiceBot — speak or type")
    audio_input = st.audio_input(f"Click to record (Recording #{st.session_state.audio_trigger + 1})")
    typed = st.text_input("Type question here", key="typed_question")

    colp1, colp2 = st.columns([1, 1])
    with colp1:
        process_btn = st.button("Send Question (Process)")
    with colp2:
        clear_btn = st.button("Clear Chat")

    if clear_btn:
        st.session_state.chat_history = []

    if process_btn:
        user_question = None
        if audio_input is not None and audio_input.getbuffer().nbytes > 0:
            text = audio_bytes_to_text(audio_input.getvalue())
            if text:
                user_question = text
            else:
                st.warning("Couldn't transcribe audio. Try again or type your question.")
        if not user_question and typed:
            user_question = typed

        if user_question:
            st.session_state.chat_history.append(("You", user_question))
            reply = generate_reply_llm(user_question, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, autoplay=st.session_state.auto_play)
            st.session_state.audio_trigger += 1
            # ✅ Clear typed input safely
            st.session_state.typed_question = ""
        else:
            st.warning("No input found. Please record or type a question.")

with right:
    st.subheader("✨ Quick Questions")
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
            reply = generate_reply_llm(s, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, autoplay=st.session_state.auto_play)

# ------------------------------
# Chat history
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

st.markdown("---")
st.caption("Built for easy sharing: edit the profile on the right (no API keys needed).")
