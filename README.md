# Knowledge Intelligence System

A modern, high-performance **Retrieval-Augmented Generation (RAG)** application designed to ingest documents of various formats and let users converse with their contents using a Chat Assistant. The system features a responsive, dark-mode glassmorphic front-end interface, Supabase storage syncing, Chroma vector storage indexing, and LangChain orchestration.

---

## Key Features

- **Multi-Format Ingestion**: Supports `.pdf`, `.docx`, `.txt`, `.csv`, `.xlsx`, `.pptx`, `.html`, and `.md` formats.
- **Intelligent Parsers**: Dynamically assigns document loaders depending on file type and extraction priority.
- **Vector DB Storage**: Indexes text chunks into Chroma vector store for semantic similarity searching.
- **Supabase Cloud Syncing**: Automatically uploads ingested documents to Supabase storage.
- **History-Aware RAG Assistant**: Re-contextualizes user queries based on chat history to formulate clean retrieval queries before producing answers.
- **Glassmorphic UI**: Premium web interface styled with custom fonts, border glows, smooth animations, and interactive drag-and-drop file ingestion.
- **Structured Logging**: Deep logging configuration that captures initialization events, backend service activity, retrieval performance metrics, and error stacktraces.

---

## Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (Fetch APIs, event handlers)
- **Backend API**: Flask
- **Orchestration**: LangChain, `langchain_classic` (Chains and history-aware retrievers)
- **Vector Database**: Chroma DB (`langchain_chroma`)
- **Cloud Storage**: Supabase Storage Client
- **LLM Engine**: ChatOpenAI wrapper utilizing Euron API

---

## Directory Structure

```text
Knowledge-Intelligence-System/
├── app/
│   ├── models/
│   │   └── vector_store.py      # Chroma vector DB operations
│   ├── services/
│   │   ├── llm_service.py       # LangChain retrieval-chain setup
│   │   └── storage_service.py   # Supabase Storage client integrations
│   ├── static/
│   │   └── style.css            # Dark-mode glassmorphic CSS
│   ├── templates/
│   │   └── index.html           # Ingestion & Chat Interface HTML + JS
│   ├── utils/
│   │   ├── file_loader.py       # Ingest loaders mapper
│   │   └── logger.py            # Console & RotatingFileHandler setup
│   ├── config.py                # Environment configurations
│   └── main.py                  # Flask entrypoint & APIs
├── logs/
│   └── app.log                  # Generated application log file
├── .env                         # Secrets configuration (ignored by Git)
├── requirements.txt             # Project Python requirements
└── README.md                    # Project documentation
```

---

## Installation & Setup

### 1. Configure the Conda Environment
Create and activate your Conda environment. This ensures dependencies are isolated to the system:
```bash
conda create -n llmapp python=3.11 -y
conda activate llmapp
```

### 2. Install Project Dependencies
Run pip within your activated conda environment:
```bash
pip install -r requirements.txt
pip install python-docx
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory of the project with the following keys:
```env
SUPABASE_URL = "your_supabase_url"
SUPABASE_ANON_KEY = "your_supabase_anon_key"
SUPABASE_SERVICE_ROLE_KEY = "your_supabase_service_role_key"
SUPABASE_BUCKET_NAME = "your_bucket_name"
EURI_API_KEY = "your_euron_api_key"
VECTOR_DB_PATH = "vector_db"
```

---

## Running the Application

To run the Flask application inside your conda environment `llmapp`, execute the following command:

**Option A (Using the absolute path of your Conda installation if `conda` is not globally registered):**
```powershell
C:\Users\DELL\miniconda3\condabin\conda.bat run -n llmapp python app/main.py
```

**Option B (If you are running in a terminal that already recognizes `conda`):**
```powershell
conda run -n llmapp python app/main.py
```

Once running, access the user interface at:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## Logging Details

Logs are captured simultaneously to the console and to a local rotating file handler:
- **Log Location**: `logs/app.log`
- **Configuration**:
  - **Console**: Captures `INFO` and `ERROR` events.
  - **File Rotating Handler**: Logs messages with a max size of 10MB per file and preserves up to 5 back-ups.
  - **Log Format**: `[Timestamp] | [Level] | [Logger Name] | [Filename:Line] | [Message]`