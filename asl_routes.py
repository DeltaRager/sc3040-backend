"""
ASL Sign Analysis Routes
Handles ASL sign recognition and analysis using OpenRouter API
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any, Optional
from auth import get_current_user
from config import settings
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/asl", tags=["asl"])

# Initialize OpenAI client
def get_openai_client() -> OpenAI:
    """Initialize OpenAI client with OpenRouter API key"""
    api_key = settings.openai_api_key
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenRouter API key not configured"
        )
    
    return OpenAI(
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",  # Frontend URL
            "X-Title": "SignLingo ASL Analysis API",
        },
    )

@router.post("/analyze")
async def analyze_asl_sign(
    image: UploadFile = File(..., description="Image file containing ASL sign"),
    letter_range: str = Form(..., description="Letter range: 'A-N' or 'O-Z'"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze ASL sign from uploaded image
    
    Args:
        image: Image file containing the ASL sign
        letter_range: Letter range to analyze ("A-N" or "O-Z")
        current_user: Authenticated user data
        
    Returns:
        Analysis result with letter prediction, score, and feedback
    """
    try:
        # Validate letter range
        if letter_range not in ["A-N", "O-Z"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Letter range must be 'A-N' or 'O-Z'"
            )
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read and process image
        image_data = await image.read()
        
        # Convert to PIL Image
        try:
            pil_image = Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Convert to base64 for API
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Set up prompt based on letter range
        if letter_range == "A-N":
            eligible_letters = "A to N,"
        else:  # O-Z
            eligible_letters = "O to Z,"
        
        prompt = f"Between the letters {eligible_letters} what ASL handsign is in this image? Isolate only the hand and thumb and ignore orientation of the sign and analyze. \
        `           Your Sign Looks Like: [Letter] \
                    Score: [1–3] ⭐️ (3 = great match, 1 = needs more practice) \
                    Feedback: [Short, friendly note on what's right or off - e.g., finger position, thumb placement, or hand shape.] \
                    If you are not confident, then also give the second most confident letter you think it is."
        
        # Get OpenAI client
        client = get_openai_client()
        
        # Send request to OpenRouter
        completion = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",  # Using the same model as the original
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                        }
                    ]
                }
            ]
        )
        
        analysis_result = completion.choices[0].message.content
        
        # Log the analysis for debugging (optional)
        logger.info(f"ASL analysis completed for user {current_user['id']}, letter_range: {letter_range}")
        
        return {
            "success": True,
            "analysis": analysis_result,
            "letter_range": letter_range,
            "user_id": current_user["id"],
            "model_used": "gpt-5-nano-2025-08-07"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in ASL analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze ASL sign"
        )

@router.get("/health")
async def asl_health_check(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Health check for ASL analysis service
    """
    try:
        # Test if OpenAI client can be initialized
        client = get_openai_client()
        
        return {
            "status": "healthy",
            "service": "ASL Analysis",
            "api_configured": bool(settings.openai_api_key),
            "user_id": current_user["id"]
        }
    except Exception as e:
        logger.error(f"ASL health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ASL analysis service unavailable"
        )
