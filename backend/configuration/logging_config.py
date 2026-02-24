"""Centralized logging configuration for the image-catalog backend."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format for structured logging
        log_file: Optional log file path. If None, logs only to console
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory if using file logging
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    config = _get_logging_config(log_level, json_format, log_file)
    logging.config.dictConfig(config)

    # Set up uvicorn logger to use our configuration
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def _get_logging_config(
    log_level: int,
    json_format: bool,
    log_file: str | None,
) -> Dict[str, Any]:
    """Generate logging configuration dictionary.

    Args:
        log_level: Logging level
        json_format: Whether to use JSON formatting
        log_file: Optional log file path

    Returns:
        Logging configuration dictionary
    """
    formatters = {
        "standard": {
            "format": "%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    if json_format:
        formatters["json"] = {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "standard",
            "stream": sys.stdout,
        },
    }

    if log_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed" if not json_format else "json",
            "filename": log_file,
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
        }

    loggers = {
        # Application loggers
        "configuration": {"level": log_level, "propagate": False},
        "models": {"level": log_level, "propagate": False},
        "repository": {"level": log_level, "propagate": False},
        "ai": {"level": log_level, "propagate": False},
        "images": {"level": log_level, "propagate": False},
        "api_routes": {"level": log_level, "propagate": False},
        "mcp_tools": {"level": log_level, "propagate": False},
        "indexer": {"level": log_level, "propagate": False},
        "server": {"level": log_level, "propagate": False},

        # Third-party loggers
        "uvicorn": {"level": "INFO", "propagate": False},
        "uvicorn.access": {"level": "WARNING", "propagate": False},
        "fastapi": {"level": "INFO", "propagate": False},
        "openai": {"level": "WARNING", "propagate": False},
        "httpx": {"level": "WARNING", "propagate": False},
        "chromadb": {"level": "WARNING", "propagate": False},
    }

    # Set handlers for all loggers
    handler_list = ["console"]
    if log_file:
        handler_list.append("file")

    for logger_config in loggers.values():
        logger_config["handlers"] = handler_list

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
        "root": {
            "level": log_level,
            "handlers": handler_list,
        },
    }


class LoggerMixin:
    """Mixin class to add logging capability to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__module__)


# Performance logging utilities
def log_performance(func_name: str, duration: float, logger: logging.Logger) -> None:
    """Log performance metrics for a function.

    Args:
        func_name: Name of the function being measured
        duration: Execution duration in seconds
        logger: Logger instance to use
    """
    logger.info("Performance", extra={
        "function": func_name,
        "duration_seconds": duration,
        "duration_ms": duration * 1000,
    })


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    logger: logging.Logger,
) -> None:
    """Log API request details.

    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration: Request duration in seconds
        logger: Logger instance to use
    """
    logger.info("API Request", extra={
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_seconds": duration,
    })