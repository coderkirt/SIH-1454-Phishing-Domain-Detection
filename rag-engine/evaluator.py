import os
import json
import sys
import time
from dotenv import load_dotenv

# Windows consoles default to cp1252 and crash on the ✅/❌ status glyphs.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from app.core.logger import ResultLogger
from app.core.validator import LLMValidator
from app.services.rag_engine import RAGEngine

# Paths
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
DATA_DIR = os.path.join(basedir, "app", "data")
DB_DIR = os.path.join(basedir, "chroma_db")

# Initialize
engine = RAGEngine(DATA_DIR, DB_DIR)
engine.initialize()
logger = ResultLogger(log_file="qa_audit_report.json")
validator = LLMValidator(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model=os.getenv("EVAL_MODEL", "qwen/qwen3.8-27b")
)

def run_evaluation():
    print(f"DEBUG: Checking collection state...")
    collection = engine.vector_store._collection
    
    # VITAL CHANGE: Extract unique, dynamic categories from the database metadata
    all_metadatas = collection.get(include=['metadatas'])['metadatas']
    available_categories = list(set(m.get('category') for m in all_metadatas if m.get('category')))
    print(f"DEBUG: Categories detected in DB: {available_categories}")
    
    test_file = os.path.join(basedir, 'qa_suite/test_cases.json')
    with open(test_file, 'r') as f:
        test_cases = json.load(f)

    print(f"\n--- Starting Evaluation: {len(test_cases)} Test Cases ---\n")
    
    for i, case in enumerate(test_cases, 1):
        question = case.get('question', 'N/A')
        expected = case.get('expected_answer', '')
        test_cat = case.get('category')
        is_negative = case.get('is_negative', False)
        
        # VITAL CHANGE: Dynamically match test category to DB category
        # Uses fuzzy match to bridge 'Test Category' vs 'Actual DB Label'
        filter_dict = None
        if not is_negative and test_cat != "Cross-Domain Synthesis":
            # Find the best match from available_categories
            match = next((c for c in available_categories if c.lower() in test_cat.lower() or test_cat.lower() in c.lower()), None)
            filter_dict = {"category": match} if match else None
        
        print(f"[{i}] Testing: {question[:50]}... | Filter: {filter_dict}")
        
        response = engine.query(question, filter_dict=filter_dict)
        actual = response.get("answer", "") if isinstance(response, dict) else str(response)
        metadata = response.get("metadata", []) if isinstance(response, dict) else []
        source_names = list(set([m.get('file_name', 'Unknown') for m in metadata]))
        
        # DEBUG: Check if database is actually working
        if not metadata:
            print(f"!!! DEBUG: Query returned zero chunks. Check RAGEngine/ChromaDB state.")
        
        # 3. Logic: Strict Grounding Safety Guard
        has_source = len(metadata) > 0
        if not has_source and not is_negative:
            passed = False
            result = {"score": 0, "rationale": "CRITICAL: No context retrieved for standard query."}
        
        # 4. Logic: Negative Test Verification
        elif is_negative:
            keywords = ["does not", "cannot", "no information", "not mentioned"]
            passed = any(k in actual.lower() for k in keywords)
            result = {"score": 10 if passed else 0, "rationale": "Negative inference check."}
            
        else:
            # Standard LLM-as-a-Judge
            result = validator.evaluate(question, expected, actual)
            passed = result.get('score', 0) >= 8
        
        # Final Logging
        is_valid = passed and (has_source or is_negative)
        status = "✅ PASS" if is_valid else "❌ FAIL"
        
        logger.log(question, expected, actual, is_valid, source_names)
        
        print(f"Result:   {status} | Score: {result.get('score')}/10")
        print(f"Rationale: {result.get('rationale')}")
        print(f"Sources:  {', '.join(source_names)}")
        print("-" * 60)
        time.sleep(2)

if __name__ == "__main__":
    run_evaluation()