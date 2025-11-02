from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from chatbot import handle_user_input

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

# A UI translation set
UI_TRANSLATIONS = {
    "en": {
        "title": "The Grand Cretan Resort Hotel Chatbot",
        "welcome_message": "Welcome to The Grand Cretan Resort Hotel! How can I assist you today? Feel free to ask about our amenities, policies, nearby attractions, or anything else.",
        "question_label": "Your question...",
        "send_button": "Send"
    },
    "el": {
        "title": "The Grand Cretan Resort Hotel Chatbot",
        "welcome_message": "Καλώς ήρθατε στο The Grand Cretan Resort Hotel! Πώς μπορώ να σας εξυπηρετήσω σήμερα; Ρωτήστε με για τις ανέσεις, τις πολιτικές μας, τα κοντινά αξιοθέατα ή οτιδήποτε άλλο.",
        "question_label": "Η ερώτησή σας...",
        "send_button": "Αποστολή"
    }
}

@app.route("/<lang>")
@app.route("/")
def index(lang="en"): # Default to English-
    ui = UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["en"])
    initial_bot_message = ui["welcome_message"]
    messages = [('bot', initial_bot_message)]
    return render_template("index.html", messages=messages, ui=ui, current_lang=lang)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("user_input", "")
    if not user_input:
        return jsonify({"response": "Please type a question."})

    response = handle_user_input(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
