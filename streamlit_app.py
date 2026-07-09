import sys
import os
import shutil
import tempfile
import streamlit as st

# Ensure Vercel / local runtime can resolve relative imports from the app directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from config import Config
from models.vector_store import VectorStore
from services.llm_service import LLMService
from services.storage_service import SupabaseStorage
from utils.file_loader import get_loader

# ==========================================
# 1. Page Configuration & Aesthetic Styles
# ==========================================
st.set_page_config(
    page_title="Knowledge Intelligence System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic Dark-Mode Styles
st.markdown(
    """
    <style>
    /* Dark Theme Base & Font overrides */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Layout */
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #151927 100%);
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(21, 25, 39, 0.85) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
    }
    
    /* Title Header and Banner */
    .banner-container {
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .banner-icon {
        font-size: 3rem;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .banner-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    /* Custom buttons and forms style */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #0f111a !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4);
        color: #0f111a !important;
    }
    
    /* Custom secondary buttons */
    .sidebar-clear-btn .stButton > button {
        background: rgba(239, 68, 68, 0.2) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        box-shadow: none !important;
    }
    .sidebar-clear-btn .stButton > button:hover {
        background: rgba(239, 68, 68, 0.4) !important;
        color: #ffffff !important;
        border-color: rgba(239, 68, 68, 0.6) !important;
    }
    
    /* File list style */
    .file-card {
        padding: 0.5rem 0.8rem;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. Components Initialization
# ==========================================
@st.cache_resource
def get_vector_store():
    return VectorStore(Config.VECTOR_DB_PATH)

@st.cache_resource
def get_storage_service():
    return SupabaseStorage()

vector_store = get_vector_store()
storage_service = get_storage_service()

# Store LLMService inside session state to isolate chat history per user
if "llm_service" not in st.session_state:
    st.session_state.llm_service = LLMService(vector_store)
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 3. Document Processing Functions
# ==========================================
def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    return text.encode('utf-8', errors='replace').decode('utf-8')

def sanitize_document(doc):
    if hasattr(doc, 'page_content') and doc.page_content:
        doc.page_content = sanitize_text(doc.page_content)
    if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
        new_metadata = {}
        for k, v in doc.metadata.items():
            if isinstance(v, str):
                new_metadata[k] = sanitize_text(v)
            elif isinstance(v, list):
                new_metadata[k] = [sanitize_text(x) if isinstance(x, str) else x for x in v]
            elif isinstance(v, dict):
                new_metadata[k] = {dict_k: (sanitize_text(dict_v) if isinstance(dict_v, str) else dict_v) for dict_k, dict_v in v.items()}
            else:
                new_metadata[k] = v
        doc.metadata = new_metadata
    return doc

def process_streamlit_file(uploaded_file, priority="default"):
    """Saves the streamlit file object to a temp path, loads and processes it."""
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    try:
        # Save file locally to temp path
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Parse document
        loader = get_loader(temp_path, priority)
        documents = loader.load()
        sanitized_documents = [sanitize_document(doc) for doc in documents]
        return sanitized_documents
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# ==========================================
# 4. Main Page Layout
# ==========================================

# Styled Banner Title
st.markdown(
    """
    <div class="banner-container">
        <div class="banner-icon">🧠</div>
        <div>
            <h1 class="banner-title">Knowledge Intelligence System</h1>
            <p style="margin:0; color:#818cf8; font-size:0.95rem;">Retrieval-Augmented Generation (RAG) Workspace</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 5. Sidebar - Settings & File Ingestion
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Document Ingestion")
    
    uploaded_files = st.file_uploader(
        "Upload files to vectorize & store",
        type=["pdf", "docx", "txt", "csv", "xlsx", "pptx", "html", "md"],
        accept_multiple_files=True
    )
    
    priority = st.selectbox(
        "Extraction Priority",
        ["default", "speed", "standard", "tables", "structured", "layout", "ocr"],
        index=0,
        help="Select parser behavior. Speed is fast; Layout uses advanced vision parsers; OCR forces text scanning."
    )
    
    # Ingestion button
    if st.button("Process & Index Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one document first.")
        else:
            total_chunks = 0
            for uploaded_file in uploaded_files:
                with st.spinner(f"Ingesting {uploaded_file.name}..."):
                    try:
                        # 1. Process document and split
                        text_chunks = process_streamlit_file(uploaded_file, priority)
                        
                        # 2. Upload to Supabase storage
                        uploaded_file.seek(0)
                        storage_service.uploadfile(uploaded_file, uploaded_file.name)
                        
                        # 3. Save to vector DB
                        vector_store.add_documents(text_chunks)
                        total_chunks += len(text_chunks)
                        st.success(f"Successfully processed {uploaded_file.name}!")
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            if total_chunks > 0:
                st.balloons()
                st.success(f"All documents indexed! Added {total_chunks} text chunks to Vector DB.")
                
    st.markdown("---")
    st.markdown("### ⚙️ Model Config")
    model_name = st.selectbox(
        "LLM Model Engine",
        ["gpt-4.1-nano", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📂 Uploaded Library")
    
    # List files from Supabase
    try:
        cloud_files = storage_service.list_files()
        if cloud_files:
            for file_name in cloud_files:
                st.markdown(
                    f"""
                    <div class="file-card">
                        <span>📄</span>
                        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;">{file_name}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.info("No files stored in cloud repository yet.")
    except Exception as e:
        st.caption(f"Could not load library: {str(e)}")
        
    st.markdown("---")
    
    # Clean workspace button
    st.markdown('<div class="sidebar-clear-btn">', unsafe_allow_html=True)
    if st.button("Clear Chat History", key="clear_chat"):
        st.session_state.llm_service.clear_history()
        st.session_state.chat_messages = []
        st.success("Conversation history cleared!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. Chat Assistant Interface
# ==========================================

# Display active chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask a question about your uploaded documents..."):
    # Render user prompt
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Get assistant answer
    with st.chat_message("assistant"):
        with st.spinner("Analyzing knowledge base..."):
            try:
                # Call LLM Service
                response = st.session_state.llm_service.get_response(prompt, model_name)
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
