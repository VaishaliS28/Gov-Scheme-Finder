import os
import json
import chromadb
from chromadb.utils import embedding_functions

def setup_database():
    print("Initializing Vector Database...")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Using a lightweight, fast embedding model
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name="india_schemes",
        embedding_function=embedding_func
    )

    print("Loading schemes.json...")
    
    # --- DYNAMIC PATH FIX ---
    # 1. Find exactly where this ingest.py file lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Build the exact path to the json file dynamically
    json_path = os.path.join(current_dir, "..", "data", "schemes.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for i, scheme in enumerate(schemes):
        # Create a rich text chunk for the AI to read
        text_chunk = f"Name: {scheme['name']}. Ministry: {scheme['ministry']}. Description: {scheme['description']} Eligibility: {scheme['eligibility']} Benefits: {scheme['benefits']}"
        
        documents.append(text_chunk)
        metadatas.append({
            "name": scheme["name"],
            "url": scheme.get("url", ""),
            "category": scheme.get("category", "General")
        })
        ids.append(f"scheme_{i}")

    print(f"Upserting {len(schemes)} schemes into ChromaDB...")
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print("Database sync complete! 🚀")

if __name__ == "__main__":
    setup_database()