"""Vision analysis using Gemini."""

import base64
from langchain_core.messages import HumanMessage


def analyze_image(image_bytes: bytes, user_query: str = "") -> str:
    """
    Analyze an image using Gemini vision model.
    
    Args:
        image_bytes: Raw image bytes
        user_query: Optional context/question about the image
    
    Returns:
        Description/analysis from vision model
    """
    from src.services.llm_utils import get_vision_llm
    
    # Encode image to base64
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Prepare prompt
    prompt = user_query or "Describe this image in detail for home repair diagnosis. Identify any visible issues, components, or relevant details."
    
    # Create message with image
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{b64_image}"
            }
        ]
    )
    
    # Get vision model and analyze
    llm = get_vision_llm()
    response = llm.invoke([message])
    
    return response.content