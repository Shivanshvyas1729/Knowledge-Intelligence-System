from langchain_community.document_loaders import (
    PyPDFLoader,
    PyMuPDFLoader,
    PDFPlumberLoader,
    UnstructuredPDFLoader,
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


LOADERS = {
    ".pdf": {
        "speed": lambda p: PyMuPDFLoader(p),
        "standard": lambda p: PyPDFLoader(p),
        "tables": lambda p: PDFPlumberLoader(p),
        "layout": lambda p: UnstructuredPDFLoader(
            p,
            strategy="hi_res"
        ),
        
        "ocr": lambda p: UnstructuredPDFLoader(
                         p,
                         strategy="ocr_only"
        ),
    },

    ".docx": {
        "speed": lambda p: Docx2txtLoader(p),
        "structured": lambda p: UnstructuredWordDocumentLoader(
            p,
            mode="elements",
            strategy="fast"
        ),
        "layout": lambda p: UnstructuredWordDocumentLoader(
            p,
            mode="elements",
            strategy="hi_res"
        ),
    },

    ".txt": {
        "default": lambda p: TextLoader(p)
    },

    ".csv": {
        "default": lambda p: CSVLoader(p)
    },

    ".xlsx": {
        "default": lambda p: UnstructuredExcelLoader(p)
    },

    ".pptx": {
        "default": lambda p: UnstructuredPowerPointLoader(p)
    },

    ".html": {
        "default": lambda p: UnstructuredHTMLLoader(p)
    },

    ".md": {
        "default": lambda p: UnstructuredMarkdownLoader(p)
    }
}



def get_loader(file_path: str, priority="default"):
    ext = Path(file_path).suffix.lower()
    logger.debug(f"Requesting loader for: {file_path} with priority: {priority}")

    if ext not in LOADERS:
        logger.error(f"Unsupported extension: {ext} for file: {file_path}")
        raise ValueError(f"Unsupported file type: {ext}")

    options = LOADERS[ext]

    if priority not in options:
        default_priority = list(options.keys())[0]
        logger.warning(
            f"Requested priority '{priority}' not available for extension '{ext}'. "
            f"Falling back to default priority '{default_priority}'"
        )
        priority = default_priority

    logger.info(f"Loaded {ext} using priority '{priority}'")
    return options[priority](file_path)


LOADER_METADATA = {
    ".pdf": {
        "speed": "PyMuPDFLoader (Speed)",
        "standard": "PyPDFLoader (Standard)",
        "tables": "PDFPlumberLoader (Tables)",
        "layout": "UnstructuredPDFLoader (Layout / Hi-Res)",
        "ocr": "UnstructuredPDFLoader (OCR Only)"
    },
    ".docx": {
        "speed": "Docx2txtLoader (Speed)",
        "structured": "UnstructuredWordDocumentLoader (Structured)",
        "layout": "UnstructuredWordDocumentLoader (Layout)"
    },
    ".txt": {
        "default": "TextLoader"
    },
    ".csv": {
        "default": "CSVLoader"
    },
    ".xlsx": {
        "default": "UnstructuredExcelLoader"
    },
    ".pptx": {
        "default": "UnstructuredPowerPointLoader"
    },
    ".html": {
        "default": "UnstructuredHTMLLoader"
    },
    ".md": {
        "default": "UnstructuredMarkdownLoader"
    }
}