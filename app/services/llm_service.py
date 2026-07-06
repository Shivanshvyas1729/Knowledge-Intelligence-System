# LLM Initialization
from langchain_openai import ChatOpenAI 

# Prompts & Message Structure
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Output Parsers & Runnables (LCEL)
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.runnables import RunnablePassthrough , RunnableParallel 

# Chains & Retrievers (Built-in)
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self,vector_store):
        logger.info("Initializing LLMService.")
        self.llm = ChatOpenAI(
            temperature=.7,
            model = "gpt-4.1-nano",
            api_key=Config.EURI_API_KEY,
            base_url="https://api.euron.one/api/v1/euri"
        )

        retriever = vector_store.as_retriever()

        # Prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question that can be understood "
            "without the chat history. "
            "Do NOT answer the question, only rewrite it if necessary."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ])

        history_aware_retriever = create_history_aware_retriever(
            self.llm,
            retriever,
            contextualize_q_prompt
        )

        qa_system_prompt = (
            "You are a helpful AI assistant.\n\n"
            "Use the following retrieved context to answer the user's question.\n"
            "If you don't know the answer, simply say you don't know.\n\n"
            "Context:\n{context}"
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system",qa_system_prompt),
            MessagesPlaceholder('chat_history'),
            ("human","{input}"),
        ])

        qa_chain = create_stuff_documents_chain(self.llm,qa_prompt)
        self.chain = create_retrieval_chain(history_aware_retriever,qa_chain)

        self.chat_history =[]

    def get_response(self,query, model_name="gpt-4.1-nano"):
        logger.info(f"Generating LLM response for query: '{query}' using model: '{model_name}'")
        try:
            self.llm.model_name = model_name
            response = self.chain.invoke({
                "input":query,
                "chat_history": self.chat_history,
            })
            answer = response.get("answer", "")
            logger.debug(f"Generated LLM answer: {answer}")
            
            # Store conversation history
            self.chat_history.append(HumanMessage(content=query))
            self.chat_history.append(AIMessage(content=answer))
            
            return answer
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}", exc_info=True)
            return "I encountered an error processing your request."
        
    def clear_history(self):
        """start a fresh conversation"""
        logger.info("Clearing chat history.")
        self.chat_history = []





































#older method 


# from langchain.chat_models import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from config import Config

# class LLMService:
#     def __init__(self, vector_store):
#         self.llm = ChatOpenAI(
#             temperature=0.7,
#             model_name="gpt-3.5-turbo",
#             openai_api_key=Config.OPENAI_API_KEY
#         )
#         self.memory = ConversationBufferMemory(
#             memory_key="chat_history",
#             return_messages=True
#         )
#         self.chain = ConversationalRetrievalChain.from_llm(
#             llm=self.llm,
#             retriever=vector_store.vectore_store.as_retriever(),
#             memory=self.memory
#         )

#     def get_response(self, query):
#         try:
#             response = self.chain({"question": query})
#             return response['answer']
#         except Exception as e:
#             print(f"Error getting LLM response: {e}")
#             return "I encountered an error processing your request."