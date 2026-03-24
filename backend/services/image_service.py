"""Image processing service for handling image-related operations."""

import io
import time
from pathlib import Path
from typing import Optional

from PIL import Image

from configuration.logging_config import get_logger, log_performance
from core.exceptions import ImageProcessingError, NotFoundError, ValidationError
from images.image_handler import create_thumbnail_as_base64_async, encode_image_async

logger = get_logger(__name__)


class ImageService:
    """Service for image processing operations.

    This service encapsulates image processing logic and provides a clean
    interface for handling images throughout the application.
    """

    def __init__(self, thumbnail_width: int = 200, thumbnail_height: int = 200):
        """Initialize the image service.

        Args:
            thumbnail_width: Default width for thumbnails
            thumbnail_height: Default height for thumbnails
        """
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.supported_formats = {".jpg", ".jpeg", ".png"}

    async def process_image_file(self, image_path: str) -> tuple[str, str]:
        """Process an image file and create its thumbnail.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (base64_image_data, base64_thumbnail)

        Raises:
            NotFoundError: If image file doesn't exist
            ImageProcessingError: If image processing fails
            ValidationError: If image format is not supported
        """
        start_time = time.time()

        # Validate file exists and format
        file_path = Path(image_path)
        if not file_path.exists():
            raise NotFoundError(
                f"Image file not found: {image_path}",
                resource_type="image_file",
                resource_id=image_path,
            )

        if file_path.suffix.lower() not in self.supported_formats:
            raise ValidationError(
                f"Unsupported image format: {file_path.suffix}",
                field="image_format",
                value=file_path.suffix,
                context={
                    "supported_formats": list(self.supported_formats),
                    "image_path": image_path,
                },
            )

        try:
            logger.debug("Processing image file", extra={"image_path": image_path})

            # Encode original image
            base64_data = await encode_image_async(image_path)

            # Create thumbnail
            thumbnail = await create_thumbnail_as_base64_async(
                base64_data, self.thumbnail_width, self.thumbnail_height
            )

            processing_time = time.time() - start_time
            log_performance("image_processing_complete", processing_time, logger)

            logger.info(
                "Image processed successfully",
                extra={
                    "image_path": image_path,
                    "processing_time_seconds": processing_time,
                    "original_size_kb": len(base64_data) / 1024,
                    "thumbnail_size_kb": len(thumbnail) / 1024,
                },
            )

            return base64_data, thumbnail

        except (ImageProcessingError, NotFoundError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during image processing",
                extra={"image_path": image_path, "error": str(e)},
            )
            raise ImageProcessingError(
                f"Failed to process image: {image_path}",
                image_path=image_path,
                operation="process_file",
            ) from e

    async def create_thumbnail_from_upload(
        self, image_data: bytes, width: Optional[int] = None, height: Optional[int] = None
    ) -> str:
        """Create a thumbnail from uploaded image data.

        Args:
            image_data: Raw image bytes
            width: Thumbnail width (uses default if None)
            height: Thumbnail height (uses default if None)

        Returns:
            Base64 encoded thumbnail with data URI prefix

        Raises:
            ValidationError: If image data is invalid
            ImageProcessingError: If thumbnail creation fails
        """
        if not image_data:
            raise ValidationError(
                "Image data is empty",
                field="image_data",
                context={"size": len(image_data) if image_data else 0},
            )

        thumb_width = width or self.thumbnail_width
        thumb_height = height or self.thumbnail_height

        try:
            # Validate the image by trying to open it
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # Check if the image is corrupt

            # Re-open for processing (verify() closes the image)
            image = Image.open(io.BytesIO(image_data))

            logger.debug(
                "Creating thumbnail from upload",
                extra={
                    "original_size": image.size,
                    "target_size": (thumb_width, thumb_height),
                    "format": image.format,
                },
            )

            # Convert to base64 and create thumbnail
            import base64

            base64_data = base64.b64encode(image_data).decode("utf-8")

            thumbnail = await create_thumbnail_as_base64_async(
                base64_data, thumb_width, thumb_height
            )

            return thumbnail

        except Exception as e:
            logger.error("Failed to create thumbnail from upload", extra={"error": str(e)})
            raise ImageProcessingError(
                "Failed to create thumbnail from uploaded image",
                operation="create_thumbnail_from_upload",
                context={"data_size": len(image_data)},
            ) from e

    def validate_image_dimensions(
        self, width: int, height: int, max_width: int = 8000, max_height: int = 8000
    ) -> bool:
        """Validate image dimensions.

        Args:
            width: Image width
            height: Image height
            max_width: Maximum allowed width
            max_height: Maximum allowed height

        Returns:
            True if dimensions are valid

        Raises:
            ValidationError: If dimensions are invalid
        """
        if width <= 0 or height <= 0:
            raise ValidationError(
                f"Invalid image dimensions: {width}x{height}",
                field="image_dimensions",
                value=f"{width}x{height}",
                context={"width": width, "height": height},
            )

        if width > max_width or height > max_height:
            raise ValidationError(
                f"Image too large: {width}x{height} (max: {max_width}x{max_height})",
                field="image_dimensions",
                value=f"{width}x{height}",
                context={
                    "width": width,
                    "height": height,
                    "max_width": max_width,
                    "max_height": max_height,
                },
            )

        return True

    def get_supported_formats(self) -> list[str]:
        """Get list of supported image formats.

        Returns:
            List of supported file extensions
        """
        return list(self.supported_formats)

    async def batch_process_images(
        self, image_paths: list[str], max_concurrent: int = 5
    ) -> list[tuple[str, str, str]]:
        """Process multiple images concurrently.

        Args:
            image_paths: List of image file paths
            max_concurrent: Maximum number of concurrent operations

        Returns:
            List of tuples (image_path, base64_data, thumbnail)

        Note:
            This method processes images in batches to avoid overwhelming the system.
            Failed images are logged but don't stop the entire batch.
        """
        import asyncio
        from asyncio import Semaphore

        semaphore = Semaphore(max_concurrent)
        results = []

        async def process_single(path: str) -> Optional[tuple[str, str, str]]:
            async with semaphore:
                try:
                    base64_data, thumbnail = await self.process_image_file(path)
                    return (path, base64_data, thumbnail)
                except Exception as e:
                    logger.warning(
                        "Failed to process image in batch",
                        extra={"image_path": path, "error": str(e)},
                    )
                    return None

        logger.info(
            "Starting batch image processing",
            extra={
                "total_images": len(image_paths),
                "max_concurrent": max_concurrent,
            },
        )

        start_time = time.time()
        tasks = [process_single(path) for path in image_paths]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed results
        for result in batch_results:
            if result and not isinstance(result, Exception):
                results.append(result)

        processing_time = time.time() - start_time
        success_count = len(results)
        failure_count = len(image_paths) - success_count

        logger.info(
            "Batch processing completed",
            extra={
                "total_images": len(image_paths),
                "successful": success_count,
                "failed": failure_count,
                "processing_time_seconds": processing_time,
            },
        )

        return results
