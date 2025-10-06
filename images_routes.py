"""
Images API Routes - Non-protected endpoints for retrieving images from Supabase Storage
"""

from fastapi import APIRouter, HTTPException, Query
from database import get_supabase_client, get_supabase_admin_client
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/images", tags=["images"])

@router.get("/")
async def get_image_url(
    filename: str = Query(..., description="Name of the image file to retrieve")
):
    """
    Get a public URL for an image stored in Supabase Storage
    
    Args:
        filename: The name of the image file (e.g., "asl-signs.png")
    
    Returns:
        dict: Contains the public URL for the image
        
    Example:
        GET /api/images?filename=asl-signs.png
        Returns: {"url": "https://your-project.supabase.co/storage/v1/object/public/images/asl-signs.png"}
    """
    try:
        # Get Supabase clients
        supabase_admin = get_supabase_admin_client()  # For file listing
        supabase = get_supabase_client()  # For public URL generation
        
        # Define the bucket name (you can change this to match your storage bucket)
        bucket_name = "Sign Images"  # Change this to match your actual bucket name
        
        # Get the public URL for the image
        try:
            # This creates a signed URL that's valid for 1 hour
            # For public images, you can also use the direct public URL
            response = supabase.storage.from_(bucket_name).get_public_url(filename)
            
            # Alternative: If you want to check if the file exists first
            # files = supabase.storage.from_(bucket_name).list()
            # if not any(file['name'] == filename for file in files):
            #     raise HTTPException(status_code=404, detail="Image not found")
            
            logger.info(f"Successfully generated URL for image: {filename}")
            
            return {
                "success": True,
                "filename": filename,
                "url": response,
                "bucket": bucket_name
            }
            
        except Exception as storage_error:
            logger.error(f"Storage error for filename {filename}: {storage_error}")
            
            # If the file doesn't exist or there's a storage error, return a 404
            raise HTTPException(
                status_code=404, 
                detail=f"Image '{filename}' not found in storage bucket '{bucket_name}'"
            )
    
    except Exception as e:
        logger.error(f"Error retrieving image {filename}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while retrieving image: {str(e)}"
        )

@router.get("/list")
async def list_images():
    """
    List all available images in the storage bucket
    
    Returns:
        dict: Contains a list of all available images
    """
    try:
        # Get Supabase admin client (needed for listing files)
        supabase = get_supabase_admin_client()
        
        # Define the bucket name
        bucket_name = "Sign Images"  # Change this to match your actual bucket name
        
        # List all files in the bucket
        files = supabase.storage.from_(bucket_name).list()
        
        # Extract just the filenames
        image_files = [file['name'] for file in files if file['name']]
        
        logger.info(f"Found {len(image_files)} images in bucket '{bucket_name}'")
        
        return {
            "success": True,
            "bucket": bucket_name,
            "count": len(image_files),
            "images": image_files
        }
        
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while listing images: {str(e)}"
        )

@router.get("/health")
async def images_health():
    """
    Health check for images service
    
    Returns:
        dict: Service status
    """
    return {
        "service": "images",
        "status": "healthy",
        "endpoints": [
            "GET /api/images?filename=<image_name>",
            "GET /api/images/list",
            "GET /api/images/debug",
            "GET /api/images/health"
        ]
    }
