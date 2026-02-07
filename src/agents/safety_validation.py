"""Safety validation for home repair responses."""

from langchain_core.messages import SystemMessage, HumanMessage
from src.services.llm_utils import get_llm


def validate_safety(user_query: str, response: str, domain: str) -> dict:
    """
    Validate that a repair response is safe.
    
    Args:
        user_query: Original user question
        response: AI-generated response
        domain: plumbing, electrical, carpentry, hvac, or general
    
    Returns:
        dict with:
            - is_safe: bool
            - warnings: list[str]
            - recommendations: list[str]
    """
    
    # Critical safety keywords by domain
    CRITICAL_KEYWORDS = {
        "electrical": ["live wire", "high voltage", "circuit breaker", "electrical panel", "220v", "240v"],
        "plumbing": ["gas line", "main water line", "sewer", "asbestos", "lead pipe"],
        "hvac": ["gas line", "refrigerant", "carbon monoxide", "furnace"],
        "carpentry": ["load-bearing", "structural", "asbestos", "foundation"],
    }
    
    # Check for critical keywords
    critical_detected = []
    if domain in CRITICAL_KEYWORDS:
        query_lower = user_query.lower()
        response_lower = response.lower()
        for keyword in CRITICAL_KEYWORDS[domain]:
            if keyword in query_lower or keyword in response_lower:
                critical_detected.append(keyword)
    
    # If critical work detected, use LLM to validate
    if critical_detected:
        return _llm_safety_check(user_query, response, domain, critical_detected)
    
    # Default: safe
    return {
        "is_safe": True,
        "warnings": [],
        "recommendations": []
    }


def _llm_safety_check(user_query: str, response: str, domain: str, critical_keywords: list[str]) -> dict:
    """Use LLM to perform deeper safety analysis."""
    
    system_prompt = f"""You are a safety validator for home repair instructions in the {domain} domain.

Critical elements detected: {', '.join(critical_keywords)}

Analyze the repair instructions and determine:
1. Is this safe for a DIY homeowner?
2. What safety warnings should be emphasized?
3. Should this require a licensed professional?

Respond in JSON format:
{{
    "is_safe": true/false,
    "warnings": ["warning 1", "warning 2"],
    "requires_professional": true/false,
    "reason": "brief explanation"
}}"""

    user_prompt = f"""User Query: {user_query}

Response to Validate:
{response}

Is this response safe? What warnings should be added?"""
    
    llm = get_llm(temperature=0.1)  # Low temperature for safety checks
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        result = llm.invoke(messages)
        
        # Parse response (simple string parsing since Gemini might not always return perfect JSON)
        content = result.content.lower()
        
        warnings = []
        if "requires_professional" in content or "call a professional" in content:
            warnings.append("This work may require a licensed professional. Consider consulting an expert.")
        
        if "electrical" in domain and any(kw in content for kw in ["danger", "hazard", "risk"]):
            warnings.append("ELECTRICAL HAZARD: Turn off power at the circuit breaker before attempting any work.")
        
        if "gas" in ' '.join(critical_keywords):
            warnings.append("GAS HAZARD: Contact a licensed professional for any gas-related work.")
        
        is_safe = "is_safe\": true" in content or len(warnings) == 0
        
        return {
            "is_safe": is_safe,
            "warnings": warnings,
            "recommendations": ["Always follow local building codes", "Wear appropriate safety equipment"]
        }
        
    except Exception:
        # If LLM fails, be conservative
        return {
            "is_safe": False,
            "warnings": [f"This involves {domain} work. Please consult a licensed professional for safety."],
            "recommendations": ["Safety first - when in doubt, call a professional"]
        }