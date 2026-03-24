"""Search service for coordinating image search operations."""

import time
from typing import Optional

from PIL import Image

from configuration.logging_config import get_logger, log_performance
from core.exceptions import SearchError, ValidationError
from models.api_models import SearchResult, TextSearchRequest
from repository.filtering_thresholds import VALID_THRESHOLDS

logger = get_logger(__name__)


class SearchService:
    """Service for coordinating search operations.

    This service provides a unified interface for different types of searches
    and handles the coordination between various search repositories.
    """

    def __init__(
        self,
        metadata_repository=None,
        multimodal_repository=None,
        default_threshold: str = "medium",
    ):
        """Initialize the search service.

        Args:
            metadata_repository: Repository for text-based searches
            multimodal_repository: Repository for multimodal searches
            default_threshold: Default search threshold
        """
        self.metadata_repository = metadata_repository
        self.multimodal_repository = multimodal_repository
        self.default_threshold = default_threshold

    async def search_by_text(
        self,
        search_request: TextSearchRequest,
        max_results: Optional[int] = None,
    ) -> list[SearchResult]:
        """Perform text-based search for images.

        Args:
            search_request: Search parameters
            max_results: Maximum number of results to return

        Returns:
            List of search results

        Raises:
            ValidationError: If search parameters are invalid
            SearchError: If search operation fails
        """
        start_time = time.time()

        # Validate search request
        self._validate_text_search_request(search_request)

        try:
            # Get threshold value
            threshold_value = VALID_THRESHOLDS[search_request.threshold]

            logger.debug(
                "Starting text search",
                extra={
                    "query": search_request.search_text,
                    "multimodal": search_request.multimodal,
                    "threshold": search_request.threshold,
                    "threshold_value": threshold_value,
                },
            )

            # Choose repository based on multimodal flag
            if search_request.multimodal and self.multimodal_repository:
                # Import here to avoid circular imports
                from repository.multimodal_repository import find_by_text_mm

                results = find_by_text_mm(search_request.search_text, threshold_value)
                search_type = "multimodal_text"
            else:
                if not self.metadata_repository:
                    # Fallback import
                    from repository.metadata_repository import find_by_text

                    results = find_by_text(search_request.search_text, threshold_value)
                else:
                    results = self.metadata_repository.find_by_text(
                        search_request.search_text, threshold_value
                    )
                search_type = "text"

            # Apply result limit if specified
            if max_results and len(results) > max_results:
                results = results[:max_results]

            search_time = time.time() - start_time
            log_performance(f"search_{search_type}", search_time, logger)

            logger.info(
                "Text search completed",
                extra={
                    "query": search_request.search_text,
                    "search_type": search_type,
                    "results_count": len(results),
                    "search_time_seconds": search_time,
                    "threshold": search_request.threshold,
                },
            )

            return results

        except Exception as e:
            search_time = time.time() - start_time
            logger.error(
                "Text search failed",
                extra={
                    "query": search_request.search_text,
                    "search_time_seconds": search_time,
                    "error": str(e),
                },
            )
            raise SearchError(
                "Text search operation failed",
                search_query=search_request.search_text,
                search_type="text",
                context={
                    "multimodal": search_request.multimodal,
                    "threshold": search_request.threshold,
                },
            ) from e

    async def search_by_image(
        self,
        image: Image.Image,
        threshold: str = None,
        max_results: Optional[int] = None,
    ) -> list[SearchResult]:
        """Perform image-based search.

        Args:
            image: PIL Image object to search with
            threshold: Search threshold (uses default if None)
            max_results: Maximum number of results to return

        Returns:
            List of search results

        Raises:
            ValidationError: If image is invalid
            SearchError: If search operation fails
        """
        start_time = time.time()
        threshold = threshold or self.default_threshold

        # Validate inputs
        if not image:
            raise ValidationError(
                "Image is required for image search",
                field="image",
                context={"search_type": "image"},
            )

        if threshold not in VALID_THRESHOLDS:
            raise ValidationError(
                f"Invalid threshold: {threshold}",
                field="threshold",
                value=threshold,
                context={"valid_thresholds": list(VALID_THRESHOLDS.keys())},
            )

        try:
            threshold_value = VALID_THRESHOLDS[threshold]

            logger.debug(
                "Starting image search",
                extra={
                    "image_size": image.size,
                    "image_format": image.format,
                    "threshold": threshold,
                    "threshold_value": threshold_value,
                },
            )

            # Perform multimodal search
            if not self.multimodal_repository:
                # Fallback import
                from repository.multimodal_repository import find_by_image

                results = find_by_image(image, threshold_value)
            else:
                results = self.multimodal_repository.find_by_image(image, threshold_value)

            # Apply result limit if specified
            if max_results and len(results) > max_results:
                results = results[:max_results]

            search_time = time.time() - start_time
            log_performance("search_image", search_time, logger)

            logger.info(
                "Image search completed",
                extra={
                    "image_size": image.size,
                    "results_count": len(results),
                    "search_time_seconds": search_time,
                    "threshold": threshold,
                },
            )

            return results

        except Exception as e:
            search_time = time.time() - start_time
            logger.error(
                "Image search failed",
                extra={
                    "image_size": image.size if image else None,
                    "search_time_seconds": search_time,
                    "error": str(e),
                },
            )
            raise SearchError(
                "Image search operation failed",
                search_type="image",
                context={
                    "threshold": threshold,
                    "image_size": image.size if image else None,
                },
            ) from e

    async def hybrid_search(
        self,
        text_query: str,
        image: Optional[Image.Image] = None,
        text_weight: float = 0.7,
        image_weight: float = 0.3,
        threshold: str = None,
        max_results: Optional[int] = None,
    ) -> list[SearchResult]:
        """Perform hybrid search combining text and image queries.

        Args:
            text_query: Text search query
            image: Optional image for visual similarity
            text_weight: Weight for text search results (0.0-1.0)
            image_weight: Weight for image search results (0.0-1.0)
            threshold: Search threshold
            max_results: Maximum number of results

        Returns:
            Combined and weighted search results

        Raises:
            ValidationError: If parameters are invalid
            SearchError: If search fails
        """
        threshold = threshold or self.default_threshold

        # Validate weights
        if not (0.0 <= text_weight <= 1.0) or not (0.0 <= image_weight <= 1.0):
            raise ValidationError(
                "Search weights must be between 0.0 and 1.0",
                field="weights",
                value={"text_weight": text_weight, "image_weight": image_weight},
            )

        if abs(text_weight + image_weight - 1.0) > 0.001:
            raise ValidationError(
                "Search weights must sum to 1.0",
                field="weights",
                value={"text_weight": text_weight, "image_weight": image_weight},
            )

        start_time = time.time()
        logger.info(
            "Starting hybrid search",
            extra={
                "text_query": text_query,
                "has_image": image is not None,
                "text_weight": text_weight,
                "image_weight": image_weight,
            },
        )

        try:
            results = {}  # Dictionary to combine results by image_path

            # Perform text search if weight > 0
            if text_weight > 0:
                text_request = TextSearchRequest(
                    search_text=text_query,
                    multimodal=True,  # Use multimodal for better hybrid results
                    threshold=threshold,
                )
                text_results = await self.search_by_text(text_request, max_results)

                for result in text_results:
                    # Weight the distance by text weight
                    weighted_distance = result.distance * text_weight
                    results[result.image_path] = {
                        "result": result,
                        "distance": weighted_distance,
                        "sources": ["text"],
                    }

            # Perform image search if weight > 0 and image provided
            if image_weight > 0 and image:
                image_results = await self.search_by_image(image, threshold, max_results)

                for result in image_results:
                    weighted_distance = result.distance * image_weight
                    key = result.image_path

                    if key in results:
                        # Combine distances from both searches
                        results[key]["distance"] += weighted_distance
                        results[key]["sources"].append("image")
                    else:
                        results[key] = {
                            "result": result,
                            "distance": weighted_distance,
                            "sources": ["image"],
                        }

            # Sort by combined distance and create final results
            sorted_results = sorted(results.values(), key=lambda x: x["distance"])

            final_results = []
            for item in sorted_results:
                result = item["result"]
                # Update the distance with the combined score
                result.distance = item["distance"]
                final_results.append(result)

            # Apply result limit
            if max_results:
                final_results = final_results[:max_results]

            search_time = time.time() - start_time
            log_performance("search_hybrid", search_time, logger)

            logger.info(
                "Hybrid search completed",
                extra={
                    "text_query": text_query,
                    "results_count": len(final_results),
                    "search_time_seconds": search_time,
                    "combined_sources": len([r for r in results.values() if len(r["sources"]) > 1]),
                },
            )

            return final_results

        except Exception as e:
            search_time = time.time() - start_time
            logger.error(
                "Hybrid search failed",
                extra={
                    "text_query": text_query,
                    "search_time_seconds": search_time,
                    "error": str(e),
                },
            )
            raise SearchError(
                "Hybrid search operation failed",
                search_query=text_query,
                search_type="hybrid",
                context={
                    "text_weight": text_weight,
                    "image_weight": image_weight,
                    "has_image": image is not None,
                },
            ) from e

    def _validate_text_search_request(self, search_request: TextSearchRequest) -> None:
        """Validate text search request parameters.

        Args:
            search_request: Request to validate

        Raises:
            ValidationError: If validation fails
        """
        if not search_request.search_text or not search_request.search_text.strip():
            raise ValidationError(
                "Search text cannot be empty",
                field="search_text",
                value=search_request.search_text,
            )

        if search_request.threshold not in VALID_THRESHOLDS:
            raise ValidationError(
                f"Invalid threshold: {search_request.threshold}",
                field="threshold",
                value=search_request.threshold,
                context={"valid_thresholds": list(VALID_THRESHOLDS.keys())},
            )

        # Check for potentially problematic queries
        if len(search_request.search_text) > 500:
            raise ValidationError(
                "Search text is too long",
                field="search_text",
                value=len(search_request.search_text),
                context={"max_length": 500},
            )

    def get_search_stats(self) -> dict:
        """Get search service statistics.

        Returns:
            Dictionary with service statistics
        """
        return {
            "supported_thresholds": list(VALID_THRESHOLDS.keys()),
            "default_threshold": self.default_threshold,
            "has_metadata_repository": self.metadata_repository is not None,
            "has_multimodal_repository": self.multimodal_repository is not None,
        }
