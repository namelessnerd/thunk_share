import time
import asyncio
from functools import wraps
import logging

def measure_execution_time(func):
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()  # Record the start time
            result = await func(*args, **kwargs)  # Await and execute the async function
            end_time = time.time()  # Record the end time
            execution_time = end_time - start_time  # Calculate the elapsed time
            logging.info(f"{func.__name__} took {execution_time:.4f} seconds to execute (async).")
            return result
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()  # Record the start time
            result = func(*args, **kwargs)  # Execute the sync function
            end_time = time.time()  # Record the end time
            execution_time = end_time - start_time  # Calculate the elapsed time
            logging.info(f"{func.__name__} took {execution_time:.4f} seconds to execute (sync).")
            return result
        return sync_wrapper
