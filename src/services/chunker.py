"""Semantic chunking with overlap."""

import tiktoken

from src.services.document_loader import DocumentChunk


# ~4 chars per token for English; 512 tokens ≈ 2000 chars
CHUNK_SIZE = 512
OVERLAP = 50


def _get_encoding():
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return tiktoken.get_encoding("gpt2")


def chunk_document(doc: DocumentChunk, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[DocumentChunk]:
    """Split document content into overlapping chunks by token count."""
    enc = _get_encoding()
    tokens = enc.encode(doc.content)
    chunks: list[DocumentChunk] = []

    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        text = enc.decode(chunk_tokens)

        chunks.append(
            DocumentChunk(
                content=text,
                source=doc.source,
                source_type=doc.source_type,
                domain=doc.domain,
                page=doc.page,
                section=doc.section,
            )
        )

        if end >= len(tokens):
            break
        start = end - overlap

    return chunks


def chunk_documents(docs: list[DocumentChunk], chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[DocumentChunk]:
    """Chunk a list of documents."""
    result: list[DocumentChunk] = []
    for doc in docs:
        result.extend(chunk_document(doc, chunk_size=chunk_size, overlap=overlap))
    return result
