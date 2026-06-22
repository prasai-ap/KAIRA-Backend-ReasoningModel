import os
from dotenv import load_dotenv

load_dotenv()

RAG_BOOK_PATH = os.getenv("RAG_BOOK_PATH")
RAG_VECTOR_PATH = os.getenv("RAG_VECTOR_PATH")
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME")

RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K"))

RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL")

RAG_RETRIEVE_K = int(os.getenv("RAG_RETRIEVE_K"))
RAG_RERANK_TOP_K = int(os.getenv("RAG_RERANK_TOP_K"))
RAG_RERANK_MODEL = os.getenv("RAG_RERANK_MODEL")