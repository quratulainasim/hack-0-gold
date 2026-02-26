#!/usr/bin/env python3
"""
Error Logger & Recovery Module
Implements exponential backoff, circuit breakers, and comprehensive logging.
"""

import logging
import logging.config
import time
import random
import functools
from typing import Callable, Optional, Tuple, Type, Union
from datetime import datetime, timedelta
from enum import Enum


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(config_file: Optional[str] = None):
    """Setup logging configuration"""
    if config_file:
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # Default configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

# Create default logger
logger = logging.getLogger('error_recovery')


# ============================================================================
# Exponential Backoff Implementation
# ============================================================================

class RetryStrategy:
    """Base class for retry strategies"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        raise NotImplementedError

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if should retry based on attempt and exception"""
        return attempt < self.max_retries


class ExponentialBackoffStrategy(RetryStrategy):
    """Exponential backoff retry strategy"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        super().__init__(max_retries)
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        # Calculate exponential delay
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class LinearBackoffStrategy(RetryStrategy):
    """Linear backoff retry strategy"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        super().__init__(max_retries)
        self.base_delay = base_delay

    def get_delay(self, attempt: int) -> float:
        """Calculate linear backoff delay"""
        return self.base_delay * (attempt + 1)


class FixedDelayStrategy(RetryStrategy):
    """Fixed delay retry strategy"""

    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        super().__init__(max_retries)
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        """Return fixed delay"""
        return self.delay


# ============================================================================
# Retry Decorators
# ============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
    on_failure: Optional[Callable] = None
):
    """
    Decorator for retrying function with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delay
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Callback function called on each retry
        on_failure: Callback function called on final failure
    """
    strategy = ExponentialBackoffStrategy(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0

            while True:
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(
                            f"{func.__name__} succeeded after {attempt} retries"
                        )
                    return result

                except exceptions as e:
                    attempt += 1

                    if not strategy.should_retry(attempt, e):
                        logger.error(
                            f"{func.__name__} failed after {attempt} attempts: {e}",
                            exc_info=True
                        )
                        if on_failure:
                            on_failure(e, attempt)
                        raise

                    delay = strategy.get_delay(attempt - 1)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_retries}), "
                        f"retrying in {delay:.2f}s: {e}"
                    )

                    if on_retry:
                        on_retry(e, attempt, delay)

                    time.sleep(delay)

        return wrapper
    return decorator


def retry_fixed(max_retries: int = 3, delay: float = 1.0, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """Decorator for retrying with fixed delay"""
    strategy = FixedDelayStrategy(max_retries=max_retries, delay=delay)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if not strategy.should_retry(attempt, e):
                        logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
                        raise

                    delay = strategy.get_delay(attempt - 1)
                    logger.warning(f"{func.__name__} retrying in {delay}s (attempt {attempt})")
                    time.sleep(delay)

        return wrapper
    return decorator


def retry_linear(max_retries: int = 3, base_delay: float = 1.0, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """Decorator for retrying with linear backoff"""
    strategy = LinearBackoffStrategy(max_retries=max_retries, base_delay=base_delay)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if not strategy.should_retry(attempt, e):
                        logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
                        raise

                    delay = strategy.get_delay(attempt - 1)
                    logger.warning(f"{func.__name__} retrying in {delay:.2f}s (attempt {attempt})")
                    time.sleep(delay)

        return wrapper
    return decorator


# ============================================================================
# Circuit Breaker Pattern
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit tripped, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation

    Prevents cascading failures by failing fast when a service is unavailable.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state")
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN, failing fast")
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is open for {func.__name__}"
                    )

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result

            except self.expected_exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker test successful, closing circuit")
            self.state = CircuitState.CLOSED
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.error(
                    f"Circuit breaker threshold reached ({self.failure_count} failures), "
                    f"opening circuit"
                )
                self.state = CircuitState.OPEN

    def reset(self):
        """Manually reset circuit breaker"""
        logger.info("Circuit breaker manually reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# ============================================================================
# Error Classification
# ============================================================================

class ErrorClassifier:
    """Classify errors as transient or permanent"""

    def __init__(self):
        self.transient_errors = set()
        self.permanent_errors = set()

    def add_transient(self, *exceptions: Type[Exception]):
        """Add exceptions that should be retried"""
        self.transient_errors.update(exceptions)

    def add_permanent(self, *exceptions: Type[Exception]):
        """Add exceptions that should not be retried"""
        self.permanent_errors.update(exceptions)

    def is_transient(self, exception: Exception) -> bool:
        """Check if exception is transient"""
        return type(exception) in self.transient_errors

    def is_permanent(self, exception: Exception) -> bool:
        """Check if exception is permanent"""
        return type(exception) in self.permanent_errors

    def classify(self, exception: Exception) -> str:
        """Classify exception as transient, permanent, or unknown"""
        if self.is_transient(exception):
            return "transient"
        elif self.is_permanent(exception):
            return "permanent"
        else:
            return "unknown"


# ============================================================================
# Retry Metrics
# ============================================================================

class RetryMetrics:
    """Track retry metrics for monitoring"""

    def __init__(self):
        self.total_attempts = 0
        self.successful = 0
        self.failed = 0
        self.total_retries = 0
        self.retry_counts = []

    def record_attempt(self, success: bool, retry_count: int):
        """Record an attempt"""
        self.total_attempts += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1

        if retry_count > 0:
            self.total_retries += retry_count
            self.retry_counts.append(retry_count)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful / self.total_attempts

    @property
    def average_retries(self) -> float:
        """Calculate average number of retries"""
        if not self.retry_counts:
            return 0.0
        return sum(self.retry_counts) / len(self.retry_counts)

    def to_dict(self) -> dict:
        """Convert metrics to dictionary"""
        return {
            'total_attempts': self.total_attempts,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': self.success_rate,
            'total_retries': self.total_retries,
            'average_retries': self.average_retries
        }


# ============================================================================
# Context Manager for Logging
# ============================================================================

class LogContext:
    """Context manager for adding context to logs"""

    _context = {}

    def __init__(self, **kwargs):
        self.context = kwargs
        self.old_context = {}

    def __enter__(self):
        self.old_context = LogContext._context.copy()
        LogContext._context.update(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        LogContext._context = self.old_context

    @classmethod
    def get_context(cls) -> dict:
        """Get current context"""
        return cls._context.copy()


# ============================================================================
# Structured Logger
# ============================================================================

class StructuredLogger:
    """Logger with structured logging support"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        """Log with structured data"""
        context = LogContext.get_context()
        extra = {**context, **kwargs}
        self.logger.log(level, message, extra={'structured': extra})

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        self.logger.error(message, exc_info=exc_info, extra={'structured': kwargs})

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        self.logger.critical(message, exc_info=exc_info, extra={'structured': kwargs})


# ============================================================================
# Async Support
# ============================================================================

try:
    import asyncio

    def async_retry_with_backoff(
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """Async version of retry_with_backoff decorator"""
        strategy = ExponentialBackoffStrategy(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter
        )

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                attempt = 0

                while True:
                    try:
                        result = await func(*args, **kwargs)
                        if attempt > 0:
                            logger.info(f"{func.__name__} succeeded after {attempt} retries")
                        return result

                    except exceptions as e:
                        attempt += 1

                        if not strategy.should_retry(attempt, e):
                            logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
                            raise

                        delay = strategy.get_delay(attempt - 1)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{max_retries}), "
                            f"retrying in {delay:.2f}s: {e}"
                        )

                        await asyncio.sleep(delay)

            return wrapper
        return decorator

except ImportError:
    # asyncio not available
    pass


# ============================================================================
# Utility Functions
# ============================================================================

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise

    return wrapper


def log_exceptions(func: Callable) -> Callable:
    """Decorator to log exceptions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    setup_logging()

    # Example 1: Basic retry with exponential backoff
    @retry_with_backoff(max_retries=3, base_delay=1)
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Connection failed")
        return "Success"

    # Example 2: Circuit breaker
    breaker = CircuitBreaker(failure_threshold=3, timeout=10)

    @breaker
    def unreliable_service():
        import random
        if random.random() < 0.8:
            raise Exception("Service unavailable")
        return "Success"

    # Example 3: Error classification
    classifier = ErrorClassifier()
    classifier.add_transient(ConnectionError, TimeoutError)
    classifier.add_permanent(ValueError, TypeError)

    # Test
    try:
        result = flaky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")
