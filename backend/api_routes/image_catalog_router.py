from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from PIL import Image

from configuration.logging_config import get_logger
from core.dependencies import get_image_service, get_search_service
from core.exceptions import ImageCatalogError, ImageProcessingError, ValidationError
from models.api_models import SearchResult, TextSearchRequest
from services.image_service import ImageService
from services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])
logger = get_logger(__name__)


@router.post("/search/image", response_model=list[SearchResult])
async def search_by_image(
    file: UploadFile,
    threshold: str = "medium",
    max_results: int = 20,
    image_service: Annotated[ImageService, Depends(get_image_service)] = None,
    search_service: Annotated[SearchService, Depends(get_search_service)] = None,
) -> list[SearchResult]:
    """Search for images similar to the uploaded image.

    This endpoint accepts an image file and returns visually similar images from the catalog.
    The search uses multimodal embeddings to find images with similar visual content.

    Args:
        file: PNG or JPEG image file for similarity search
        threshold: Search sensitivity ("small", "medium", "yuge")
        max_results: Maximum number of results to return
        image_service: Image processing service (injected)
        search_service: Search coordination service (injected)

    Returns:
        List of similar images with metadata and thumbnails

    Raises:
        HTTPException: If the image is invalid or search fails
    """
    try:
        logger.info(
            "Image search request received",
            extra={
                "filename": file.filename,
                "content_type": file.content_type,
                "threshold": threshold,
                "max_results": max_results,
            },
        )

        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ValidationError(
                "File must be an image (JPEG, PNG, etc.)",
                field="file",
                value=file.content_type,
            )

        # Read and validate image
        image_data = await file.read()
        if not image_data:
            raise ValidationError(
                "Image file is empty",
                field="file",
                context={"filename": file.filename},
            )

        # Convert to PIL Image for search
        try:
            img = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise ImageProcessingError(
                "Unable to process image file",
                operation="open_image",
                context={"filename": file.filename, "content_type": file.content_type},
            ) from e

        # Perform search
        results = await search_service.search_by_image(
            image=img,
            threshold=threshold,
            max_results=max_results,
        )

        logger.info(
            "Image search completed successfully",
            extra={
                "filename": file.filename,
                "results_count": len(results),
                "threshold": threshold,
            },
        )

        return results

    except ImageCatalogError:
        # Our custom exceptions are handled by middleware
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in image search",
            extra={"filename": file.filename, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/search/text", response_model=list[SearchResult])
async def search_by_text(
    search: TextSearchRequest,
    max_results: int = 20,
    search_service: Annotated[SearchService, Depends(get_search_service)] = None,
) -> list[SearchResult]:
    """Search for images using text descriptions.

    This endpoint searches the image catalog using natural language text. It can use
    either text-only embeddings or multimodal embeddings depending on the search parameters.

    Args:
        search: Search parameters including query text, modality, and threshold
        max_results: Maximum number of results to return
        search_service: Search coordination service (injected)

    Returns:
        List of matching images with metadata and thumbnails

    Raises:
        HTTPException: If the search parameters are invalid or search fails
    """
    try:
        logger.info(
            "Text search request received",
            extra={
                "query": search.search_text,
                "multimodal": search.multimodal,
                "threshold": search.threshold,
                "max_results": max_results,
            },
        )

        # Perform search using the service
        results = await search_service.search_by_text(
            search_request=search,
            max_results=max_results,
        )

        logger.info(
            "Text search completed successfully",
            extra={
                "query": search.search_text,
                "results_count": len(results),
                "multimodal": search.multimodal,
                "threshold": search.threshold,
            },
        )

        return results

    except ImageCatalogError:
        # Our custom exceptions are handled by middleware
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in text search",
            extra={"query": search.search_text, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/search/hybrid", response_model=list[SearchResult])
async def hybrid_search(
    text_query: str,
    file: UploadFile = None,
    text_weight: float = 0.7,
    image_weight: float = 0.3,
    threshold: str = "medium",
    max_results: int = 20,
    search_service: Annotated[SearchService, Depends(get_search_service)] = None,
) -> list[SearchResult]:
    """Perform hybrid search combining text and image queries.

    This endpoint combines text-based and image-based search to find images that match
    both the textual description and visual similarity (if an image is provided).

    Args:
        text_query: Text description to search for
        file: Optional image file for visual similarity
        text_weight: Weight for text search results (0.0-1.0)
        image_weight: Weight for image search results (0.0-1.0)
        threshold: Search sensitivity ("small", "medium", "yuge")
        max_results: Maximum number of results to return
        search_service: Search coordination service (injected)

    Returns:
        List of matching images ranked by combined similarity

    Raises:
        HTTPException: If parameters are invalid or search fails
    """
    try:
        logger.info(
            "Hybrid search request received",
            extra={
                "text_query": text_query,
                "has_image": file is not None,
                "text_weight": text_weight,
                "image_weight": image_weight,
                "threshold": threshold,
                "max_results": max_results,
            },
        )

        # Process image if provided
        image = None
        if file:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise ValidationError(
                    "File must be an image (JPEG, PNG, etc.)",
                    field="file",
                    value=file.content_type,
                )

            image_data = await file.read()
            if image_data:
                try:
                    image = Image.open(io.BytesIO(image_data))
                except Exception as e:
                    raise ImageProcessingError(
                        "Unable to process image file",
                        operation="open_image",
                        context={"filename": file.filename},
                    ) from e

        # Perform hybrid search
        results = await search_service.hybrid_search(
            text_query=text_query,
            image=image,
            text_weight=text_weight,
            image_weight=image_weight,
            threshold=threshold,
            max_results=max_results,
        )

        logger.info(
            "Hybrid search completed successfully",
            extra={
                "text_query": text_query,
                "results_count": len(results),
                "has_image": image is not None,
            },
        )

        return results

    except ImageCatalogError:
        # Our custom exceptions are handled by middleware
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in hybrid search",
            extra={"text_query": text_query, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring service availability.

    Returns:
        Service health status and component information
    """
    from core.dependencies import check_service_health

    health_status = await check_service_health()

    # Return appropriate HTTP status based on health
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    elif health_status["status"] == "degraded":
        # Return 200 but indicate degraded status
        return {"status": "degraded", "details": health_status}
    else:
        return health_status
