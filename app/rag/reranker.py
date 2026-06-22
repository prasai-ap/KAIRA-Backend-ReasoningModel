from sentence_transformers import CrossEncoder

from app.rag.config import RAG_RERANK_MODEL, RAG_RERANK_TOP_K

_reranker = None


def get_reranker():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(RAG_RERANK_MODEL)

    return _reranker


def rerank_documents(query: str, docs):
    if not docs:
        return []

    reranker = get_reranker()

    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(docs, scores),
        key=lambda item: item[1],
        reverse=True,
    )

    return [doc for doc, score in ranked[:RAG_RERANK_TOP_K]]