from langchain_community.document_loaders import PyPDFLoader
import os

# Adjust this path if your file name is slightly different
file_path = os.path.join("app", "data", "SANS-Bridging-Gap-Between-Threat-Intelligence-Business-Risk_Garvey.pdf")

print(f"DEBUG: Looking for file at: {file_path}")

try:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(f"DEBUG: Successfully loaded {len(docs)} pages.")
    print(f"--- PREVIEW OF PAGE 1 ---")
    print(docs[0].page_content[:1000]) # Prints the first 1000 characters
except Exception as e:
    print(f"DEBUG: Error loading file: {e}")