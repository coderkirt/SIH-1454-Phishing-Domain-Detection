import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Use the same path and embedding as your rag_engine.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
local_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the database
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=local_embeddings)

# Check how many documents are inside
count = vector_store._collection.count()
print(f"DEBUG: The database contains {count} documents.")