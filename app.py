import streamlit as st
from chatbot import handle_user_input

# --- UI CONFIGURATION ---
st.set_page_config(page_title="The Grand  Resort Hotel Chatbot", page_icon=":robot_face:")

# A UI translation set
UI_TRANSLATIONS = {
    "en": {
        "title": "The Grand  Resort Hotel Chatbot",
        "welcome_message": "Welcome to The Grand  Resort Hotel! How can I assist you today? Feel free to ask about our amenities, nearby attractions, or anything else.",
        "question_label": "Your question...",
        "send_button": "Send"
    },
    "el": {
        "title": "The Grand  Resort Hotel Chatbot",
        "welcome_message": "Καλώς ήρθατε στο The Grand  Resort Hotel! Πώς μπορώ να σας εξυπηρετήσω σήμερα; Ρωτήστε με για τις ανέσεις, τα κοντινά αξιοθέατα ή οτιδήποτε άλλο.",
        "question_label": "Η ερώτησή σας...",
        "send_button": "Αποστολή"
    }
}

# --- INITIALIZE SESSION STATE ---
# This ensures that variables persist across reruns of the app.
if 'lang' not in st.session_state:
    st.session_state.lang = "en" # Default language is English
if "messages" not in st.session_state:
    # Initialize chat history with a welcome message from the bot
    st.session_state.messages = [("bot", UI_TRANSLATIONS[st.session_state.lang]["welcome_message"])]

# --- LANGUAGE SELECTION WIDGET ---
# Allows the user to choose the language of the chatbot interface.
selected_lang = st.sidebar.selectbox(
    "Language",
    ["en", "el"],
    index=["en", "el"].index(st.session_state.lang), # Set initial selection based on current session language
    key="lang_selector" # Unique key for the widget
)

# Check if the language has changed
if st.session_state.lang != selected_lang:
    st.session_state.lang = selected_lang # Update the session language
    # Reset messages to show the welcome message in the new language
    st.session_state.messages = [("bot", UI_TRANSLATIONS[selected_lang]["welcome_message"])]
    st.rerun() # Rerun the app to apply language changes immediately

# Get the UI translations for the current language
ui = UI_TRANSLATIONS.get(st.session_state.lang, UI_TRANSLATIONS["en"])

# Set the title of the Streamlit application
st.title(ui["title"])

# --- DISPLAY CHAT HISTORY ---
# Iterate through all messages stored in the session state and display them.
for author, message in st.session_state.messages:
    with st.chat_message(author):
        st.markdown(message)

# --- USER INPUT ---
# This is where the user types their question.
prompt = st.chat_input(ui["question_label"])

if prompt:
    # Add the user's message to the chat history
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display a thinking message while the bot processes the input
    with st.chat_message("bot"):
        with st.spinner("Thinking..."):
            response = handle_user_input(prompt, st.session_state.lang)  # Call the chatbot's logic
            st.markdown(response)

    # Add the bot's response to the chat history
    st.session_state.messages.append(("bot", response))