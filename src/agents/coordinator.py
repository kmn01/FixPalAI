"""Coordinator - routes queries to specialists, with optional Dedalus support."""

import os
from langchain_core.vectorstores import VectorStore


def classify_domain(query: str) -> str:
    """Classify query into domain, with optional Dedalus support."""
    use_dedalus = os.getenv("USE_DEDALUS", "false").lower() == "true"
    
    if use_dedalus:
        return _classify_with_dedalus(query)
    else:
        return _classify_with_gemini(query)


def coordinator_invoke(
    user_query: str,
    vector_store: VectorStore | None = None,
    image_context: str | None = None,
) -> tuple[str, str]:
    """
    Main coordinator function: classify domain and route to specialist.
    Returns: (answer, domain)
    """
    from src.agents.specialists.registry import get_specialist_response
    
    # Build context for classification
    context = user_query
    if image_context:
        context += f"\nImage context: {image_context}"
    
    # Classify domain
    domain = classify_domain(context)
    
    # Get specialist response
    answer = get_specialist_response(
        domain=domain,
        user_query=user_query,
        vector_store=vector_store,
        image_context=image_context,
    )
    
    return answer, domain


def _classify_with_dedalus(query: str) -> str:
    """Use Dedalus for classification."""
    try:
        from src.services.dedalus_wrapper import get_dedalus_agent
        
        prompt = f"""Classify this home repair query into ONE domain:
- plumbing: pipes, leaks, faucets, drains, toilets, water heaters
- electrical: wiring, outlets, switches, circuit breakers, lighting
- carpentry: wood, doors, windows, cabinets, framing
- hvac: heating, cooling, air conditioning, furnace, thermostat
- general: unclear or multi-domain

Respond with ONLY the domain name.

Query: {query}"""
        
        agent = get_dedalus_agent()
        domain = agent.run(prompt).strip().lower()
        
        valid = ["plumbing", "electrical", "carpentry", "hvac", "general"]
        return domain if domain in valid else "general"
    except Exception as e:
        print(f"Dedalus classification failed: {e}, using fallback")
        return _keyword_route(query)


def _classify_with_gemini(query: str) -> str:
    """Use Gemini for classification (fallback)."""
    try:
        from langchain_core.messages import HumanMessage
        from src.services.llm_utils import get_llm
        
        prompt = f"""Classify this query into ONE domain:
plumbing, electrical, carpentry, hvac, or general

Query: {query}

Respond with only the domain name."""
        
        llm = get_llm(temperature=0.1)
        response = llm.invoke([HumanMessage(content=prompt)])
        domain = response.content.strip().lower()
        
        valid = ["plumbing", "electrical", "carpentry", "hvac", "general"]
        return domain if domain in valid else "general"
    except Exception as e:
        print(f"Gemini classification failed: {e}, using keyword fallback")
        return _keyword_route(query)


def _keyword_route(query: str) -> str:
    """Keyword-based fallback routing."""
    q = query.lower()
    if any(w in q for w in ["pipe", "drain", "faucet", "toilet", "leak", "water", "plumb"]):
        return "plumbing"
    if any(w in q for w in ["wire", "outlet", "switch", "circuit", "breaker", "electric", "light"]):
        return "electrical"
    if any(w in q for w in ["door", "cabinet", "trim", "floor", "wood", "carpent"]):
        return "carpentry"
    if any(w in q for w in ["furnace", "ac", "thermostat", "hvac", "heat", "cool"]):
        return "hvac"
    return "general"