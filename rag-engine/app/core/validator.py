import json
import logging
import time
from typing import Dict, Any
from openai import OpenAI

class LLMValidator:
    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1", model: str = "llama3-70b-8192"):
        # This works for Groq or any OpenAI-compatible API
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.logger = logging.getLogger(__name__)

    def evaluate(self, question: str, expected: str, actual: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a strict evaluator. Assess the 'actual' answer against the 'expected' "
            "answer. Output ONLY a valid JSON object with keys: 'score' (int 0-10) and 'rationale' (str)."
        )
        
        try:
            response = None
            for attempt in range(3):  # ride out transient Groq 429/503s
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Q: {question}\nExpected: {expected}\nActual: {actual}"}
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=500  # stay under Groq on-demand OTPM limit (1000/min)
                    )
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"LLM validation error: {e}")
            return {"score": 0, "rationale": f"Validation failed: {str(e)}"}