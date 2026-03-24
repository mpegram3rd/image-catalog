# =============================================================================
# Image Catalog Indexer Module
# =============================================================================
# This module orchestrates the indexing of images for a multimodal search system.
# It processes image files, analyzes them using an LLM to generate descriptions and tags,
# creates thumbnails, and stores both text-based and multimodal embeddings in a Vector DB.
# =============================================================================

import asyncio
import time
from pathlib import Path

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionUserMessageParam, \
    ChatCompletionContentPartImageParam, ChatCompletionContentPartTextParam
from openai.types.chat.chat_completion_content_part_image_param import ImageURL

from ai.client_provider import get_client
from ai.prompt_provider import PromptProvider
from configuration.config import Config
from images.image_handler import encode_image_async, create_thumbnail_as_base64_async
from models.indexing_models import AnalysisResult
from repository.metadata_repository import add_analysis
from repository.multimodal_repository import add_multimodal

load_dotenv()

def extract_json(response) -> str:
    """
    Extracts the raw JSON string from an LLM response.

    The LLM's parse() method returns a structured response, but we need to
    manually extract the JSON content from the message for parsing.

    :param response: The ChatCompletionResponse object from OpenAI
    :return: A cleaned JSON string (stripped of whitespace)

    :raises IndexError: If the response has no choices
    """
    return response.choices[0].message.content.strip()

def map_response(response) -> AnalysisResult:
    """
    Converts the LLM's JSON response into an AnalysisResult Pydantic model.

    This function first extracts the raw JSON from the response, then validates
    and parses it into our AnalysisResult model which contains structured fields
    for the image analysis (description, tags, colors).

    :param response: The ChatCompletionResponse object from OpenAI
    :return: An AnalysisResult instance with parsed data

    :raises ValidationError: If the JSON doesn't match the expected schema
    """
    json_str = extract_json(response)
    return AnalysisResult.model_validate_json(json_str)

async def main() -> None:
    """
    Main entry point for the image indexing process.

    This function orchestrates the complete workflow:
    1. Loads configuration and initializes the LLM client
    2. Retrieves the image analysis prompt from a template file
    3. Iterates through all JPG/PNG images in the base path directory
    4. For each image: encodes it, analyzes with LLM, creates thumbnail, stores embeddings
    5. Reports timing statistics for each processing step

    The indexing process uses a multimodal approach where:
    - Text embeddings are stored for description-based search
    - Multimodal embeddings are stored for visual similarity search

    :return: None (side effects only)
    """

    print("Starting Indexer")
    indexing_time = time.time()
    config = Config()

    client = get_client()
    print(f"Using LLM model (for Image Analysis): {config.llm_model}\n-------\n")
    prompt_provider = PromptProvider('ai/prompts')
    prompt = await prompt_provider.get_prompt_async('image-analysis')

    base_path = Path(config.photos_base_path)
    processed_images = 0
    for p in base_path.rglob("*"):
        if p.is_file() and (p.suffix in ['.jpg', '.png']):
            print(f"Processing {p}...")
            total_processing = time.time()
            processed_images += 1
            timer = time.time()  # Record start time

            image_data = await encode_image_async(p)

            response = client.chat.completions.parse(
                model=config.llm_model,
                response_format=AnalysisResult,
                messages=[
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=[
                            ChatCompletionContentPartTextParam(type="text", text = f"{prompt}"),
                            ChatCompletionContentPartImageParam(type="image_url", image_url = ImageURL(url=f"data:image/jpeg;base64,{image_data}"))
                        ]
                    )
                ]
            )

            results = map_response(response)

            print(f"- Model analysis took {time.time() - timer:.4f} seconds")

            thumbnail = await create_thumbnail_as_base64_async(image_data, config.thumbnail_width, config.thumbnail_height)

            timer = time.time()

            add_analysis(str(p), results, thumbnail)
            add_multimodal(str(p), results, thumbnail)

            print(f"- Embedding and storing took {time.time() - timer:.4f} seconds")
            print(f"- Total Processing Time: {time.time() - total_processing:.4f} seconds\n")
    indexing_end = time.time()
    print(f"Indexing {processed_images} images took {indexing_end - indexing_time:.4f} seconds")

asyncio.run(main())