import os
import redis
import logging
from typing import Optional, Any
from tenacity import retry, stop_after_delay, wait_exponential, RetryError
from utils.sysutils import getenv

# Set up logging
logging.basicConfig(level=logging.INFO)


class RedisConfig:
    """Loads the Redis configuration from environment variables."""
    
    def __init__(self) -> None:
        """Initializes the RedisConfig object by loading settings from environment variables."""

        self.host = getenv('REDIS_HOST', str, 'redis')
        self.port = getenv('REDIS_PORT', int, 6379)
        self.db = getenv('REDIS_DB', int, 0)
        self.max_connections = getenv('REDIS_MAX_CONNECTIONS', int, 10)
        self.retry_stop_after_delay = getenv('RETRY_STOP_AFTER_DELAY', int, 10)
        self.retry_wait_multiplier = getenv('RETRY_WAIT_MULTIPLIER', int, 1)
        self.retry_wait_min = getenv('RETRY_WAIT_MIN', int, 1)
        self.retry_wait_max = getenv('RETRY_WAIT_MAX', int, 5)


class RedisClient:
    """Handles Redis connections with retry and exponential backoff."""

    def __init__(self, config: RedisConfig) -> None:
        """
        Initialize RedisClient with Redis configuration.
        :param config: RedisConfig object containing Redis settings.
        """
        self.config = config
        self.redis_pool = redis.ConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            max_connections=config.max_connections
        )


    @retry(
        stop=stop_after_delay(int(os.getenv('RETRY_STOP_AFTER_DELAY', 10))),
        wait=wait_exponential(
            multiplier=int(os.getenv('RETRY_WAIT_MULTIPLIER', 1)),
            min=int(os.getenv('RETRY_WAIT_MIN', 1)),
            max=int(os.getenv('RETRY_WAIT_MAX', 5))
        )
    )
    def get_connection(self) -> redis.Redis:
        """
        Get a Redis connection from the connection pool.
        Will retry with exponential backoff in case of failures.
        :raises RedisError: If unable to connect after retries.
        :return: Redis connection object.
        """
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.ping()  # Check if the Redis server is reachable
            logging.info("Successfully connected to Redis.")
            return redis_conn
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.error(f"Redis connection error: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unexpected error during Redis connection: {e}")
            raise Exception("Failed to connect to Redis.") from e
