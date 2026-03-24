"""Dependency injection providers for FastAPI.

This module provides dependency injection functions that create and configure
services and repositories for use in FastAPI endpoints and other components.
"""

from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from configuration.config import Config
from configuration.logging_config import get_logger
from services.image_service import ImageService
from services.indexing_service import IndexingService
from services.search_service import SearchService

logger = get_logger(__name__)


@lru_cache
def get_config() -> Config:
    """Get application configuration.

    This function is cached to ensure we use the same configuration
    instance throughout the application lifecycle.

    Returns:
        Application configuration instance
    """
    return Config()


def get_image_service(config: Annotated[Config, Depends(get_config)]) -> ImageService:
    """Get image processing service.

    Args:
        config: Application configuration

    Returns:
        Configured image service instance
    """
    return ImageService(
        thumbnail_width=config.thumbnail_width,
        thumbnail_height=config.thumbnail_height,
    )


def get_search_service() -> SearchService:
    """Get search service.

    Returns:
        Configured search service instance

    Note:
        This service uses late binding to repositories to avoid circular imports.
        The repositories are imported when needed within the service methods.
    """
    return SearchService(
        # Repositories are injected via late binding within the service
        default_threshold="medium",
    )


async def get_indexing_service(
    config: Annotated[Config, Depends(get_config)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> Generator[IndexingService, None, None]:
    """Get indexing service with proper initialization and cleanup.

    Args:
        config: Application configuration
        image_service: Image processing service

    Yields:
        Initialized indexing service

    Note:
        This is an async generator dependency that ensures proper
        initialization and cleanup of the indexing service.
    """
    logger.debug("Creating indexing service")

    service = IndexingService(
        config=config,
        image_service=image_service,
        # Repositories use late binding to avoid circular imports
    )

    try:
        await service.initialize()
        logger.debug("Indexing service initialized successfully")
        yield service
    except Exception as e:
        logger.error("Failed to initialize indexing service", extra={"error": str(e)})
        raise
    finally:
        # Cleanup if needed
        logger.debug("Indexing service dependency cleanup completed")


# Repository dependency providers
# These use late imports to avoid circular dependencies during module loading


def get_metadata_repository():
    """Get metadata repository instance.

    Returns:
        Metadata repository for text-based searches

    Note:
        Uses late import to avoid circular dependencies.
    """
    try:
        # Late import to avoid circular dependency
        import repository.metadata_repository as meta_repo

        return meta_repo
    except Exception as e:
        logger.error("Failed to import metadata repository", extra={"error": str(e)})
        raise


def get_multimodal_repository():
    """Get multimodal repository instance.

    Returns:
        Multimodal repository for image and multimodal searches

    Note:
        Uses late import to avoid circular dependencies.
    """
    try:
        # Late import to avoid circular dependency
        import repository.multimodal_repository as mm_repo

        return mm_repo
    except Exception as e:
        logger.error("Failed to import multimodal repository", extra={"error": str(e)})
        raise


# Health check dependencies


async def check_service_health() -> dict:
    """Check the health of all services.

    Returns:
        Dictionary with health status of all components

    Note:
        This is useful for health check endpoints.
    """
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": None,
    }

    try:
        import time

        health_status["timestamp"] = time.time()

        # Check configuration
        try:
            config = get_config()
            # Run configuration validation
            warnings = config.validate_configuration()
            health_status["services"]["config"] = {
                "status": "healthy",
                "environment": config.environment.value,
                "llm_model": config.llm_model,
                "llm_provider": config.llm_provider.value,
                "warnings": warnings,
            }
            if warnings:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["config"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check image service
        try:
            image_service = get_image_service(config)
            health_status["services"]["image_service"] = {
                "status": "healthy",
                "supported_formats": image_service.get_supported_formats(),
            }
        except Exception as e:
            health_status["services"]["image_service"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check search service
        try:
            search_service = get_search_service()
            health_status["services"]["search_service"] = {
                "status": "healthy",
                "stats": search_service.get_search_stats(),
            }
        except Exception as e:
            health_status["services"]["search_service"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check repositories
        try:
            get_metadata_repository()
            health_status["services"]["metadata_repository"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["metadata_repository"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        try:
            get_multimodal_repository()
            health_status["services"]["multimodal_repository"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["multimodal_repository"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check if AI client can be created
        try:
            from ai.client_provider import get_client

            get_client()
            health_status["services"]["ai_client"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["ai_client"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

    except Exception as e:
        logger.error("Health check failed", extra={"error": str(e)})
        health_status = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time(),
        }

    logger.debug("Health check completed", extra={"status": health_status["status"]})
    return health_status


# Utility dependencies for common patterns


def get_request_context() -> dict:
    """Get request context information.

    Returns:
        Dictionary with request context (can be extended)

    Note:
        This can be enhanced to include request ID, user info, etc.
    """
    import time

    return {
        "timestamp": time.time(),
        "request_id": None,  # Can be populated from middleware
    }


# Factory functions for testing and advanced configurations


def create_image_service(
    thumbnail_width: int = 200,
    thumbnail_height: int = 200,
) -> ImageService:
    """Create image service with custom configuration.

    Args:
        thumbnail_width: Custom thumbnail width
        thumbnail_height: Custom thumbnail height

    Returns:
        Configured image service

    Note:
        This function is useful for testing and custom configurations.
    """
    return ImageService(
        thumbnail_width=thumbnail_width,
        thumbnail_height=thumbnail_height,
    )


def create_search_service(
    default_threshold: str = "medium",
    metadata_repository=None,
    multimodal_repository=None,
) -> SearchService:
    """Create search service with custom configuration.

    Args:
        default_threshold: Default search threshold
        metadata_repository: Optional metadata repository
        multimodal_repository: Optional multimodal repository

    Returns:
        Configured search service

    Note:
        This function is useful for testing and custom configurations.
    """
    return SearchService(
        default_threshold=default_threshold,
        metadata_repository=metadata_repository,
        multimodal_repository=multimodal_repository,
    )


async def create_indexing_service(
    config: Config,
    image_service: ImageService = None,
    metadata_repository=None,
    multimodal_repository=None,
) -> IndexingService:
    """Create and initialize indexing service with custom configuration.

    Args:
        config: Application configuration
        image_service: Optional image service
        metadata_repository: Optional metadata repository
        multimodal_repository: Optional multimodal repository

    Returns:
        Initialized indexing service

    Note:
        This function is useful for testing and custom configurations.
    """
    service = IndexingService(
        config=config,
        image_service=image_service,
        metadata_repository=metadata_repository,
        multimodal_repository=multimodal_repository,
    )

    await service.initialize()
    return service
