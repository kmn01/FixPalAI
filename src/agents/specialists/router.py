"""Lightweight router: map user query to domain."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from src.services.llm_utils import get_llm

from src.agents.specialists.registry import DOMAINS

Domain = Literal["plumbing", "electrical", "carpentry", "hvac", "general"]

ROUTER_PROMPT = """Classify the following home repair question into exactly one domain. Reply with only the domain name, nothing else.

Domains: plumbing, electrical, carpentry, hvac, general

- plumbing: pipes, drains, faucets, toilets, water heaters, leaks, sinks, showers
- electrical: wiring, outlets, switches, circuit breakers, lights, GFCI, panels
- carpentry: doors, cabinets, trim, floors, wood, furniture, screws, hinges
- hvac: furnace, AC, thermostat, air conditioning, heating, filters, ducts
- general: unclear, multiple domains, or doesn't fit above

Question: {query}"""


def route_query(query: str, image_context: str | None = None) -> Domain:
    """
    Classify user query into a domain using LLM.
    Falls back to keyword matching if LLM fails.
    """
    full_query = query
    if image_context:
        full_query = f"{query}\n[Image context: {image_context}]"

    try:
        llm = get_llm(temperature=0.0)
        messages = [
            HumanMessage(content=ROUTER_PROMPT.format(query=full_query)),
        ]
        response = llm.invoke(messages)
        text = (response.content if hasattr(response, "content") else str(response)).strip().lower()
        for d in DOMAINS:
            if d in text or text == d:
                return d
    except Exception:
        pass

    return _keyword_route(query)


def _keyword_route(query: str) -> Domain:
    """Fallback: keyword-based routing."""
    q = query.lower()
    if any(w in q for w in ["pipe", "drain", "faucet", "toilet", "leak", "sink", "water", "plumb"]):
        return "plumbing"
    if any(w in q for w in ["wire", "outlet", "switch", "circuit", "breaker", "electric", "light", "gfci"]):
        return "electrical"
    if any(w in q for w in ["door", "cabinet", "trim", "floor", "wood", "screw", "hinge", "carpent"]):
        return "carpentry"
    if any(w in q for w in ["furnace", "ac", "thermostat", "hvac", "filter", "heat", "cool", "duct"]):
        return "hvac"
    return "general"