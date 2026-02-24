import base64
import io
import time
from typing import Final

import aiofiles
from PIL import Image

from configuration.logging_config import get_logger, log_performance

BASE64_PNG_PREFIX: Final = "data:image/png;base64,"
logger = get_logger(__name__)


async def encode_image_async(image_path: str) -> str:
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            return base64.b64encode(await image_file.read()).decode("utf-8")
    except FileNotFoundError:
        logger.error("Could not process image", extra={"image_path": image_path})
        raise


async def create_thumbnail_as_base64_async(
    image_base64: str, thumbnail_width: int, thumbnail_height: int
) -> str | None:
    thumbnail_time = time.time()
    try:
        # Decode the base64 string
        image_data = base64.b64decode(image_base64)

        # Now convert to a PIL image
        thumbnail_image = Image.open(io.BytesIO(image_data))

        # figure out the aspect ratio
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

        # Convert to a JPEG with 80% quality in memory
        jpeg_buffer = io.BytesIO()
        thumbnail_image.save(jpeg_buffer, format="PNG", quality=80)
        b64_thumbnail = BASE64_PNG_PREFIX + base64.b64encode(jpeg_buffer.getvalue()).decode("utf-8")

        execution_time = time.time() - thumbnail_time
        log_performance("thumbnail_generation", execution_time, logger)

        return b64_thumbnail

    except Exception as e:
        logger.error("Unexpected error during thumbnail generation", extra={"error": str(e)})
        raise
