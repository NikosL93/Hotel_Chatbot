import sqlite3
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION ---
DB_PATH = 'hotel.db'
VECTOR_STORE_PATH = "vector_stores/good_examples_vector_store"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def update_vector_store():
    """Connects to the database, retrieves good conversations, and updates the vector store."""
    print("Connecting to the database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Retrieving good conversations...")
    cursor.execute("SELECT prompt, response FROM conversation_turns WHERE feedback = 'good'")
    good_conversations = cursor.fetchall()
    conn.close()

    if not good_conversations:
        print("No new good conversations to add.")
        return

    print(f"Found {len(good_conversations)} good conversations.")

    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # Create documents for the vector store
    documents = [prompt for prompt, response in good_conversations]
    metadatas = [{"response": response} for prompt, response in good_conversations]

    print("Creating or updating the vector store...")
    try:
        # Load existing vector store
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_texts(texts=documents, metadatas=metadatas)
        print("Vector store updated.")
    except Exception as e:
        # Create new vector store if it doesn't exist
        print(f"Creating new vector store: {e}")
        vector_store = FAISS.from_texts(texts=documents, embedding=embeddings, metadatas=metadatas)
        print("New vector store created.")

    # Save the vector store
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector store saved to {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    update_vector_store()
