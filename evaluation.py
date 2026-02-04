import os
import json
import time
import pandas as pd
from langchain_openai import ChatOpenAI
from chatbot_logic import handle_user_input
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv

# --- CONFIG DEEPSEEK ---
load_dotenv()
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

judge_llm = ChatOpenAI(
    model="deepseek-chat", 
    openai_api_key=DEEPSEEK_KEY,
    openai_api_base="https://api.deepseek.com",
    temperature=0
)

# --- ΦΟΡΤΩΣΗ ΣΕΝΑΡΙΩΝ ΑΠΟ CSV ---
SCENARIOS_FILE = "evaluation/test_scenarios.csv"

if os.path.exists(SCENARIOS_FILE):
    df_scenarios = pd.read_csv(SCENARIOS_FILE)
    test_scenarios = df_scenarios.to_dict(orient="records")
else:
    print(f"Error: {SCENARIOS_FILE} not found!")
    test_scenarios = []

def grade_response(question, response, truth):
    """Ρωτάει το DeepSeek να βαθμολογήσει την απάντηση συγκρίνοντας με την αλήθεια"""
    prompt = f"""
    You are an expert hotel manager evaluating a chatbot's response. 
    
    Question asked by guest: {question}
    Chatbot Response: {response}
    
    CORRECT ANSWER (Ground Truth): {truth}
    
    Grade the response on a scale of 0 to 5 for the following criteria:
    1. Accuracy: Does the chatbot's response match the CORRECT ANSWER? (0=Wrong, 5=Perfect Match)
    2. Relevance: Did the chatbot directly answer the specific question asked? (0=Irrelevant, 5=Highly Relevant)
    3. Persuasiveness: Does it encourage the guest to book the hotel? (0=Boring, 5=Very Persuasive)
    4. Hallucination: Is the answer consistent with the Ground Truth? (0=Faithful/No Hallucination5, 5=Hallucination/Contradiction)
    
    Return ONLY a valid JSON object in this format:
    {{"accuracy": 5, "relevance": 5, "persuasiveness": 5, "hallucination": 5, "reason": "brief explanation"}}
    """
    
    try:
        res = judge_llm.invoke(prompt)
        content = res.content.strip()
        
        # Καθαρισμός markdown αν υπάρχει
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Error grading: {e}")
        return {"accuracy": 0, "relevance": 0, "persuasiveness": 0, "hallucination": 0, "reason": "error"}

# --- ΕΝΑΡΞΗ ΑΞΙΟΛΟΓΗΣΗΣ ---
results = []

print("Starting Evaluation...")

for scenario in test_scenarios:
    q = scenario["question"]
    truth = scenario["ground_truth"]
    
    print(f"Testing question: {q}")
    
    # 1. Μέτρηση Latency και απάντηση από το chatbot
    start_time = time.time()
    memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", input_key="input")
    
    # Ανίχνευση γλώσσας
    lang = "el" if any(char > '\u0370' for char in str(q)) else "en"
    
    chatbot_res = handle_user_input(q, lang, memory)
    end_time = time.time()
    latency = end_time - start_time
    
    # 2. Βαθμολογούμε συγκρίνοντας με την αλήθεια
    grades = grade_response(q, chatbot_res, truth)
    
    # 3. Αποθηκεύουμε
    results.append({
        "Question": q,
        "Response": chatbot_res,
        "Latency": round(latency, 2),
        "Accuracy": grades.get("accuracy", 0),
        "Relevance": grades.get("relevance", 0),
        "Persuasiveness": grades.get("persuasiveness", 0),
        "Hallucination": grades.get("hallucination", 0),
        "Reason": grades.get("reason", "")
    })

# --- ΑΠΟΘΗΚΕΥΣΗ ---
df = pd.DataFrame(results)

# Υπολογισμός μέσων όρων με στρογγυλοποίηση
averages = {
    "Question": "AVERAGE SCORE",
    "Response": "-",
    "Latency": round(df['Latency'].mean(), 2),
    "Accuracy": round(df['Accuracy'].mean(), 2),
    "Relevance": round(df['Relevance'].mean(), 2),
    "Persuasiveness": round(df['Persuasiveness'].mean(), 2),
    "Hallucination": round(df['Hallucination'].mean(), 2),
    "Reason": "-"
}

# Προσθήκη της γραμμής μέσων όρων στο τέλος
df_final = pd.concat([df, pd.DataFrame([averages])], ignore_index=True)

# Αποθήκευση του τελικού DataFrame
df_final.to_csv("evaluation/evaluation_results.csv", index=False)
print("\nResults saved to evaluation/evaluation_results.csv")
