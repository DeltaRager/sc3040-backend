"""
ASL Sign Analysis Routes
Handles ASL sign recognition and analysis using OpenRouter API
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
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
    request: Request,
    image: UploadFile = File(..., description="Image file containing ASL sign"),
    letter_range: str = Form(..., description="Letter range: 'A-N' or 'O-Z'"),
    expected_letter: str = Form(..., description="The letter the user should be signing"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze ASL sign from uploaded image
    
    Args:
        image: Image file containing the ASL sign
        letter_range: Letter range to analyze ("A-N" or "O-Z")
        expected_letter: The letter the user should be signing
        current_user: Authenticated user data
        
    Returns:
        Analysis result with letter prediction, score, feedback, and correctness
    """
    try:
        # Debug logging
        logger.info(f"Received request - letter_range: '{letter_range}', expected_letter: '{expected_letter}'")
        try:
            form_data = await request.form()
            logger.info(f"Request form data: {dict(form_data)}")
        except Exception as e:
            logger.error(f"Error getting form data: {e}")
        
        try:
            files_data = await request.files()
            logger.info(f"Request files: {dict(files_data)}")
        except Exception as e:
            logger.error(f"Error getting files data: {e}")
        
        # Validate letter range
        if letter_range not in ["A-N", "O-Z"]:
            logger.error(f"Invalid letter range: '{letter_range}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Letter range must be 'A-N' or 'O-Z'"
            )
        
        # Validate expected letter
        logger.info(f"Expected letter type: {type(expected_letter)}, value: '{expected_letter}'")
        if not expected_letter or len(expected_letter) != 1:
            logger.error(f"Invalid expected letter: '{expected_letter}' (length: {len(expected_letter) if expected_letter else 0})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expected letter must be a single character"
            )
        
        # Check if expected letter is in the correct range
        try:
            expected_letter_upper = expected_letter.upper()
            logger.info(f"Expected letter upper: '{expected_letter_upper}'")
            
            if letter_range == "A-N" and not ('A' <= expected_letter_upper <= 'N'):
                logger.error(f"Expected letter '{expected_letter}' not in range A-N")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expected letter must be in range A-N"
                )
            elif letter_range == "O-Z" and not ('O' <= expected_letter_upper <= 'Z'):
                logger.error(f"Expected letter '{expected_letter}' not in range O-Z")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expected letter must be in range O-Z"
                )
        except Exception as e:
            logger.error(f"Error processing expected letter: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid expected letter format: {str(e)}"
            )
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read and process image
        logger.info(f"Processing image: {image.filename}, content_type: {image.content_type}")
        try:
            image_data = await image.read()
            logger.info(f"Image data length: {len(image_data)}")
        except Exception as e:
            logger.error(f"Error reading image: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read image file"
            )
        
        # Convert to PIL Image
        try:
            pil_image = Image.open(BytesIO(image_data))
            logger.info(f"PIL image created successfully: {pil_image.size}")
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Convert to base64 for API
        try:
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()
            logger.info(f"Base64 conversion successful, length: {len(img_b64)}")
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image"
            )
        
        # Set up prompt based on letter range
        if letter_range == "A-N":
            eligible_letters = "A to N,"
        else:  # O-Z
            eligible_letters = "O to Z,"
        
        prompt = f"You are an expert ASL instructor. The user is signing one of these letters: {eligible_letters}. The user should be signing the letter '{expected_letter.upper()}'. \
        Analyze the handshape, palm orientation, and position. \
        \
        Respond in this EXACT format: \
        Your Sign Looks Like: [Letter] \
        Score: [1–3] ⭐️ (3 = great match, 1 = needs more practice) \
        Feedback: [Short, friendly note on what's right or off - e.g., finger position, thumb placement, or hand shape.] \
        \
        If you think the sign does not correspond to any letter in the range, respond with: \
        Your Sign Looks Like: Not identified \
        Score: 0 ⭐️ \
        Feedback: Letter not identified. Please try again."
        
        # Get OpenAI client
        client = get_openai_client()
        
        # Send request to OpenRouter
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Use a valid OpenRouter model
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
            logger.info(f"API call successful, response type: {type(analysis_result)}")
            
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {api_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI analysis failed: {str(api_error)}"
            )
        
        # Parse the analysis result to extract the analyzed letter and determine correctness
        analyzed_letter = None
        is_correct = False
        score = 0
        
        try:
            # Ensure analysis_result is a string
            if not isinstance(analysis_result, str):
                logger.error(f"Analysis result is not a string: {type(analysis_result)}")
                analysis_result = str(analysis_result)
            
            # Extract the analyzed letter from the response
            lines = analysis_result.split('\n')
            for line in lines:
                if line.startswith('Your Sign Looks Like:'):
                    letter_part = line.split(':', 1)[1].strip()
                    if letter_part != 'Not identified':
                        analyzed_letter = letter_part
                    break
            
            # Extract score
            for line in lines:
                if line.startswith('Score:'):
                    score_part = line.split(':', 1)[1].strip()
                    # Extract number from score (e.g., "3 ⭐️" -> 3)
                    import re
                    score_match = re.search(r'(\d+)', score_part)
                    if score_match:
                        score = int(score_match.group(1))
                    break
            
            # Determine if the analyzed letter matches the expected letter
            if analyzed_letter and analyzed_letter.upper() == expected_letter.upper():
                is_correct = True
                
        except Exception as e:
            logger.error(f"Error parsing analysis result: {e}")
            logger.error(f"Analysis result type: {type(analysis_result)}")
            logger.error(f"Analysis result content: {analysis_result}")
            # If parsing fails, assume incorrect
            is_correct = False
        
        # Log the analysis for debugging (optional)
        logger.info(f"ASL analysis completed for user {current_user['id']}, letter_range: {letter_range}, expected: {expected_letter}, analyzed: {analyzed_letter}, correct: {is_correct}")
        
        return {
            "success": True,
            "analysis": analysis_result,
            "letter_range": letter_range,
            "expected_letter": expected_letter.upper(),
            "analyzed_letter": analyzed_letter,
            "is_correct": is_correct,
            "score": score,
            "user_id": current_user["id"],
            "model_used": "gpt-4o-mini"
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

@router.post("/test")
async def test_endpoint(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Test endpoint to debug form data issues
    """
    try:
        form_data = await request.form()
        logger.info(f"Test endpoint - form data: {dict(form_data)}")
        return {
            "success": True,
            "form_data": dict(form_data),
            "user_id": current_user["id"]
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {"success": False, "error": str(e)}

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
