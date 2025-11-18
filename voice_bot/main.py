import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from google import genai
import speech_recognition as sr
from gtts import gTTS
import base64

# -------------------------------
# Load Gemini API Key
# -------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("API key not found! Set GEMINI_API_KEY in .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="Snappy Voice Chat Bot",
    layout="wide",
    page_icon="🤖"
)

# -------------------------------
# Sidebar Instructions
# -------------------------------
st.sidebar.title("📝 How to Use")
st.sidebar.markdown("""
1. Enable your microphone. 🎤  
2. Press **'🎙️ Talk'** to speak.  
3. Bot replies **short, playful, human-like**. 😄  
4. Latest audio plays automatically. Previous audios can be replayed.  
5. Optional: Check **'Show Conversation History'** to see past chats.  
6. Keep conversation fun & brief! 💬  
""")

st.sidebar.markdown("---")
st.sidebar.markdown("💡 Try asking:")
st.sidebar.markdown("- What's your superpower?")  
st.sidebar.markdown("- Tell me a joke!")  
st.sidebar.markdown("- Give me a fun tip for today.")  

# -------------------------------
# Initialize conversation state
# -------------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # list of tuples: (role, text, audio_file)

recognizer = sr.Recognizer()

# Temporary folder to save audio files
if "audio_dir" not in st.session_state:
    st.session_state.audio_dir = tempfile.mkdtemp()

# -------------------------------
# Main Chat UI
# -------------------------------
st.title("🤖 Snappy Voice Chat Bot")
st.markdown(
    "Talk to the bot! Replies are **short, playful, and like chatting with a friend**. "
    "Bot responds in **text + voice**."
)

# -------------------------------
# Two-column layout
# -------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🎙️ Talk"):
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic)
            st.info("Listening...")
            audio = recognizer.listen(mic)

        try:
            # Speech to Text
            user_text = recognizer.recognize_google(audio)
            st.success(f"🧑 You said: {user_text}")

            # Append user text with None as audio_file
            st.session_state.conversation.append(("user", user_text, None))

            # -------------------------------
            # Build prompt for Gemini
            # -------------------------------
            prompt = """
You are a fun, witty, snappy conversational agent. 
Keep responses **1–2 sentences max**, playful, casual, humorous, like friends chatting. 
Add small jokes, exclamations, and reactions where appropriate.\n\n
"""
            for role, text, _ in st.session_state.conversation:
                if role == "user":
                    prompt += f"User: {text}\n"
                else:
                    prompt += f"Bot: {text}\n"
            prompt += "Bot:"

            # Gemini LLM Response
            st.info("🤖 Thinking...")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                bot_reply = response.text.strip()
                bot_reply = f"{bot_reply} 😄"

                # -------------------------------
                # Save bot audio
                # -------------------------------
                audio_filename = os.path.join(
                    st.session_state.audio_dir,
                    f"bot_reply_{len(st.session_state.conversation)}.mp3"
                )
                tts = gTTS(bot_reply, lang="en")
                tts.save(audio_filename)

                # Append bot reply with audio file
                st.session_state.conversation.append(("bot", bot_reply, audio_filename))

                # -------------------------------
                # Play latest audio (HTML autoplay)
                # -------------------------------
                audio_bytes = open(audio_filename, "rb").read()
                audio_b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                <audio controls autoplay style="width:100%;">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    Your browser does not support the audio tag.
                </audio>
                """
                st.success("🤖 Bot Reply:")
                st.write(bot_reply)
                st.markdown(audio_html, unsafe_allow_html=True)

            except Exception as api_e:
                # Handle Gemini API 503 overload
                if hasattr(api_e, 'args') and len(api_e.args) > 0 and "503" in str(api_e.args[0]):
                    st.warning("🤖 The bot is busy right now. Please refresh the page and try again.")
                else:
                    st.error(f"Error: {api_e}")

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------------
# Show Conversation History (Optional)
# -------------------------------
with col2:
    if st.checkbox("Show Conversation History"):
        st.markdown("### 🗨️ Conversation History")
        for role, text, audio_file in st.session_state.conversation:
            if role == "user":
                st.markdown(f"**You:** {text}")
            else:
                st.markdown(f"**Bot:** {text}")
                if audio_file:
                    audio_bytes = open(audio_file, "rb").read()
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
