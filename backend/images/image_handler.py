import base64
import io
import time
from typing import Final

import aiofiles
from PIL import Image
BASE64_PNG_PREFIX :Final = "data:image/png;base64,"

async def encode_image_async(image_path: str) -> str:
    """
    Asynchronously reads an image file from disk and returns its base64-encoded representation.

    :param image_path: The absolute or relative path to the image file on disk (e.g., '/path/to/image.png').
    :return: A base64-encoded string representing the image data.
    :raises FileNotFoundError: If the specified image file does not exist on disk.
    """
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            return base64.b64encode(await image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: Could not process image at: '{image_path}'.")
        raise

async def create_thumbnail_as_base64_async(image_base64:str, thumbnail_width: int, thumbnail_height: int) -> str | None:
    """
    Creates a resized thumbnail from a base64-encoded image and returns the thumbnail as a base64 string.

    This function decodes the provided base64 image, resizes it to fit within the specified
    thumbnail dimensions while maintaining aspect ratio (using a "fit" strategy), and re-encodes
    it as base64. The thumbnail is converted to PNG format.

    :param image_base64: A base64-encoded string of the original image data.
    :param thumbnail_width: The maximum width for the thumbnail in pixels.
    :param thumbnail_height: The maximum height for the thumbnail in pixels.
    :return: A base64-encoded string of the resized thumbnail with a PNG data URI prefix.
             Returns None if an error occurs during processing (though the function will still raise).

    :raises Exception: If any unexpected error occurs during image processing (e.g., invalid base64,
                      unsupported image format).

    """
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

        finish_time = time.time()
        execution_time = finish_time - thumbnail_time
        print(f"- Thumbnail generation took took {execution_time:.4f} seconds")

        return b64_thumbnail

    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # Catch other potential errors
        raise

