# app.py
import streamlit as st
import speech_recognition as sr
import io
from gtts import gTTS
import base64
import tempfile
import uuid

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

# Top layout: title + description
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 VoiceBot — Respond like *you*")
    st.write("A polished, shareable voice demo: record, ask, and the bot will answer in your voice/personality. Edit your personal profile on the right to make the bot *sound* like you.")
with col2:
    st.image("https://raw.githubusercontent.com/streamlit/brand/master/streamlit-mark-color.png", width=64)

st.write("---")

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

    st.session_state.profile["life_story"] = st.text_area("1) Life story (a few sentences)", value=st.session_state.profile["life_story"], height=100)
    st.session_state.profile["superpower"] = st.text_input("2) #1 Superpower", value=st.session_state.profile["superpower"])
    st.session_state.profile["growth_areas"] = st.text_input("3) Top 3 areas to grow in (comma-separated)", value=st.session_state.profile["growth_areas"])
    st.session_state.profile["coworker_misconception"] = st.text_input("4) Coworker misconception", value=st.session_state.profile["coworker_misconception"])
    st.session_state.profile["how_i_push_limits"] = st.text_area("5) How you push boundaries", value=st.session_state.profile["how_i_push_limits"], height=100)

    st.markdown("---")
    st.checkbox("Auto play audio responses", key="auto_play", value=True)
    st.markdown("---")
    st.write("Tip: edit the profile to match yourself before submitting the demo link.")

# ------------------------------
# Session vars + reset logic
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "audio_trigger" not in st.session_state:
    st.session_state.audio_trigger = 0

if "reset_typed" not in st.session_state:
    st.session_state.reset_typed = False

# Reset typed input BEFORE it is created
if st.session_state.reset_typed:
    st.session_state["typed_question"] = ""
    st.session_state.reset_typed = False

# ------------------------------
# Helper: Speech-to-text
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

# ------------------------------
# Helper: Rule-based response
# ------------------------------
def generate_reply(user_question: str, profile: dict) -> str:
    q = user_question.lower().strip()

    if any(k in q for k in ["life story", "about your life", "who are you"]):
        return profile["life_story"]

    if any(k in q for k in ["superpower", "super power", "strength"]):
        return f"My #1 superpower is {profile['superpower']}."

    if any(k in q for k in ["top 3", "areas you'd like to grow", "growth areas"]):
        items = [s.strip() for s in profile["growth_areas"].split(",") if s.strip()]
        if items:
            return "The top areas I'd like to grow in are: " + ", ".join(items) + "."
        return profile["growth_areas"]

    if any(k in q for k in ["misconception", "coworker"]):
        return profile["coworker_misconception"]

    if any(k in q for k in ["push", "boundaries", "limits"]):
        return profile["how_i_push_limits"]

    return (
        f"I'll keep it short: {profile['life_story'].split('.')[0]}. "
        f"My superpower is {profile['superpower']}."
    )

# ------------------------------
# Helper: TTS + render
# ------------------------------
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
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ------------------------------
# UI (Main)
# ------------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("🎙 Ask the VoiceBot — speak or type")

    audio_input = st.audio_input(f"Click to record (Recording #{st.session_state.audio_trigger + 1})")

    st.write("Or type your question:")
    typed = st.text_input("Type question here", key="typed_question")

    c1, c2 = st.columns([1, 1])
    process_btn = c1.button("Send Question (Process)")
    clear_btn = c2.button("Clear Chat")

    if clear_btn:
        st.session_state.chat_history = []
        st.experimental_rerun()

    if process_btn:
        user_question = None

        # Audio
        if audio_input and audio_input.getbuffer().nbytes > 0:
            st.info("Transcribing...")
            text = audio_bytes_to_text(audio_input.getvalue())
            if text:
                user_question = text

        # Typed fallback
        if not user_question and typed:
            user_question = typed

        if user_question:
            st.session_state.chat_history.append(("You", user_question))
            reply = generate_reply(user_question, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, st.session_state.auto_play)

            st.session_state.audio_trigger += 1
            st.session_state.reset_typed = True
            st.experimental_rerun()
        else:
            st.warning("No input detected.")

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
            reply = generate_reply(s, st.session_state.profile)
            st.session_state.chat_history.append(("Bot", reply))
            speak_and_render(reply, st.session_state.auto_play)
            st.experimental_rerun()

# ------------------------------
# Chat History
# ------------------------------
st.markdown("---")
st.subheader("💬 Chat History")

if not st.session_state.chat_history:
    st.info("No conversation yet.")
else:
    for who, msg in st.session_state.chat_history[::-1]:
        label = "🧑 You:" if who == "You" else "🤖 Bot:"
        st.markdown(f"<div class='card'><strong>{label}</strong> {msg}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Built for easy sharing — no API keys needed.")
