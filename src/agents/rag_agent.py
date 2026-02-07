"""RAG (Retrieval-Augmented Generation) agent."""

from langchain_core.vectorstores import VectorStore
from langchain_core.messages import SystemMessage, HumanMessage

from src.services.llm_utils import get_llm
from src.services.vector_store import search_multiple_namespaces


def rag_query(
    query: str,
    vector_store: VectorStore,
    domain: str | None = None,
    k: int = 5,
) -> str:
    """
    Perform RAG query: retrieve relevant docs and generate answer.
    
    Args:
        query: User question
        vector_store: Vector store to search
        domain: Optional domain filter
        k: Number of documents to retrieve
    
    Returns:
        Generated answer based on retrieved context
    """
    
    # Retrieve relevant documents
    docs = search_multiple_namespaces(
        query=query,
        namespaces=["manuals"],
        k_per_namespace=k // 2,
        filter_domain=domain
    )
    
    if not docs:
        return "I couldn't find relevant information in the knowledge base. Please upload manuals or ask a more specific question."
    
    # Build context from retrieved docs
    context = "\n\n".join([
        f"**Source: {doc.metadata.get('source', 'Unknown')}**\n{doc.page_content}"
        for doc in docs
    ])
    
    # Generate answer using LLM
    system_prompt = """You are a helpful home repair assistant. The user is a technician who is on ground, fixing home repair problems such as plumbing, electrical, carpentry, hvac, etc.
Use the provided context from manuals and guides to answer the user's question accurately.
If the context doesn't contain enough information, say so and provide general guidance.
Always cite your sources when possible. Keep the answer concise and to the point."""

    user_prompt = f"""Context from knowledge base: {context}\n\nUser Question: {query}
    Please provide a helpful answer based on the context above."""
    
    llm = get_llm(temperature=0.7)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content