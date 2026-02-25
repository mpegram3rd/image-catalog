"""Middleware components for error handling and request processing."""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from configuration.logging_config import get_logger, log_api_request
from core.exceptions import ImageCatalogError, ValidationError


logger = get_logger(__name__)


async def error_handling_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware to handle exceptions and return structured error responses.

    This middleware catches all exceptions and converts them to appropriate
    HTTP responses with consistent error formatting.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Add request ID to request state for logging context
    request.state.request_id = request_id

    try:
        response = await call_next(request)

        # Log successful requests
        duration = time.time() - start_time
        log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration,
            logger=logger,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except ImageCatalogError as exc:
        # Handle our custom exceptions
        duration = time.time() - start_time

        logger.error(
            "Application error occurred",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "error_message": exc.message,
                "error_context": exc.context,
                "method": request.method,
                "path": str(request.url.path),
                "duration_seconds": duration,
            },
            exc_info=True,
        )

        error_response = exc.to_dict()
        error_response["request_id"] = request_id

        log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=exc.http_status,
            duration=duration,
            logger=logger,
        )

        return JSONResponse(
            status_code=exc.http_status,
            content=error_response,
            headers={"X-Request-ID": request_id},
        )

    except PydanticValidationError as exc:
        # Handle Pydantic validation errors
        duration = time.time() - start_time

        logger.warning(
            "Validation error occurred",
            extra={
                "request_id": request_id,
                "validation_errors": exc.errors(),
                "method": request.method,
                "path": str(request.url.path),
                "duration_seconds": duration,
            },
        )

        # Convert Pydantic errors to our format
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            })

        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "type": "ValidationError",
                "details": error_details,
            },
            "request_id": request_id,
        }

        log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=422,
            duration=duration,
            logger=logger,
        )

        return JSONResponse(
            status_code=422,
            content=error_response,
            headers={"X-Request-ID": request_id},
        )

    except Exception as exc:
        # Handle unexpected exceptions
        duration = time.time() - start_time

        logger.error(
            "Unexpected error occurred",
            extra={
                "request_id": request_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "method": request.method,
                "path": str(request.url.path),
                "duration_seconds": duration,
            },
            exc_info=True,
        )

        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "type": "InternalServerError",
            },
            "request_id": request_id,
        }

        log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=500,
            duration=duration,
            logger=logger,
        )

        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"X-Request-ID": request_id},
        )


def setup_error_handling(app: FastAPI) -> None:
    """Setup error handling middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add the error handling middleware
    app.middleware("http")(error_handling_middleware)

    logger.info("Error handling middleware configured")


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware to log request details.

    This middleware logs incoming requests with relevant details for monitoring
    and debugging purposes.
    """
    start_time = time.time()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log incoming request
    logger.debug(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    response = await call_next(request)

    duration = time.time() - start_time

    # Log response details
    logger.debug(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_seconds": duration,
        },
    )

    return response


def setup_request_logging(app: FastAPI) -> None:
    """Setup request logging middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.middleware("http")(request_logging_middleware)
    logger.info("Request logging middleware configured")