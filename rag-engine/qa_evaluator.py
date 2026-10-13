import json
from langchain_groq import ChatGroq

# Using a high-reasoning model for the audit process
qa_model = ChatGroq(model_name="qwen/qwen3.8-27b", temperature=0)

def perform_audit(question, answer, context):
    """
    Performs a formal audit of the RAG pipeline output.
    """
    prompt = f"""
    You are an AI Quality Assurance Engineer. Perform a rigorous evaluation 
    of the system response against the provided context.
    
    Question: {question}
    Context: {context}
    Answer: {answer}
    
    Evaluate the following:
    1. Faithfulness: Is the answer strictly derived from the context?
    2. Relevance: Does the answer directly solve the user's intent?
    
    Format: Faithfulness: X/10, Relevance: X/10, Reasoning: [Concise professional assessment]
    """
    return qa_model.invoke(prompt).content

def run_qa_suite():
    try:
        with open("eval_results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: eval_results.json not found. Run your engine tests first.")
        return
    
    results = []
    for entry in data:
        print(f"Auditing: {entry['question']}...")
        # Map your JSON keys to the perform_audit function parameters
        metrics = perform_audit(
            entry['question'], 
            entry['actual_answer'], 
            entry.get('context', 'No context provided') # Using .get() is safer
        )
        results.append({"question": entry['question'], "metrics": metrics})
    
    with open("qa_audit_report.json", "w") as f:
        json.dump(results, f, indent=4)
    print("QA audit complete. Report generated: qa_audit_report.json")

if __name__ == "__main__":
    run_qa_suite()