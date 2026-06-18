from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from app.rag.config import (
    RAG_BOOK_PATH,
    RAG_VECTOR_PATH,
    RAG_COLLECTION_NAME,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    RAG_EMBEDDING_MODEL,
)


def ingest_phaladeepika():
    loader = PyPDFLoader(RAG_BOOK_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=RAG_EMBEDDING_MODEL,
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=RAG_VECTOR_PATH,
        collection_name=RAG_COLLECTION_NAME,
    )

    return {
        "message": "Phaladeepika ingestion completed",
        "chunks": len(chunks),
    }


if __name__ == "__main__":
    print(ingest_phaladeepika())