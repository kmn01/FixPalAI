"""LLM model utilities - Gemini and Dedalus integration."""

import os
from typing import Sequence

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


def get_llm(model_name: str | None = None, temperature: float = 0.7):
    """Get Gemini LLM instance."""
    model = model_name or os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
    )


def get_vision_llm(temperature: float = 0.7):
    """Get Gemini vision-capable LLM."""
    model = os.getenv("VISION_MODEL", "gemini-2.5-flash")
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
    )

def get_dedalus_llm(prompt: str, temperature: float = 0.7):
    """Run Dedalus with the given prompt. Returns the model output string. Requires: pip install dedalus-labs."""
    import asyncio
    try:
        from dedalus_labs import AsyncDedalus, DedalusRunner
    except ImportError:
        raise ImportError("Dedalus requires the 'dedalus_labs' package. Install with: pip install dedalus-labs")

    async def main():
        client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
        runner = DedalusRunner(client)
        response = await runner.run(
            input=prompt,
            model=os.getenv("DEDALUS_MODEL"),
        )
        return response.final_output or ""

    return asyncio.run(main())


def _messages_to_prompt(messages: Sequence[BaseMessage]) -> str:
    """Convert LangChain messages to a single prompt string for Dedalus."""
    parts = []
    for m in messages:
        role = "System" if isinstance(m, SystemMessage) else "Human"
        content = getattr(m, "content", str(m))
        if isinstance(content, list):
            text_parts = [
                c.get("text", c) for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ]
            content = " ".join(str(t) for t in text_parts) if text_parts else str(content)
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


def invoke_llm(
    messages: Sequence[BaseMessage],
    temperature: float = 0.7,
    model_name: str | None = None,
) -> str:
    """
    Invoke LLM with the given messages.
    Uses Dedalus if USE_DEDALUS is set and dedalus_labs is installed; otherwise Gemini.
    Returns the model output as a string. Gemini code path is unchanged when not using Dedalus.
    """
    if os.getenv("USE_DEDALUS") and os.getenv("DEDALUS_API_KEY") and os.getenv("DEDALUS_MODEL"):
        try:
            prompt = _messages_to_prompt(messages)
            return get_dedalus_llm(prompt, temperature=temperature)
        except ImportError:
            import warnings
            warnings.warn(
                "USE_DEDALUS is set but 'dedalus_labs' is not installed. Install with: pip install dedalus-labs. Using Gemini.",
                UserWarning,
                stacklevel=2,
            )
    llm = get_llm(model_name=model_name, temperature=temperature)
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)