import streamlit as st
import requests
import json
import os

# Set up page configurations
st.set_page_config(page_title="RAG AI Assistant", page_icon="🤖", layout="centered")

# Configure backend URLs
BASE_API_URL = "http://127.0.0.1:8000"
QUERY_URL = f"{BASE_API_URL}/query"
UPLOAD_URL = f"{BASE_API_URL}/api/upload"
CLEAR_URL = f"{BASE_API_URL}/api/clear-history"
RESET_URL = f"{BASE_API_URL}/api/reset-database"

# Initialize persistent tracking for uploaded files in session state
if "uploaded_tracker" not in st.session_state:
    st.session_state.uploaded_tracker = []

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.title("🎛️ Control Panel")
    st.write("Manage documents and system context.")
    
    # 1. Drag-and-Drop File Uploader
    uploaded_file = st.file_uploader("Upload new documents (.pdf, .txt)", type=["pdf", "txt"])
    
    # Only upload if the file exists and hasn't been processed in this state yet
    if uploaded_file is not None and uploaded_file.name not in st.session_state.uploaded_tracker:
        with st.spinner(f"Uploading and processing {uploaded_file.name}..."):
            try:
                # Prepare file payload for Multipart Form Upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                upload_response = requests.post(UPLOAD_URL, files=files, timeout=300)
                
                if upload_response.status_code == 200:
                    st.success(f"{uploaded_file.name} successfully indexed!")
                    # Log the file name so it never re-uploads on chat inputs
                    st.session_state.uploaded_tracker.append(uploaded_file.name)
                    st.rerun()
                else:
                    st.error("Backend processing error encountered.")
            except requests.exceptions.ConnectionError:
                st.error("Backend server is offline.")

    # 2. Visually Display All Uploaded Files Currently Active
    if st.session_state.uploaded_tracker:
        st.markdown("### 📁 Active System Documents")
        for doc_name in st.session_state.uploaded_tracker:
            st.caption(f"✅ {doc_name}")

    st.markdown("---")
    
    # 3. Clear Chat History Button
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        try:
            requests.post(CLEAR_URL, json={"session_id": "streamlit_user_session"}, timeout=5)
            st.success("History wiped!")
        except requests.exceptions.ConnectionError:
            st.error("Could not reach backend to wipe memory.")
        st.rerun()

    # 4. Hard Reset Vector Database Button
    if st.button("Hard Reset Database", use_container_width=True):
        with st.spinner("Wiping database and re-indexing data folder..."):
            try:
                reset_response = requests.post(RESET_URL, timeout=45)
                if reset_response.status_code == 200:
                    st.success("Database rebuilt fresh!")
                    st.session_state.messages = []  # Clear current chat logs from view
                    st.session_state.uploaded_tracker = []  # Clear tracker view
                    st.rerun()
                else:
                    st.error("Failed to reset database.")
            except requests.exceptions.ConnectionError:
                st.error("Backend server is offline.")

st.title("🤖 Secure RAG Pipeline Chat")
st.caption("Ask questions about your company policy or practice documents in real-time.")

# Initialize session state message log
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant" and "diagnostics" in message:
            diag = message["diagnostics"]
            with st.expander("⚙️ System Diagnostics (Behind the Scenes)"):
                st.info(f"**Contextualized Search Query:** *\"{diag['standalone_q']}\"*")
                if diag["context"]:
                    st.write("**Retrieved Document Context Chunks:**")
                    for idx, chunk in enumerate(diag["context"]):
                        chunk_text = chunk.get("text", "No context text found.")
                        chunk_source = chunk.get("source", "Unknown Source")
                        with st.expander(f"📄 Chunk {idx+1}: Found in {chunk_source}"):
                            st.write(chunk_text)

# Accept user input
if user_question := st.chat_input("What would you like to know?"):
    
    # Render user message immediately
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Render assistant response block
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            payload = {
                "question": user_question,
                "session_id": "streamlit_user_session"
            }
            
            # Request connection to the backend
            response = requests.post(QUERY_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer field found.")
                context = data.get("retrieved_context", [])
                standalone_q = data.get("standalone_query", user_question)
                
                # Helper generator function to simulate smooth token-by-token text generation
                def token_streamer():
                    for word in answer.split(" "):
                        yield word + " "
                        import time
                        time.sleep(0.04)
                
                full_streamed_text = response_placeholder.write_stream(token_streamer())
                
                # Live System Diagnostics Panel rendered right after the stream concludes
                with st.expander("⚙️ System Diagnostics (Behind the Scenes)"):
                    st.info(f"**Contextualized Search Query:** *\"{standalone_q}\"*")
                    if context:
                        st.write("**Retrieved Document Context Chunks:**")
                        for idx, chunk in enumerate(context):
                            chunk_text = chunk.get("text", "No context text found.")
                            chunk_source = chunk.get("source", "Unknown Source File")
                            
                            with st.expander(f"📄 Chunk {idx+1}: Found in {chunk_source}"):
                                st.write(chunk_text)
                
                # Append everything into the message object so it remains persistent
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "diagnostics": {
                        "standalone_q": standalone_q,
                        "context": context
                    }
                })
            else:
                response_placeholder.error(f"Backend Error ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            response_placeholder.error("Could not connect to the FastAPI backend.")