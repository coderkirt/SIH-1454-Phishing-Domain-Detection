import json
import os
from datetime import datetime

class ResultLogger:
    def __init__(self, log_file="qa_audit_report.json"):
        self.log_file = log_file
        # Get the directory part
        directory = os.path.dirname(self.log_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def log(self, question, expected, actual, passed, metadata):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "sources": metadata
        }
        
        # Load existing, append, and save
        data = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        data.append(entry)
        
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=4)