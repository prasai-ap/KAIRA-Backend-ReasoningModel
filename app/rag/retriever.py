from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.rag.config import (
    RAG_VECTOR_PATH,
    RAG_COLLECTION_NAME,
    RAG_TOP_K,
    RAG_EMBEDDING_MODEL,
)


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=RAG_EMBEDDING_MODEL,
    )

    return Chroma(
        persist_directory=RAG_VECTOR_PATH,
        collection_name=RAG_COLLECTION_NAME,
        embedding_function=embeddings,
    )


def retrieve_phaladeepika_context(query: str) -> str:
    vectorstore = get_vectorstore()

    docs = vectorstore.similarity_search(
        query,
        k=RAG_TOP_K,
    )

    if not docs:
        return "No relevant Phaladeepika context found."

    parts = []

    for index, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page", "unknown")
        parts.append(
            f"[Reference {index} | Phaladeepika | Page {page}]\n{doc.page_content}"
        )

    return "\n\n".join(parts)