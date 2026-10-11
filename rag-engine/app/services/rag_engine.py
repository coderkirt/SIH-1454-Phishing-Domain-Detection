import os
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import json

class RAGEngine:
    def _classify_text(self, text_snippet):
        prompt = f"""
    Analyze the following research text. Create a single, short, descriptive 
    category tag (e.g., 'Marine Plastic Detection', 'Threat Intelligence').
    Do not use complex sentences. Return ONLY the tag.
    
    Text: {text_snippet[:1000]}
    """
        response = self._invoke_llm_with_retry(prompt)
        return response.content.strip()
    
    def __init__(self, data_dir, db_dir):
        self.data_dir = os.path.abspath(data_dir)
        self.db_dir = os.path.abspath(db_dir)
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = ChatGroq(model_name="qwen/qwen3.8-27b", temperature=0, max_tokens=800)
        self.vector_store = Chroma(persist_directory=self.db_dir, embedding_function=self.embeddings)
        self.bm25_index = None
        self.chunks = []
        # Per-session conversation memory: {session_id: [(question, answer), ...]}
        self.sessions = {}

    def initialize(self):
        import json
        print(f"DEBUG: Scanning directory: {self.data_dir}")
        files = [f for f in os.listdir(self.data_dir) if f.endswith(('.pdf', '.txt'))]
        cache_file = os.path.join(self.data_dir, "category_cache.json")
        
        file_categories = {}
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                file_categories = json.load(f)

        # Check existing data
        data = self.vector_store.get(include=['metadatas', 'documents'])
        
        # Determine if we need to ingest (If DB is empty OR files were added)
        if data['documents'] and not files:
             # Just load what's there
            self.chunks = [Document(page_content=doc, metadata=meta) for doc, meta in zip(data['documents'], data['metadatas'])]
        elif not files:
            # Fresh clone with an empty data directory: nothing in the DB and
            # nothing to ingest. Start with zero chunks instead of crashing on
            # an empty upsert; the first upload will populate everything.
            print("WARNING: No documents found in data directory and database is empty. "
                  "Starting with an empty index - upload a .pdf or .txt to begin.")
            self.chunks = []
        else:
            print("Ingesting or Refreshing documents...")
            raw_docs = []
            for loader_cls, glob in [(TextLoader, "**/*.txt"), (PyPDFLoader, "**/*.pdf")]:
                loader = DirectoryLoader(self.data_dir, glob=glob, loader_cls=loader_cls)
                raw_docs.extend(loader.load())
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            self.chunks = splitter.split_documents(raw_docs)
            
            print("Categorizing and indexing documents...")
            for doc in self.chunks:
                source = os.path.basename(doc.metadata.get('source', 'unknown'))
                
                # If file not in cache, categorize it
                if source not in file_categories:
                    text_sample = doc.page_content[:800]
                    category = self._classify_text(text_sample).strip().replace("'", "").title()
                    file_categories[source] = category
                    print(f"DEBUG: Classified {source} as {category}")
                
                doc.metadata['file_name'] = source
                doc.metadata['category'] = file_categories[source]

            with open(cache_file, 'w') as f:
                json.dump(file_categories, f)

            # CRITICAL: If data exists, clear it to avoid duplicate indices before adding new
            if data['documents']:
                self.vector_store.delete_collection()
                # Re-initialize vector store after deletion
                self.vector_store = Chroma(persist_directory=self.db_dir, embedding_function=self.embeddings)
            
            if self.chunks:
                self.vector_store.add_documents(self.chunks)
                print(f"Indexed {len(self.chunks)} chunks.")
            else:
                print("WARNING: No documents to index (data directory is empty).")

        self._rebuild_indices()

    @staticmethod
    def _rrf_fuse(rankings, k=60):
        """Fuse ranked document lists with Reciprocal Rank Fusion.

        Each document earns sum(1 / (k + rank)) across every list it appears
        in, so a doc ranked high in EITHER dense or BM25 search surfaces.
        Deduplicates by page content.
        """
        scores = {}
        docs_by_key = {}
        for ranking in rankings:
            for rank, doc in enumerate(ranking):
                key = doc.page_content
                docs_by_key[key] = doc
                scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        return [docs_by_key[key] for key in sorted(scores, key=scores.get, reverse=True)]

    def _rebuild_indices(self):
        self.bm25_index = None
        if self.chunks:
            tokenized_corpus = [c.page_content.lower().split() for c in self.chunks]
            self.bm25_index = BM25Okapi(tokenized_corpus)

    # --- Conversation memory ---------------------------------------------

    def _get_history(self, session_id):
        if not session_id or session_id not in self.sessions:
            return []
        return self.sessions[session_id][-5:]

    def _condense_question(self, user_question: str, history) -> str:
        """Rewrite a follow-up question into a standalone search query.

        Example: history contains 'What is YOLOv4?' and the user asks
        'how is it different from v5?' -> the condensed query names YOLOv4,
        so retrieval still works even though the pronoun is unresolved.
        """
        if not history:
            return user_question
        transcript = "\n".join(
            [f"User: {q}\nAssistant: {a[:300]}" for q, a in history]
        )
        prompt = ChatPromptTemplate.from_template(
            """Given the conversation history and a follow-up question, rewrite the
follow-up question so it is fully self-contained. Keep the same language.
Return ONLY the rewritten question, with no extra words.

History:
{history}

Follow-up question: {question}"""
        )
        try:
            response = self._invoke_llm_with_retry(
                prompt.format(history=transcript, question=user_question)
            )
            condensed = response.content.strip()
            return condensed or user_question
        except Exception as e:
            print(f"DEBUG: Question condensation failed, using raw question: {e}")
            return user_question

    def clear_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def _invoke_llm_with_retry(self, prompt_value, attempts=4, base_delay=2.0):
        """Invoke the LLM with exponential backoff.

        Groq intermittently returns 503 (over capacity) or 429 (rate
        limit); retrying with backoff rides through transient failures
        instead of surfacing them to the user.
        """
        last_error = None
        for attempt in range(attempts):
            try:
                return self.llm.invoke(prompt_value)
            except Exception as e:  # noqa: BLE001 - retry any transient API error
                last_error = e
                delay = base_delay * (2 ** attempt)
                print(f"DEBUG: LLM call failed ({e}); retrying in {delay:.0f}s "
                      f"({attempt + 1}/{attempts})")
                time.sleep(delay)
        raise last_error

    def query(self, user_question: str, filter_dict: dict = None, session_id: str = None):
        history = self._get_history(session_id)
        search_query = self._condense_question(user_question, history)

        # 1. Hybrid Search (retrieves against the standalone query)
        search_kwargs = {"k": 8}
        if filter_dict:
            search_kwargs["filter"] = filter_dict
            filter_key = list(filter_dict.keys())[0]
            filter_value = filter_dict[filter_key]
            filtered_chunks = [
                c for c in self.chunks 
                if c.metadata.get(filter_key, "").lower() == filter_value.lower()
            ]
    
            if not filtered_chunks:
                print(f"DEBUG: No chunks matched {filter_dict}")
        
        vector_docs = self.vector_store.similarity_search(search_query, **search_kwargs)
        
        # 2. BM25 Retrieval using self.chunks
        bm25_docs = []
        if self.bm25_index:
            query_tokens = search_query.lower().split()
            if filter_dict:
                # Respect the same metadata filter the vector search used,
                # whatever key it is on (file_name, category, ...).
                filter_key, filter_value = next(iter(filter_dict.items()))
                filtered_chunks = [
                    c for c in self.chunks
                    if str(c.metadata.get(filter_key, "")).lower() == str(filter_value).lower()
                ]
                if not filtered_chunks:
                    print(f"DEBUG: No chunks found for filter {filter_dict}, skipping BM25.")
                else:
                    temp_tokenized = [c.page_content.lower().split() for c in filtered_chunks]
                    temp_bm25 = BM25Okapi(temp_tokenized)
                    bm25_docs = temp_bm25.get_top_n(query_tokens, filtered_chunks, n=8)
            else:
                bm25_docs = self.bm25_index.get_top_n(query_tokens, self.chunks, n=8)

        # 3. Reciprocal Rank Fusion of the dense and BM25 rankings, so a
        # keyword hit that dense search missed can still reach the LLM.
        combined_docs = self._rrf_fuse([vector_docs, bm25_docs])
        
        if not combined_docs:
            return {"answer": "I do not have enough information to answer this question.", "metadata": []}

        # 4. Context Preparation
        combined_context = "\n---\n".join([
            f"Source File: {d.metadata.get('file_name', 'Unknown')}\nContent: {d.page_content}" 
            for d in combined_docs
        ])
        print(f"DEBUG: Retrieved {len(combined_docs)} docs.")
        for i, d in enumerate(combined_docs):
            print(f"DEBUG: Doc {i} Source: {d.metadata.get('file_name')}")
        
        # 5. LLM Prompting (top docs only, sources kept visible for grounding)
        top_docs = combined_docs[:8]
        combined_context = "\n---\n".join(
            [f"Source File: {d.metadata.get('file_name', 'Unknown')}\nContent: {d.page_content}" for d in top_docs]
        )
        prompt = ChatPromptTemplate.from_template(
            """You are a research assistant answering strictly from the provided context.

Question: {question}

Context:
{context}

RULES:
- Answer precisely using ONLY the context above. Cite the source file names you used.
- If answering requires connecting information from multiple source files, synthesize ONE combined answer that uses every relevant file, and cite all of them.
- If the context does not contain the answer, say exactly what information is missing instead of guessing.
- Do not use any outside knowledge."""
        )
        response = self._invoke_llm_with_retry(
            prompt.format(context=combined_context, question=user_question)
        )

        # Remember this exchange for multi-turn follow-ups
        if session_id:
            self.sessions.setdefault(session_id, []).append(
                (user_question, response.content)
            )
            self.sessions[session_id] = self.sessions[session_id][-10:]

        return {
            "answer": response.content,
            "metadata": [d.metadata for d in combined_docs],
            "retrieved_context": [
                {
                    "text": d.page_content,
                    "source": d.metadata.get("file_name", "Unknown"),
                    "category": d.metadata.get("category", "Uncategorized"),
                }
                for d in top_docs
            ],
            "standalone_query": search_query,
        }