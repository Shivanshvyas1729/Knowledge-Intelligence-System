from re import search

from langchain_chroma import Chroma
import os 
from langchain_core import retrievers
from langchain_openai import OpenAIEmbeddings
from openai import embeddings
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)



class VectorStore:
    def __init__(self,
                 persist_directory:str,
                 collection_name:str = "rag_collection",
                 ):
        logger.info(f"Initializing VectorStore in directory: {persist_directory} with collection: {collection_name}")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=Config.EURI_API_KEY,
            base_url="https://api.euron.one/api/v1/euri",
        )
        self.vector_store = Chroma(
            persist_directory= persist_directory, 
            embedding_function = self.embeddings,
            collection_name=collection_name
        )

    def add_documents(self,documents):
        logger.info(f"Adding {len(documents)} documents to vector store.")
        self.vector_store.add_documents(documents)
        logger.debug("Successfully added documents to vector store.")

    def similarity_search(self,query:str,k:int = 4):
        logger.debug(f"Performing similarity search for query: '{query}' with k={k}")
        results = self.vector_store.similarity_search(
            query=query,
            k=k
        )
        logger.info(f"Similarity search returned {len(results)} results.")
        return results
    
    def as_retriever(self,k:int = 8):
        logger.debug(f"Creating retriever wrapper with k={k}")
        retriever = self.vector_store.as_retriever(
                    search_kwargs ={"k":k}
                )

        return retriever