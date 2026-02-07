"""LLM model utilities - Gemini integration."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI


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
    import asyncio
    from dedalus_labs import AsyncDedalus, DedalusRunner

    async def main():
        client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
        runner = DedalusRunner(client)

        response = await runner.run(
            input=prompt,
            model=os.getenv("DEDALUS_MODEL"),
        )
        print(response.final_output)

    asyncio.run(main())