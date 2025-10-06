from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    try:
        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set. Please create a .env file with your Supabase credentials.")
        
        if not settings.supabase_publishable_key:
            raise ValueError("SUPABASE_PUBLISHABLE_KEY environment variable is not set. Please create a .env file with your Supabase credentials.")
        
        logger.info("Creating Supabase client...")
        client = create_client(settings.supabase_url, settings.supabase_publishable_key)
        logger.info("Supabase client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        logger.error("Please ensure you have created a .env file with valid Supabase credentials.")
        raise


def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key"""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
