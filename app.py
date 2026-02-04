import streamlit as st
from chatbot_logic import handle_user_input
import sqlite3
from langchain.memory import ConversationBufferWindowMemory

# --- UI CONFIGURATION ---
st.set_page_config(page_title="The Grand Resort Hotel Chatbot", page_icon=":robot_face:")

# --- DATABASE & FEEDBACK FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('hotel.db')

def initialize_conversation():
    if 'conversation_id' not in st.session_state:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Create a new conversation session with current time
        cursor.execute("INSERT INTO conversation_session DEFAULT VALUES")
        st.session_state.conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()

    if 'memory' not in st.session_state:
        # memory_key: The name of the variable in  prompt template ({chat_history})
        # input_key: Tells the memory which specific input variable is the user's message (there are 3 variables: language, examples, input)
        st.session_state.memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="input")

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
    # The turn_id is 0 for the initial welcome message
    st.session_state.messages.append({"role": "bot", "message": UI_TRANSLATIONS[st.session_state.lang]["welcome_message"], "turn_id": 0})

initialize_conversation()

# --- LANGUAGE SELECTION ---
selected_lang = st.sidebar.selectbox(
    "Language", ["en", "el"], index=["en", "el"].index(st.session_state.lang), key="lang_selector"
)

if st.session_state.lang != selected_lang:
    st.session_state.lang = selected_lang
    st.session_state.messages = [{"role": "bot", "message": UI_TRANSLATIONS[selected_lang]["welcome_message"], "turn_id": 0}]
    # Reset memory for new conversation
    st.session_state.memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="input")
    st.rerun()

ui = UI_TRANSLATIONS.get(st.session_state.lang, UI_TRANSLATIONS["en"])

st.title(ui["title"])

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    # "With" inserts messages in a block
    with st.chat_message(msg["role"]):
        st.markdown(msg["message"])
        # Buttons for feedback
        if msg["role"] == "bot" and msg["turn_id"] > 0:
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
                    st.toast(ui["feedback_saved"])

# --- USER INPUT ---
prompt = st.chat_input(ui["question_label"])
if prompt:
    st.session_state.messages.append({"role": "user", "message": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("bot"):
        with st.spinner("Thinking..."):
            response = handle_user_input(prompt, st.session_state.lang, st.session_state.memory)
            st.markdown(response)
            turn_id = log_turn(st.session_state.conversation_id, prompt, response)
            st.session_state.messages.append({"role": "bot", "message": response, "turn_id": turn_id})
    st.rerun()
