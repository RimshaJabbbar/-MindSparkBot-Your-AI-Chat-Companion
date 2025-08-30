from dotenv import load_dotenv
import os
import json
import random
from datetime import datetime
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set app title
st.set_page_config(page_title="MindSparkBot💡", page_icon="💡")

# Theme toggle in sidebar
with st.sidebar:
    st.markdown("## 🎨 Theme Settings")
    theme = st.radio("Choose Theme", ["🌞 Light", "🌙 Dark"])

# Apply theme
if theme == "🌞 Light":
    st.markdown("""
        <style>
        .stApp { background-color: #fefefe; color: black; }
        .sidebar .sidebar-content { background-color: #e3f2fd; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #121212; color: white; }
        .sidebar .sidebar-content { background-color: #1e1e1e; }
        .stMarkdown, .stTextInput, .stChatMessage, .stSelectbox, .stTextArea { color: white; }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MindSparkBot💡", page_icon="💡")
st.title(" Mind_Spark_Bot ")

# Time and date display
now = datetime.now()
current_time = now.strftime("%H:%M")
current_day = now.strftime("%A, %d %B %Y")
st.markdown(f"🕒 **{current_time}** • {current_day}")

# Daily quote or joke
quotes = [
    "🌟 Believe you can and you're halfway there.",
    "💪 Push yourself, because no one else is going to do it for you.",
    "😂 Why don’t scientists trust atoms? Because they make up everything!",
    "🔥 Success is not for the lazy. Keep going!"
]
if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(quotes)
st.markdown(f"💬 **MindSparkBot says:** _{st.session_state.daily_quote}_")

# Sidebar controls
with st.sidebar:
    st.subheader("🎛️ Controls")

    # Chat session management
    if "chats" not in st.session_state:
        st.session_state.chats = {}
        st.session_state.active_chat = None
        st.session_state.notes = {}

    chat_names = list(st.session_state.chats.keys())
    selected_chat = st.selectbox("🗂️ Select Chat", chat_names + ["➕ Start New Chat"])

    if selected_chat == "➕ Start New Chat":
        new_name = st.text_input("📝 Name your chat")
        if new_name and new_name not in st.session_state.chats:
            st.session_state.chats[new_name] = InMemoryChatMessageHistory()
            st.session_state.notes[new_name] = ""
            st.session_state.active_chat = new_name
            st.rerun()
    else:
        st.session_state.active_chat = selected_chat

    if st.session_state.active_chat:
        if st.button("🗑️ Delete This Chat"):
            del st.session_state.chats[st.session_state.active_chat]
            del st.session_state.notes[st.session_state.active_chat]
            st.session_state.active_chat = None
            st.rerun()

        if st.button("🧹 Clear This Chat"):
            st.session_state.chats[st.session_state.active_chat] = InMemoryChatMessageHistory()
            st.session_state.notes[st.session_state.active_chat] = ""
            st.rerun()

    # Personality input
    personality_options = ["Friendly ", "Sarcastic ", "Motivational ", "Formal ", "Playful "]
    personality_choice = st.selectbox("🎭 Choose Personality", personality_options + ["Custom"])
    if personality_choice == "Custom":
        custom_personality = st.text_input("✍️ Write your own bot personality")
    else:
        custom_personality = personality_choice

    # Language input
    language_options = [
        "English", "Urdu 🇵🇰", "Punjabi ", "Hindi 🇮🇳", "Arabic ",
        "French 🇫🇷", "Spanish 🇪🇸", "German 🇩🇪", "Chinese 🇨🇳", "Japanese 🇯🇵",
        "Korean 🇰🇷", "Turkish 🇹🇷", "Russian 🇷🇺", "Italian 🇮🇹", "Portuguese 🇧🇷"
    ]
    language_choice = st.selectbox("🌐 Choose Language", language_options + ["Other"])
    if language_choice == "Other":
        custom_language = st.text_input("✍️ Type your language")
    else:
        custom_language = language_choice

    # Model and creativity
    model_name = st.selectbox("🧠 Groq Model", [
        "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "llama-3.1-8b-instant"
    ], index=2)
    temperature = st.slider("🎨 Creativity Level", 0.0, 1.0, 0.7)
    max_tokens = st.slider("🔢 Max Tokens", 50, 2000, 150)

    # System instructions
    system_prompt = f"""
You are MindSparkBot 💡, a smart, expressive, and multilingual chatbot created by Misha.

Your mission:
- You are a helpful, concise teaching assistant. Use short, clear explanations.
- Speak in {custom_language} with fluency and cultural respect.
- Match the personality: {custom_personality}
- Use emojis naturally to make the conversation lively and fun.
- Keep responses short, clear, and engaging unless asked for detail.
- Never sound robotic—be warm, human-like, and full of personality.
- Always adapt your tone and style to make the user feel heard and understood.
"""

    st.caption("💡 Tip: You can write your own bot personality or language!")

# API key check
if not GROQ_API_KEY:
    st.error("🚫 Missing GROQ_API_KEY. Add it to your .env or deployment secrets.")
    st.stop()

# Initialize active chat
if st.session_state.active_chat and st.session_state.active_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.active_chat] = InMemoryChatMessageHistory()
    st.session_state.notes[st.session_state.active_chat] = ""

# Set up model and chain
llm = ChatGroq(model=model_name, temperature=temperature, max_tokens=max_tokens)
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | llm | StrOutputParser()

chat_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: st.session_state.chats[session_id],
    input_messages_key="input",
    history_messages_key="history",
)

# Render conversation
if st.session_state.active_chat:
    for msg in st.session_state.chats[st.session_state.active_chat].messages:
        role = getattr(msg, "type", None) or getattr(msg, "role", "")
        content = msg.content
        if role == "human":
            st.chat_message("user").write(f"👤 {content}")
        elif role in ("ai", "assistant"):
            st.chat_message("assistant").write(f"🤖 {content}")

# Handle user input
user_input = st.chat_input("💬 Type your message...")
if user_input and st.session_state.active_chat:
    st.chat_message("user").write(f"👤 {user_input}")
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            response_text = chat_with_history.invoke(
                {"input": user_input, "system_prompt": system_prompt},
                config={"configurable": {"session_id": st.session_state.active_chat}},
            )
        except Exception as e:
            st.error(f"⚠️ Model error: {e}")
            response_text = ""
        typed = ""
        for ch in response_text:
            typed += ch
            placeholder.markdown(f"🤖 {typed}")

# Chat summary and downloads
if st.session_state.active_chat:
    messages = st.session_state.chats[st.session_state.active_chat].messages
    summary = "📝 Summary Notes:\n"
    for m in messages:
        role = getattr(m, "role", "")
        if role == "human":
            summary += f"- User asked: {m.content}\n"
        elif role in ("ai", "assistant"):
            summary += f"- Bot replied: {m.content[:60]}...\n"

    manual_notes = st.sidebar.text_area("🧾 Your Notes", value=st.session_state.notes[st.session_state.active_chat], height=300)
    st.session_state.notes[st.session_state.active_chat] = manual_notes
    full_summary = summary + "\n" + manual_notes

    export = [{"role": getattr(m, "role", ""), "text": m.content} for m in messages]

    st.sidebar.download_button(
        "⬇️ Download Chat (.json)",
        data=json.dumps({
            "chat_name": st.session_state.active_chat,
            "messages": export,
            "summary": full_summary
        }, ensure_ascii=False, indent=2),
        file_name=f"{st.session_state.active_chat}_summary.json",
        mime="application/json",
        use_container_width=True,
    )

    st.sidebar.download_button(
        "⬇️ Download Summary (.txt)",
        data=full_summary,
        file_name=f"{st.session_state.active_chat}_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )
