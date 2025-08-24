"""Redis cache configuration."""
import redis
from typing import Optional, Any
import json
import pickle
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize Redis client
redis_client = None


def get_redis_client():
    """Get or create Redis client instance."""
    global redis_client
    
    if redis_client is None:
        try:
            redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Keep as bytes for pickle support
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            redis_client.ping()
            logger.info("Redis client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise
    
    return redis_client


class CacheManager:
    """Cache manager for Redis operations."""
    
    def __init__(self):
        self.client = get_redis_client()
        self.default_ttl = 3600  # 1 hour default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in cache."""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = pickle.dumps(value)
            
            return self.client.setex(key, ttl, serialized_value)
            
        except Exception as e:
            logger.error(f"Failed to set cache key '{key}': {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, UnicodeDecodeError):
                try:
                    return pickle.loads(value)
                except:
                    return value.decode('utf-8') if isinstance(value, bytes) else value
                    
        except Exception as e:
            logger.error(f"Failed to get cache key '{key}': {str(e)}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete cache key '{key}': {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check cache key '{key}': {str(e)}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Failed to set expiration for key '{key}': {str(e)}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get time to live for a key."""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key '{key}': {str(e)}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache."""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment key '{key}': {str(e)}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement a numeric value in cache."""
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"Failed to decrement key '{key}': {str(e)}")
            return None
    
    def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set a hash in cache."""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Serialize values
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[field] = json.dumps(value)
                else:
                    serialized_mapping[field] = str(value)
            
            result = self.client.hmset(key, serialized_mapping)
            if ttl > 0:
                self.client.expire(key, ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to set hash key '{key}': {str(e)}")
            return False
    
    def get_hash(self, key: str, field: Optional[str] = None) -> Any:
        """Get a hash or hash field from cache."""
        try:
            if field:
                value = self.client.hget(key, field)
                if value is None:
                    return None
                
                # Try to deserialize
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode('utf-8') if isinstance(value, bytes) else value
            else:
                return self.client.hgetall(key)
                
        except Exception as e:
            logger.error(f"Failed to get hash key '{key}': {str(e)}")
            return None
    
    def delete_hash_field(self, key: str, field: str) -> bool:
        """Delete a field from a hash."""
        try:
            return bool(self.client.hdel(key, field))
        except Exception as e:
            logger.error(f"Failed to delete hash field '{key}:{field}': {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear pattern '{pattern}': {str(e)}")
            return 0
    
    def get_stats(self) -> dict:
        """Get Redis server statistics."""
        try:
            info = self.client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {str(e)}")
            return {}


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager