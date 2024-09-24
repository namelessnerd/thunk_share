import unittest
from unittest.mock import patch, MagicMock
import redis
from redis.exceptions import ConnectionError, TimeoutError
from utils.sysutils import getenv
from cache.redis_client import RedisConfig, RedisClient
from tenacity import retry, stop_after_delay, wait_exponential, RetryError

class TestRedisConfig(unittest.TestCase):
    
    @patch('os.getenv')
    def test_redis_config_defaults(self, mock_getenv):
        # Simulate environment variables not being set
        mock_getenv.side_effect = lambda k, d=None: d
        config = RedisConfig()
        self.assertEqual(config.host, 'redis')
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.db, 0)
        self.assertEqual(config.max_connections, 10)
        self.assertEqual(config.retry_stop_after_delay, 10)
        self.assertEqual(config.retry_wait_multiplier, 1)
        self.assertEqual(config.retry_wait_min, 1)
        self.assertEqual(config.retry_wait_max, 5)

    @patch('os.getenv')
    def test_redis_config_env_variables(self, mock_getenv):
        # Simulate environment variables being set
        mock_getenv.side_effect = lambda k, d=None: {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6380',
            'REDIS_DB': '1',
            'REDIS_MAX_CONNECTIONS': '20',
            'RETRY_STOP_AFTER_DELAY': '15',
            'RETRY_WAIT_MULTIPLIER': '2',
            'RETRY_WAIT_MIN': '2',
            'RETRY_WAIT_MAX': '10',
        }.get(k, d)

        config = RedisConfig()

        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 6380)
        self.assertEqual(config.db, 1)
        self.assertEqual(config.max_connections, 20)
        self.assertEqual(config.retry_stop_after_delay, 15)
        self.assertEqual(config.retry_wait_multiplier, 2)
        self.assertEqual(config.retry_wait_min, 2)
        self.assertEqual(config.retry_wait_max, 10)

class TestRedisClient(unittest.TestCase):
    
    @patch('redis.Redis')
    def test_get_connection_success(self, mock_redis):
        # Mock a successful Redis connection
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        config = RedisConfig()  # Assuming default values
        client = RedisClient(config)

        connection = client.get_connection()
        mock_redis_instance.ping.assert_called_once()  # Verify ping was called
        self.assertEqual(connection, mock_redis_instance)

    @patch('redis.Redis')
    @patch('tenacity.retry')
    def test_get_connection_redis_failure(self, mock_retry, mock_redis):
        # Mock a Redis connection failure
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.side_effect = ConnectionError("Redis connection failed")
        mock_redis.return_value = mock_redis_instance

        config = RedisConfig()
        client = RedisClient(config)

        with self.assertRaises(RetryError) as context:
            client.get_connection()

        # Check if the underlying exception was a ConnectionError
        self.assertIsInstance(context.exception.last_attempt.exception(), redis.ConnectionError)