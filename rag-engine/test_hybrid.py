import sys
import os

# Point to the directory
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'services'))
sys.path.insert(0, module_path)

# Import the class instead of the functions
from rag_engine import RAGEngine

def run_test():
    print("--- Starting Hybrid Retrieval Test ---")
    
    # Instantiate the engine (you might need to adjust data_dir/db_dir paths)
    engine = RAGEngine(data_dir="app/data", db_dir="chroma_db")
    engine.initialize()
    
    # Test 1: Blind query
    print("\nRunning blind query...")
    res1 = engine.query("What is the primary objective of this project?")
    print(f"Answer: {res1['answer']}")

    # Test 2: Filtered query
    print("\nRunning filtered query (forcing SANS paper)...")
    filter_val = {"file_name": "SANS-Bridging-Gap-Between-Threat-Intelligence-Business-Risk_Garvey.pdf"}
    res2 = engine.query("What is the primary objective of this project?", filter_dict=filter_val)
    print(f"Answer: {res2['answer']}")

    # Verification
    expected_file = "SANS-Bridging-Gap-Between-Threat-Intelligence-Business-Risk_Garvey.pdf"
    for meta in res2['metadata']:
        assert meta.get('file_name') == expected_file, f"Filter failed! Expected {expected_file} but got {meta.get('file_name')}"
    print("\n✅ Filtered Query Test: PASS")

if __name__ == "__main__":
    run_test()