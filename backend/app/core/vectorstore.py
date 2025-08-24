"""Vector store configuration for ChromaDB."""
import chromadb
from chromadb.config import Settings
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize ChromaDB client
chroma_client = None


def get_chroma_client():
    """Get or create ChromaDB client instance."""
    global chroma_client
    
    if chroma_client is None:
        try:
            chroma_client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST,
                port=settings.CHROMADB_PORT,
                settings=Settings(
                    chroma_api_impl="rest",
                    persist_directory=None  # Use server-side persistence
                )
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
    
    return chroma_client


def get_or_create_collection(name: str, metadata: dict = None):
    """Get or create a ChromaDB collection."""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=name,
            metadata=metadata or {}
        )
        logger.info(f"Collection '{name}' ready")
        return collection
    except Exception as e:
        logger.error(f"Failed to get/create collection '{name}': {str(e)}")
        raise


def get_collections():
    """Get all available collections."""
    try:
        client = get_chroma_client()
        collections = client.list_collections()
        return collections
    except Exception as e:
        logger.error(f"Failed to list collections: {str(e)}")
        return []


def delete_collection(name: str):
    """Delete a ChromaDB collection."""
    try:
        client = get_chroma_client()
        client.delete_collection(name=name)
        logger.info(f"Collection '{name}' deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete collection '{name}': {str(e)}")
        raise


def reset_vectorstore():
    """Reset the entire vector store (delete all collections)."""
    try:
        client = get_chroma_client()
        collections = client.list_collections()
        
        for collection in collections:
            client.delete_collection(name=collection.name)
        
        logger.info("Vector store reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset vector store: {str(e)}")
        raise


# Initialize default collections
def init_default_collections():
    """Initialize default collections for the application."""
    try:
        # Collection for user profile vectors
        get_or_create_collection(
            name="user_profiles",
            metadata={
                "description": "User profile embeddings for matching",
                "embedding_function": "text-embedding-ada-002"
            }
        )
        
        # Collection for job posting vectors
        get_or_create_collection(
            name="job_postings",
            metadata={
                "description": "Job posting embeddings for matching",
                "embedding_function": "text-embedding-ada-002"
            }
        )
        
        # Collection for company vectors
        get_or_create_collection(
            name="companies",
            metadata={
                "description": "Company profile embeddings",
                "embedding_function": "text-embedding-ada-002"
            }
        )
        
        # Collection for skills vectors
        get_or_create_collection(
            name="skills",
            metadata={
                "description": "Skills and competency embeddings",
                "embedding_function": "text-embedding-ada-002"
            }
        )
        
        logger.info("Default collections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize default collections: {str(e)}")
        raise