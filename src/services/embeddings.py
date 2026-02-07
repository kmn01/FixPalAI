"""Embedding generation using HuggingFace or Google Gemini."""

import os
from langchain_core.embeddings import Embeddings


def get_embeddings_model() -> Embeddings:
    """Return embeddings model based on configuration."""
    
    # Check if using Google embeddings
    if os.getenv("EMBEDDING_MODEL", "").startswith("models/"):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        )
    
    # HuggingFace embeddings
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )