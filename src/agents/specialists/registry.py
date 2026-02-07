"""Specialist agent registry and domain-specific prompts."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStore

from src.services.llm_utils import get_llm
from src.services.vector_store import search_multiple_namespaces
from src.agents.safety_validation import validate_safety


# Domain-specific system prompts
SPECIALIST_PROMPTS = {
    "plumbing": """You are an expert plumbing specialist. Provide detailed, safe, and practical advice for plumbing repairs.
Focus on: pipes, leaks, faucets, drains, toilets, water heaters, and water-related issues.
Always prioritize safety: mention when to shut off water, when to call a professional, and safety precautions.""",
    
    "electrical": """You are an expert electrical specialist. Provide detailed, safe, and practical advice for electrical repairs.
Focus on: wiring, outlets, switches, circuit breakers, lighting, and electrical systems.
CRITICAL: Always emphasize safety. Mention turning off circuit breakers, when to call a licensed electrician, and electrical hazards.""",
    
    "carpentry": """You are an expert carpentry specialist. Provide detailed, practical advice for woodworking and structural repairs.
Focus on: wood repair, doors, windows, cabinets, framing, flooring, and furniture.
Include: proper tools, techniques, materials, and safety considerations.""",
    
    "hvac": """You are an expert HVAC specialist. Provide detailed, practical advice for heating and cooling systems.
Focus on: air conditioning, heating, furnaces, thermostats, ventilation, and climate control.
Include: maintenance tips, troubleshooting, when to call professionals, and safety considerations.""",
    
    "general": """You are a knowledgeable home repair generalist. Provide helpful advice for general home maintenance and repairs.
Draw from knowledge across all domains. If the issue requires specialized expertise, recommend consulting a professional.""",
}


def get_specialist_response(
    domain: str,
    user_query: str,
    vector_store: VectorStore | None = None,
    image_context: str | None = None,
) -> str:
    """
    Get response from domain specialist using RAG.
    
    Args:
        domain: plumbing, electrical, carpentry, hvac, or general
        user_query: User's question
        vector_store: Vector store for RAG
        image_context: Optional image analysis context
    
    Returns:
        Specialist's response with safety validation
    """
    # Get RAG context
    rag_context = ""
    if vector_store:
        try:
            docs = search_multiple_namespaces(
                query=user_query,
                namespaces=["manuals"],
                k_per_namespace=3,
                filter_domain=domain if domain != "general" else None
            )
            if docs:
                rag_context = "\n\n".join([
                    f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
                    for doc in docs
                ])
        except Exception:
            rag_context = ""
    
    # Build context
    context_parts = []
    if rag_context:
        context_parts.append(f"**Knowledge Base Context:**\n{rag_context}")
    if image_context:
        context_parts.append(f"**Visual Analysis:**\n{image_context}")
    context_parts.append(f"**User Question:**\n{user_query}")
    
    full_context = "\n\n".join(context_parts)
    
    # Get specialist system prompt
    system_prompt = SPECIALIST_PROMPTS.get(domain, SPECIALIST_PROMPTS["general"])
    
    # Add RAG instruction
    system_prompt += """

When knowledge base context is provided, use it to give accurate, specific answers.
If the context doesn't contain relevant information, use your general knowledge but mention this.

Provide your response in this format:
1. **Diagnosis**: What's likely causing the issue
2. **Safety First**: Critical safety precautions
3. **Tools & Materials**: What you'll need
4. **Step-by-Step Instructions**: Clear, numbered steps
5. **When to Call a Pro**: Situations requiring professional help
6. **Additional Tips**: Best practices and preventive measures

Be concise but thorough. Prioritize safety above all else."""
    
    # Get LLM and generate response
    llm = get_llm(temperature=0.7)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=full_context)
    ]
    
    response = llm.invoke(messages)
    answer = response.content
    
    # Safety validation
    safety_check = validate_safety(user_query, answer, domain)
    
    if not safety_check["is_safe"]:
        # Prepend safety warnings
        warnings = "\n".join([f"⚠️ {w}" for w in safety_check["warnings"]])
        answer = f"**SAFETY WARNINGS:**\n{warnings}\n\n{answer}"
    
    return answer