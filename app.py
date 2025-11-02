import streamlit as st
from chatbot import handle_user_input
import sqlite3

# --- UI CONFIGURATION ---
st.set_page_config(page_title="The Grand Resort Hotel Chatbot", page_icon=":robot_face:")

# --- DATABASE & FEEDBACK FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('hotel.db')

def initialize_conversation():
    if 'conversation_id' not in st.session_state:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations DEFAULT VALUES")
        st.session_state.conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()

def log_turn(conversation_id, prompt, response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversation_turns (conversation_id, prompt, response) VALUES (?, ?, ?)",
        (conversation_id, prompt, response)
    )
    turn_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return turn_id

def save_feedback(turn_id, feedback):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE conversation_turns SET feedback = ? WHERE turn_id = ?", (feedback, turn_id))
    conn.commit()
    conn.close()

# --- UI TRANSLATIONS ---
UI_TRANSLATIONS = {
    "en": {
        "title": "The Grand Resort Hotel Chatbot",
        "welcome_message": "Welcome to The Grand Resort Hotel! How can I assist you today?",
        "question_label": "Your question...",
        "feedback_good": "👍 Good",
        "feedback_bad": "👎 Bad",
        "feedback_saved": "Feedback saved!"
    },
    "el": {
        "title": "The Grand Resort Hotel Chatbot",
        "welcome_message": "Καλώς ήρθατε στο The Grand Resort Hotel! Πώς μπορώ να σας εξυπηρετήσω;",
        "question_label": "Η ερώτησή σας...",
        "feedback_good": "👍 Καλό",
        "feedback_bad": "👎 Κακό",
        "feedback_saved": "Η αξιολόγηση αποθηκεύτηκε!"
    }
}

# --- INITIALIZE SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"author": "bot", "message": UI_TRANSLATIONS[st.session_state.lang]["welcome_message"], "turn_id": 0})

initialize_conversation()

# --- LANGUAGE SELECTION ---
selected_lang = st.sidebar.selectbox(
    "Language", ["en", "el"], index=["en", "el"].index(st.session_state.lang), key="lang_selector"
)

if st.session_state.lang != selected_lang:
    st.session_state.lang = selected_lang
    st.session_state.messages = [{"author": "bot", "message": UI_TRANSLATIONS[selected_lang]["welcome_message"], "turn_id": 0}]
    st.rerun()

ui = UI_TRANSLATIONS.get(st.session_state.lang, UI_TRANSLATIONS["en"])

st.title(ui["title"])

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["author"]):
        st.markdown(msg["message"])
        if msg["author"] == "bot" and msg["turn_id"] > 0:
            turn_id = msg["turn_id"]
            col1, col2 = st.columns(2)
            with col1:
                if st.button(ui["feedback_good"], key=f"good_{turn_id}"):
                    save_feedback(turn_id, 'good')
                    st.toast(ui["feedback_saved"])
            with col2:
                if st.button(ui["feedback_bad"], key=f"bad_{turn_id}"):
                    save_feedback(turn_id, 'bad')
                    st.toast(ui["feedback_saved"])

# --- USER INPUT ---
if prompt := st.chat_input(ui["question_label"]):
    st.session_state.messages.append({"author": "user", "message": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("bot"):
        with st.spinner("Thinking..."):
            response = handle_user_input(prompt, st.session_state.lang)
            st.markdown(response)
            turn_id = log_turn(st.session_state.conversation_id, prompt, response)
            st.session_state.messages.append({"author": "bot", "message": response, "turn_id": turn_id})
    st.rerun()
