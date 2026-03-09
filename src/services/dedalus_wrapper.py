"""Dedalus Labs integration - simplified with streaming support."""

import os
import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner


class DedalusAgent:
    """Wrapper for Dedalus agent calls."""
    
    def __init__(self):
        self.api_key = os.getenv("DEDALUS_API_KEY")
        if not self.api_key:
            raise ValueError("DEDALUS_API_KEY not found in environment")
        
        self.client = AsyncDedalus(api_key=self.api_key)
        self.runner = DedalusRunner(self.client)
        # Use Sonnet for better speed/cost balance
        self.model = os.getenv("DEDALUS_MODEL", "anthropic/claude-sonnet-4-5")
    
    async def run_async(self, input_text: str, model: str = None) -> str:
        """Run agent with Dedalus (async) with streaming enabled."""
        response = await self.runner.run(
            input=input_text,
            model=model or self.model,
            stream=True,  # Enable streaming as required by API
        )
        return response.final_output
    
    def run(self, input_text: str, model: str = None) -> str:
        """Synchronous wrapper for async run (for Streamlit compatibility)."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.run_async(input_text, model))


def get_dedalus_agent() -> DedalusAgent:
    """Get or create Dedalus agent instance."""
    return DedalusAgent()