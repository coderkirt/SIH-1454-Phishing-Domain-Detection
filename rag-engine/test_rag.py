import sys, os
sys.path.append(os.getcwd())

# Import the CLASS instead of the function
from app.services.rag_engine import RAGEngine

# Initialize the engine
engine = RAGEngine(data_dir="app/data", db_dir="chroma_db")
engine.initialize()

# Run the query using the class instance
res = engine.query("What is a loss function?")

# Print the keys to verify
print(f"DEBUG: Keys in response: {res.keys()}")

if 'metadata' in res:
    print(f"DEBUG: Retrieved {len(res['metadata'])} metadata entries")
    print(f"DEBUG: First source: {res['metadata'][0]}")
else:
    print("ERROR: No 'metadata' key found in the response!")

print(f"DEBUG: Answer: {res['answer']}")