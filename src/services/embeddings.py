"""Embedding generation using Google Gemini (default when GOOGLE_API_KEY set, fast) or HuggingFace.
Set EMBEDDING_MODEL=google or leave unset for fast startup; use sentence-transformers only if needed."""

import os
from langchain_core.embeddings import Embeddings


def get_embeddings_model() -> Embeddings:
    """Return embeddings model. Defaults to Google when GOOGLE_API_KEY is set (fast startup)."""
    env = os.getenv("EMBEDDING_MODEL", "").strip().lower()

    # Explicit Google: "models/..." or "google"
    if env.startswith("models/") or env == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004").strip()
        if not model.startswith("models/"):
            model = "models/text-embedding-004"
        return GoogleGenerativeAIEmbeddings(model=model)

    # Explicit HuggingFace / sentence-transformers (loads local model, slower startup)
    if env in ("huggingface", "sentence-transformers", "hf"):
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name=os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )

    # Default: use Google when API key is set (no local model, fast startup)
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # Fallback: HuggingFace (set HF_TOKEN in .env for higher rate limits and faster downloads)
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )