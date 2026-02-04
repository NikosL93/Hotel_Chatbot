import os
import sqlite3
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

# --- CONFIGURATION ---

FAQ_VECTOR_STORE_PATH = "vector_stores/faq_vector_store"
REVIEWS_VECTOR_STORE_PATH = "vector_stores/reviews_vector_store"
POIS_VECTOR_STORE_PATH = "vector_stores/pois_vector_store"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GOOD_EXAMPLES_VECTOR_STORE_PATH = "vector_stores/good_examples_vector_store"

# Load environment variables from .env file
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- LOAD VECTOR STORES ---

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

try:
    faq_vector_store = FAISS.load_local(FAQ_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Error loading FAQ vector store: {e}")
    faq_vector_store = None

try:
    reviews_vector_store = FAISS.load_local(REVIEWS_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Error loading reviews vector store: {e}")
    reviews_vector_store = None

try:
    pois_vector_store = FAISS.load_local(POIS_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Error loading POIs vector store: {e}")
    pois_vector_store = None

try:
    good_examples_vector_store = FAISS.load_local(GOOD_EXAMPLES_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Error loading good examples vector store: {e}")
    good_examples_vector_store = None

# --- TOOLS ---

@tool
def get_faq_answer(question: str) -> str:
    """
    Searches the hotel's FAQ for an answer to a specific question using vector similarity search.

    Args:
        question: The question to search for in the FAQ.
    """
    print(f"\n--- Searching FAQ for: {question}")
    if faq_vector_store:
        results = faq_vector_store.similarity_search(question, k=3)
        if results:
            return results[0].metadata['answer']
        else:
            return "I couldn't find an answer to that question in our FAQ."
    else:
        return "I'm sorry, I couldn't access the FAQ information right now."


@tool
def get_review_summary(topic: str) -> str:
    """
    Summarizes customer reviews based on a specific topic using vector similarity search.

    Args:
        topic: The topic to search for in the reviews ("breakfast", "staff", "pool",...). 
    """
    print(f"\n--- Summarizing reviews for: {topic}")
    if reviews_vector_store:
        results = reviews_vector_store.similarity_search(topic, k=3)
        if results:
            summary = f"Here's a summary of what our guests are saying about '{topic}':\n"
            for doc in results:
                metadata = doc.metadata
                summary += f"-(Rating: {metadata['rating']}): {metadata['review_text']}\n"
            return summary
        else:
            return f"I couldn't find any reviews mentioning '{topic}'."
    else:
        return "I'm sorry, I couldn't access the review information right now."


@tool
def find_points_of_interest(query: str) -> list:
    """
    Finds points of interest relevant to a user's query using vector similarity search.

    Args:
        query: A natural language query about points of interest ("museums near me", "good restaurants",...). 
    """
    print(f"\n--- Searching for POIs with query: {query}")
    if pois_vector_store:
        results = pois_vector_store.similarity_search(query, k=3)
        if results:
            poi_list = []
            for doc in results:
                metadata = doc.metadata
                poi_list.append({
                    'name': metadata.get('name'),
                    'address': metadata.get('address'),
                    'category': metadata.get('category')
                })
            return poi_list
        else:
            return ["I couldn't find any points of interest matching your query."]
    else:
        return ["I'm sorry, I couldn't access the points of interest information right now."]

@tool
def get_available_rooms(room_type: str) -> str:
    """
    Checks the availability of a specific room type in the hotel.

    Args:
        room_type: The type of room to check ("Standard", "Deluxe", "Suite").
    """
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hotel_rooms WHERE UPPER(room_type) = UPPER(?) AND availability = 1", (room_type.strip(),))
    count = cursor.fetchone()[0]
    conn.close()
    if count > 0:
        return f"Yes, we have {count} {room_type} rooms available."
    else:
        return f"Sorry, we don't have any {room_type} rooms available."

@tool
def get_room_info(room_type: str) -> str:
    """
    Gets information about a specific room type, including price.

    Args:
        room_type: The type of room to get information about ("Standard", "Deluxe", "Suite").
    """
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT price_per_night FROM hotel_rooms WHERE UPPER(room_type) = UPPER(?)" , (room_type.strip(),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return f"A {room_type} room costs {result[0]}euros per night."
    else:
        return f"Sorry, I couldn't find any information about {room_type} rooms."

@tool
def get_all_room_types() -> list:
    """Gets all available room types from the database."""
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT room_type FROM hotel_rooms")
    room_types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return room_types

# --- MAIN HANDLER ---

def handle_user_input(user_question, language, memory):
    """The main function of chatbot's logic."""

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        model_kwargs={"extra_headers": {"X-Project-Name": "Hotel Chatbot"}},
        metadata={"ls_provider": "openai", "ls_model_name": "deepseek-chat"},
        streaming=False
    )

    tools = [get_faq_answer, get_review_summary, find_points_of_interest, get_available_rooms, get_room_info, get_all_room_types]

    # Retrieve good examples of llm-answers, remember to run update_good_conversations_vector_store.py for updating the vector store with good examples
    examples = ""
    if good_examples_vector_store:
        results = good_examples_vector_store.similarity_search(user_question, k=2)
        if results:
            examples = "\n".join([f"Question: {doc.page_content}\nResponse: {doc.metadata['response']}" for doc in results])

    prompt_template = """
    You are a persuasive assistant for The Grand Cretan Resort Hotel. Your primary goal is to convince users to book a stay at the hotel. While answering their questions, always highlight the hotel's best features and create a sense of desirability.
    When asked about rooms, you should first get all the available room types, then for each room type get the info and availability. When the user asks a question in a language other than English, you must translate the query to English before using any of the tools.
    Answer only in this language: {language}. 

    Current conversation:
    {chat_history}

    Before answering, consider these examples of good answers to similar questions:
    {examples}
    
    IMPORTANT: If the user's question is directly answered by one of the examples above, YOU MUST SKIP THE TOOLS. instead, your Thought should be "The answer is in the examples" and you should provide the Final Answer immediately.
    
    You have access to the following tools:
    {tools}

    Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question.

    Begin

    Question: {input}
    Thought:{agent_scratchpad}
    """
    # agent_scratchpad = variable where LangChain stores the intermediate steps (Thoughts, Actions, and Observations) like memory for generating asnwer

    prompt = PromptTemplate.from_template(prompt_template)

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        memory=memory
    )

    response = agent_executor.invoke({
        "input": user_question,
        "language": language,
        "examples": examples
    })

    return response["output"]
