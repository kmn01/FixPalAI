"""Vision analysis using Dedalus or Gemini."""

import asyncio
import base64
import os


def _detect_mime_type(image_bytes: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def analyze_image(image_bytes: bytes, user_query: str = "") -> str:
    """
    Analyze an image using Dedalus (if configured) or Gemini vision model.

    Args:
        image_bytes: Raw image bytes
        user_query: Optional context/question about the image

    Returns:
        Description/analysis from vision model
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = _detect_mime_type(image_bytes)
    prompt = (
        user_query
        or "Describe this image in detail for home repair diagnosis. Identify any visible issues, components, or relevant details."
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_image}"}},
            ],
        }
    ]

    if os.getenv("USE_DEDALUS") and os.getenv("DEDALUS_API_KEY") and os.getenv("DEDALUS_MODEL"):
        from dedalus_labs import AsyncDedalus

        async def _run():
            client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
            response = await client.chat.completions.create(
                model=os.getenv("DEDALUS_MODEL"),
                messages=messages,
            )
            return response.choices[0].message.content

        return asyncio.run(_run())

    # Fallback: Gemini via LangChain
    from langchain_core.messages import HumanMessage
    from src.services.llm_utils import get_vision_llm

    message = HumanMessage(content=messages[0]["content"])
    llm = get_vision_llm()
    response = llm.invoke([message])
    return getattr(response, "content", None) or str(response)