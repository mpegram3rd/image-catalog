import base64

import aiofiles


async def encode_image_async(image_path):
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            return base64.b64encode(await image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: Could not process image at: '{image_path}'.")
        raise
