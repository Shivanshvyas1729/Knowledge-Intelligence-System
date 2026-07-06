import shutil
from tempfile import tempdir
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader, UnstructuredWordDocumentLoader
from regex import E
from unstructured.partition.docx import partition_docx

from models.vector_store import VectorStore
from services.llm_service import LLMService
from services.storage_service import SupabaseStorage
from config import Config
import os 
from utils.file_loader import get_loader
from flask import Flask ,request, render_template,jsonify
import logging
from utils.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__)

vector_store = VectorStore(Config.VECTOR_DB_PATH)
storage_service = SupabaseStorage()
llm_service = LLMService(vector_store)

@app.route("/")
def index():
    logger.info("Index page accessed.")
    return render_template('index.html')



def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Replace surrogate characters that UTF-8 cannot encode
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


def process_document(file, priority="default"):
    """Process document based on file type and return text chunks"""

    tempdir = tempfile.mkdtemp()
    temp_path = os.path.join(tempdir, file.filename)

    try:

        file.save(temp_path)

        loader = get_loader(temp_path, priority)

        documents = loader.load()
        sanitized_documents = [sanitize_document(doc) for doc in documents]

        return sanitized_documents

    finally:
        
        shutil.rmtree(tempdir, ignore_errors=True)



@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        logger.debug("Upload endpoint called")

        if "file" not in request.files:
            logger.warning("No file in request")
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            logger.warning("Empty filename")
            return jsonify({"error": "No file selected"}), 400

        allowed_extensions = (
            ".pdf",
            ".docx",
            ".txt",
            ".csv",
            ".xlsx",
            ".pptx",
            ".html",
            ".md",
        )

        if not file.filename.lower().endswith(allowed_extensions):
            logger.warning("Unsupported file type")
            return jsonify({"error": "Unsupported file type"}), 400
        
        priority = request.form.get("priority", "default")
        logger.debug(f"Processing file: {file.filename} with priority: {priority}")

        try:
            text_chunks = process_document(file, priority)
            logger.debug(f"Documents processed into {len(text_chunks)} chunks")

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500
        
        # upload to S3 
        try:
            file.seek(0)
            storage_service.uploadfile(file,file.filename)
            logger.debug(f"File uploaded to storage service")

        except Exception as e:
            logger.error(f"Error while uploading the file to Storage service aws/s3 or supabase bucket: {str(e)}", exc_info=True)
            return jsonify({"error": f"Error while uploading the file: {str(e)}"}), 500
        

        # add to vector store

        try:
            vector_store.add_documents(text_chunks)
            logger.debug("Document added to vector store")

        except Exception as e:
            logger.error(f"Error adding to vector store: {str(e)}")
            return jsonify({"error":f"Error adding to vector store:{str(e)}"}) , 500
        
        return jsonify({
            'message': 'File uploaded and processed successfully',
            'chunks_processed': len(text_chunks)
        })

    except Exception as e:
        logger.error(f"Unexpected error (check main file upload section): {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/query', methods=['POST'])
def query():
    logger.info("Query endpoint called.")
    data = request.json
    if not data or "question" not in data:
        logger.warning("No question provided in request data.")
        return jsonify({"error": "No question provided"}), 400
    
    question = data['question']
    model_name = data.get('model', 'gpt-4.1-nano')
    logger.debug(f"User question: '{question}' using model: '{model_name}'")
    
    try:
        response = llm_service.get_response(question, model_name)
        logger.info("Successfully generated query response.")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error handling query: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

@app.route('/loaders', methods=['GET'])
def get_loaders_metadata():
    logger.info("Loaders metadata endpoint called.")
    from utils.file_loader import LOADER_METADATA
    return jsonify(LOADER_METADATA)


@app.route('/files', methods=['GET'])
def list_uploaded_files():
    logger.info("List uploaded files endpoint called.")
    try:
        filenames = storage_service.list_files()
        return jsonify(filenames)
    except Exception as e:
        logger.error(f"Error listing uploaded files: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/clear', methods=['POST'])
def clear_chat():
    logger.info("Clear chat history endpoint called.")
    try:
        llm_service.clear_history()
        logger.info("Chat history cleared successfully.")
        return jsonify({"message": "Conversation history cleared successfully"})
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    logger.info("Starting Flask application on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)