import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

FAQ_CSV_PATH = "faq.csv"
REVIEWS_CSV_PATH = "hotel_Reviews_dataset.csv"
POIS_CSV_PATH = "pois.csv"
FAQ_VECTOR_STORE_PATH = "faq_vector_store"
REVIEWS_VECTOR_STORE_PATH = "reviews_vector_store"
POIS_VECTOR_STORE_PATH = "pois_vector_store"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def setup():
    """
    Creates the vector stores for the hotel chatbot.
    """
    # Initialize HuggingFaceEmbeddings with the specified model name.
    # This model will be used to convert text into numerical vector representations,
    # which are essential for creating the FAISS vector stores.
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # Create FAISS vector store for FAQs
    try:
        faq_df = pd.read_csv(FAQ_CSV_PATH)
        documents = faq_df['question'].tolist()
        metadatas = faq_df.to_dict('records')
        vector_store = FAISS.from_texts(documents, embeddings, metadatas=metadatas)
        vector_store.save_local(FAQ_VECTOR_STORE_PATH)
        print(f"FAISS vector store for FAQs created at '{FAQ_VECTOR_STORE_PATH}'.")
    except (FileNotFoundError, Exception) as e:
        print(f"Error creating FAQ vector store: {e}")

    # Create FAISS vector store for reviews
    try:
        reviews_df = pd.read_csv(REVIEWS_CSV_PATH)
        #List of reviews text only ['Excellent hotel!', 'Great location, close to many attractions.', ...]
        documents = reviews_df['review_text'].tolist()
        metadatas = reviews_df.to_dict('records')
        vector_store = FAISS.from_texts(documents, embeddings, metadatas=metadatas)
        vector_store.save_local(REVIEWS_VECTOR_STORE_PATH)
        print(f"FAISS vector store for reviews created at '{REVIEWS_VECTOR_STORE_PATH}'.")
    except (FileNotFoundError, Exception) as e:
        print(f"Error creating reviews vector store: {e}")

    # Create FAISS vector store for POIs
    try:
        pois_df = pd.read_csv(POIS_CSV_PATH)
        # Combine name and category for a richer document
        documents = (pois_df['name'] + " - " + pois_df['category']).tolist()
        metadatas = pois_df.to_dict('records')
        vector_store = FAISS.from_texts(documents, embeddings, metadatas=metadatas)
        vector_store.save_local(POIS_VECTOR_STORE_PATH)
        print(f"FAISS vector store for POIs created at '{POIS_VECTOR_STORE_PATH}'.")
    except (FileNotFoundError, Exception) as e:
        print(f"Error creating POIs vector store: {e}")

if __name__ == "__main__":
    setup()
