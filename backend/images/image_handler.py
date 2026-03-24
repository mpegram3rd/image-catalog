import base64
import io
import time
from typing import Final

import aiofiles
from PIL import Image

from configuration.logging_config import get_logger, log_performance
from core.exceptions import ImageProcessingError, NotFoundError
from core.retry import IMAGE_PROCESSING_RETRY, retry_on_failure

BASE64_PNG_PREFIX: Final = "data:image/png;base64,"
logger = get_logger(__name__)


@retry_on_failure(IMAGE_PROCESSING_RETRY, "encode_image")
async def encode_image_async(image_path: str) -> str:
    """Encode an image file to base64 string.

    Args:
        image_path: Path to the image file

    Returns:
        Base64 encoded image data

    Raises:
        NotFoundError: If the image file is not found
        ImageProcessingError: If the image cannot be processed
    """
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            return base64.b64encode(await image_file.read()).decode("utf-8")
    except FileNotFoundError as e:
        logger.error("Image file not found", extra={"image_path": image_path})
        raise NotFoundError(
            f"Image file not found: {image_path}",
            resource_type="image",
            resource_id=image_path,
        ) from e
    except OSError as e:
        logger.error("Failed to read image file", extra={"image_path": image_path, "error": str(e)})
        raise ImageProcessingError(
            f"Failed to read image file: {image_path}",
            image_path=image_path,
            operation="encode",
        ) from e


@retry_on_failure(IMAGE_PROCESSING_RETRY, "create_thumbnail")
async def create_thumbnail_as_base64_async(
    image_base64: str, thumbnail_width: int, thumbnail_height: int
) -> str:
    """Create a thumbnail from base64 image data.

    Args:
        image_base64: Base64 encoded image data
        thumbnail_width: Maximum width for the thumbnail
        thumbnail_height: Maximum height for the thumbnail

    Returns:
        Base64 encoded thumbnail with data URI prefix

    Raises:
        ImageProcessingError: If thumbnail creation fails
        ValidationError: If input parameters are invalid
    """
    if not image_base64:
        raise ImageProcessingError(
            "Image data is empty",
            operation="create_thumbnail",
            context={"reason": "empty_base64_data"},
        )

    if thumbnail_width <= 0 or thumbnail_height <= 0:
        raise ImageProcessingError(
            f"Invalid thumbnail dimensions: {thumbnail_width}x{thumbnail_height}",
            operation="create_thumbnail",
            context={"width": thumbnail_width, "height": thumbnail_height},
        )

    thumbnail_time = time.time()
    try:
        # Decode the base64 string
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            raise ImageProcessingError(
                "Failed to decode base64 image data",
                operation="create_thumbnail",
                context={"reason": "invalid_base64"},
            ) from e

        # Convert to a PIL image
        try:
            thumbnail_image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise ImageProcessingError(
                "Failed to open image from decoded data",
                operation="create_thumbnail",
                context={"reason": "invalid_image_data"},
            ) from e

        # Calculate aspect ratio and dimensions
        width, height = thumbnail_image.size
        aspect_ratio = width / float(height)

        # Determine thumbnail dimensions based on aspect ratio
        if thumbnail_width / float(thumbnail_height) > aspect_ratio:
            # Width is the constraining dimension
            new_width = thumbnail_width
            new_height = int(thumbnail_width / aspect_ratio)
        else:
            # Height is the constraining dimension
            new_height = thumbnail_height
            new_width = int(thumbnail_height * aspect_ratio)

        # Resize the image
        thumbnail_image.thumbnail((new_width, new_height))

        # Convert to PNG in memory
        png_buffer = io.BytesIO()
        try:
            thumbnail_image.save(png_buffer, format="PNG", quality=80)
        except Exception as e:
            raise ImageProcessingError(
                "Failed to save thumbnail to PNG format",
                operation="create_thumbnail",
                context={"format": "PNG"},
            ) from e

        b64_thumbnail = BASE64_PNG_PREFIX + base64.b64encode(png_buffer.getvalue()).decode("utf-8")

        execution_time = time.time() - thumbnail_time
        log_performance("thumbnail_generation", execution_time, logger)

        return b64_thumbnail

    except ImageProcessingError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error("Unexpected error during thumbnail generation", extra={"error": str(e)})
        raise ImageProcessingError(
            "Unexpected error during thumbnail generation",
            operation="create_thumbnail",
            context={"error_type": type(e).__name__},
        ) from e
