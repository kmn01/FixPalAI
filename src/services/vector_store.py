"""Vector store abstraction: Chroma (dev) and Pinecone (prod)."""

import os
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from src.services.document_loader import DocumentChunk


def _doc_chunk_to_langchain(chunk: DocumentChunk) -> Document:
    """Convert DocumentChunk to LangChain Document."""
    metadata: dict[str, Any] = {
        "source": chunk.source,
        "source_type": chunk.source_type,
    }
    if chunk.domain:
        metadata["domain"] = chunk.domain
    if chunk.page is not None:
        metadata["page"] = chunk.page
    if chunk.section:
        metadata["section"] = chunk.section
    return Document(page_content=chunk.content, metadata=metadata)


def get_vector_store(
    collection_name: str = "fixpalai",
    namespace: str | None = None,
) -> tuple[VectorStore, str]:
    """
    Return (vector_store, namespace) based on VECTOR_DB env var.
    Uses Chroma for local dev (VECTOR_DB=chroma or unset), Pinecone for prod.
    """
    db_type = os.getenv("VECTOR_DB", "chroma").lower()
    embeddings = __import__("src.services.embeddings", fromlist=["get_embeddings_model"]).get_embeddings_model()

    ns = namespace or "manuals"

    if db_type == "pinecone":
        from langchain_pinecone import PineconeVectorStore

        index_name = os.getenv("PINECONE_INDEX_NAME", "fixpalai")
        vs = PineconeVectorStore.from_existing_index(index_name, embeddings, namespace=ns)
        return vs, ns

    # Default: Chroma
    import chromadb
    from langchain_chroma import Chroma

    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    vs = Chroma(
        client=chroma_client,
        collection_name=f"{collection_name}_{ns}".replace("-", "_"),
        embedding_function=embeddings,
    )
    return vs, ns


def add_chunks_to_store(
    vector_store: VectorStore,
    chunks: list[DocumentChunk],
) -> None:
    """Add document chunks to the vector store."""
    docs = [_doc_chunk_to_langchain(c) for c in chunks]
    vector_store.add_documents(docs)


def search_vector_store(
    vector_store: VectorStore,
    query: str,
    k: int = 5,
    filter_domain: str | None = None,
) -> list[Document]:
    """Search the vector store. Optionally filter by domain."""
    # Chroma/Pinecone accept where for metadata filter
    filter_dict: dict[str, Any] | None = None
    if filter_domain:
        filter_dict = {"domain": filter_domain}

    # LangChain's similarity_search accepts filter
    return vector_store.similarity_search(query, k=k, filter=filter_dict)


def search_multiple_namespaces(
    query: str,
    namespaces: list[str] = ("manuals",),
    k_per_namespace: int = 3,
    filter_domain: str | None = None,
) -> list[Document]:
    """Search multiple namespaces and merge results (deduplicated by content)."""
    seen: set[str] = set()
    merged: list[Document] = []
    for ns in namespaces:
        vs, _ = get_vector_store(namespace=ns)
        docs = search_vector_store(vs, query, k=k_per_namespace, filter_domain=filter_domain)
        for doc in docs:
            key = doc.page_content[:200]
            if key not in seen:
                seen.add(key)
                merged.append(doc)
    return merged[: k_per_namespace * len(namespaces)]
