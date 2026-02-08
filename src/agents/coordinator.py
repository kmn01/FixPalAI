"""Coordinator agent - routes queries to specialist agents."""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import VectorStore

from src.services.llm_utils import invoke_llm
from src.agents.specialists.registry import get_specialist_response


def coordinator_invoke(
    user_query: str,
    vector_store: VectorStore | None = None,
    image_context: str | None = None,
) -> tuple[str, str]:
    """
    Coordinate the query: classify domain, route to specialist.
    
    Returns:
        (answer, domain)
    """
    # Build context
    context_parts = [f"User query: {user_query}"]
    if image_context:
        context_parts.append(f"Image analysis: {image_context}")
    
    full_context = "\n".join(context_parts)
    
    # Step 1: Classify domain
    domain = _classify_domain(full_context)
    
    # Step 2: Route to specialist
    answer = get_specialist_response(
        domain=domain,
        user_query=user_query,
        vector_store=vector_store,
        image_context=image_context,
    )
    
    return answer, domain


def _classify_domain(query: str) -> str:
    """Classify the query into a domain: plumbing, electrical, carpentry, hvac, or general."""
    
    system_prompt = """You are a domain classifier for home repair queries.
Analyze the query and classify it into ONE of these domains:
- plumbing: pipes, leaks, faucets, drains, toilets, water heaters
- electrical: wiring, outlets, switches, circuit breakers, lighting
- carpentry: wood, doors, windows, cabinets, framing, flooring
- hvac: heating, cooling, air conditioning, furnace, thermostat, ventilation
- general: multi-domain, unclear, or general home maintenance

Respond with ONLY the domain name, nothing else."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    response_text = invoke_llm(messages, temperature=0.1)  # Low temp for classification
    domain = response_text.strip().lower()
    
    # Validate domain
    valid_domains = ["plumbing", "electrical", "carpentry", "hvac", "general"]
    if domain not in valid_domains:
        domain = "general"
    
    return domain