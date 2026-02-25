"""Retry mechanisms and resilience patterns for external service calls."""

import asyncio
import functools
import random
import time
from typing import Any, Callable, List, Optional, Type, Union

from configuration.logging_config import get_logger
from core.exceptions import AIServiceError, DatabaseError, ServiceUnavailableError


logger = get_logger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        exceptions: Optional[List[Type[Exception]]] = None,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Whether to add random jitter to delays
            exceptions: List of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.exceptions = exceptions or [Exception]

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.base_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add jitter to prevent thundering herd
            delay = delay * (0.5 + random.random() * 0.5)

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """Determine if the exception should trigger a retry."""
        return any(isinstance(exception, exc_type) for exc_type in self.exceptions)


def retry_on_failure(
    config: Optional[RetryConfig] = None,
    operation_name: str = "operation",
) -> Callable:
    """Decorator to add retry logic to functions.

    Args:
        config: Retry configuration, uses defaults if None
        operation_name: Name of the operation for logging

    Returns:
        Decorator function
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as exc:
                    last_exception = exc

                    if not config.should_retry(exc):
                        logger.warning(
                            f"{operation_name} failed with non-retryable error",
                            extra={
                                "operation": operation_name,
                                "attempt": attempt + 1,
                                "error_type": type(exc).__name__,
                                "error_message": str(exc),
                            },
                        )
                        raise

                    if attempt == config.max_attempts - 1:
                        # Last attempt failed
                        logger.error(
                            f"{operation_name} failed after {config.max_attempts} attempts",
                            extra={
                                "operation": operation_name,
                                "total_attempts": config.max_attempts,
                                "final_error_type": type(exc).__name__,
                                "final_error_message": str(exc),
                            },
                        )
                        raise

                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"{operation_name} failed, retrying in {delay:.2f} seconds",
                        extra={
                            "operation": operation_name,
                            "attempt": attempt + 1,
                            "max_attempts": config.max_attempts,
                            "delay_seconds": delay,
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        },
                    )

                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    last_exception = exc

                    if not config.should_retry(exc):
                        logger.warning(
                            f"{operation_name} failed with non-retryable error",
                            extra={
                                "operation": operation_name,
                                "attempt": attempt + 1,
                                "error_type": type(exc).__name__,
                                "error_message": str(exc),
                            },
                        )
                        raise

                    if attempt == config.max_attempts - 1:
                        # Last attempt failed
                        logger.error(
                            f"{operation_name} failed after {config.max_attempts} attempts",
                            extra={
                                "operation": operation_name,
                                "total_attempts": config.max_attempts,
                                "final_error_type": type(exc).__name__,
                                "final_error_message": str(exc),
                            },
                        )
                        raise

                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"{operation_name} failed, retrying in {delay:.2f} seconds",
                        extra={
                            "operation": operation_name,
                            "attempt": attempt + 1,
                            "max_attempts": config.max_attempts,
                            "delay_seconds": delay,
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        },
                    )

                    await asyncio.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        # Return the appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation for service resilience."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        name: str = "circuit_breaker",
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time to wait before attempting to close circuit
            expected_exception: Exception type that triggers the circuit breaker
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name

        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def _can_attempt(self) -> bool:
        """Check if an attempt can be made based on current state."""
        if self._state == "CLOSED":
            return True
        elif self._state == "OPEN":
            if time.time() - self._last_failure_time >= self.timeout:
                self._state = "HALF_OPEN"
                logger.info(
                    f"Circuit breaker {self.name} moving to HALF_OPEN state",
                    extra={"circuit_breaker": self.name, "state": self._state},
                )
                return True
            return False
        else:  # HALF_OPEN
            return True

    def _record_success(self) -> None:
        """Record a successful operation."""
        if self._state == "HALF_OPEN":
            self._state = "CLOSED"
            logger.info(
                f"Circuit breaker {self.name} closing after successful operation",
                extra={"circuit_breaker": self.name, "state": self._state},
            )

        self._failure_count = 0

    def _record_failure(self) -> None:
        """Record a failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"
            logger.warning(
                f"Circuit breaker {self.name} opening after {self._failure_count} failures",
                extra={
                    "circuit_breaker": self.name,
                    "state": self._state,
                    "failure_count": self._failure_count,
                },
            )

    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not self._can_attempt():
                raise ServiceUnavailableError(
                    f"Circuit breaker {self.name} is OPEN",
                    service=self.name,
                    context={"state": self._state, "failure_count": self._failure_count},
                )

            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result

            except self.expected_exception as exc:
                self._record_failure()
                raise
            except Exception:
                # Don't count unexpected exceptions as circuit breaker failures
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not self._can_attempt():
                raise ServiceUnavailableError(
                    f"Circuit breaker {self.name} is OPEN",
                    service=self.name,
                    context={"state": self._state, "failure_count": self._failure_count},
                )

            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result

            except self.expected_exception as exc:
                self._record_failure()
                raise
            except Exception:
                # Don't count unexpected exceptions as circuit breaker failures
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    @property
    def state(self) -> str:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count


# Predefined retry configurations for common scenarios
AI_SERVICE_RETRY = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    exceptions=[AIServiceError, ConnectionError, TimeoutError],
)

DATABASE_RETRY = RetryConfig(
    max_attempts=2,
    base_delay=1.0,
    max_delay=10.0,
    backoff_multiplier=2.0,
    exceptions=[DatabaseError, ConnectionError],
)

IMAGE_PROCESSING_RETRY = RetryConfig(
    max_attempts=2,
    base_delay=0.5,
    max_delay=5.0,
    backoff_multiplier=2.0,
    exceptions=[IOError, OSError],
)


# Predefined circuit breakers
ai_service_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60.0,
    expected_exception=AIServiceError,
    name="ai_service",
)

database_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30.0,
    expected_exception=DatabaseError,
    name="database",
)