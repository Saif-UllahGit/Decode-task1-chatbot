import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==================================================
# Page Configuration (Must be first Streamlit command)
# ==================================================

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
)

# ==================================================
# Load External CSS
# ==================================================

from pathlib import Path

def load_css(file_name):
    css_path = Path(__file__).parent / file_name

    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css("styles.css")

# ==================================================
# Load Environment Variables
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found in the .env file.")
    st.stop()

# ==================================================
# Gemini Client
# ==================================================

client = genai.Client(api_key=API_KEY)

# ==================================================
# Header
# ==================================================

st.markdown(
    """
    <div class="main-title">
        🤖 AI Assistant
    </div>

    <div class="subtitle">
        Powered by <b>Gemini 2.5 Flash</b><br>
        Ask anything and continue conversations naturally.
    </div>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Session State
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==================================================
# Display Previous Messages
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==================================================
# Chat Input
# ==================================================

prompt = st.chat_input("💬 Ask me anything...")

if prompt:

    # ----------------------------
    # Save User Message
    # ----------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # ----------------------------
    # Build Conversation History
    # ----------------------------

    conversation = ""

    for message in st.session_state.messages:

        if message["role"] == "user":
            conversation += f"User: {message['content']}\n"

        else:
            conversation += f"Assistant: {message['content']}\n"

    conversation += "Assistant:"

    # ----------------------------
    # Generate Response
    # ----------------------------

    try:

        with st.chat_message("assistant"):

            with st.spinner("🤖 Thinking..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=conversation,
                )

                answer = (
                    response.text
                    if response.text
                    else "Sorry, I couldn't generate a response."
                )

            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    except Exception as e:
        st.error(f"❌ {e}")

# ==================================================
# Sidebar
# ==================================================

with st.sidebar:

    st.title("⚙️ Control Panel")

    st.info(
        "This chatbot remembers your conversation only during the current session."
    )

    st.metric(
        label="Messages",
        value=len(st.session_state.messages),
    )

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages.clear()
        st.rerun()

    st.markdown("---")

    st.success("✅ Gemini 2.5 Flash Connected")

    st.caption("Built with ❤️ using Streamlit + Google Gemini")