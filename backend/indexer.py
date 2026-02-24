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
from configuration.logging_config import setup_logging, get_logger, log_performance
from images.image_handler import encode_image_async, create_thumbnail_as_base64_async
from models.indexing_models import AnalysisResult
from repository.metadata_repository import add_analysis
from repository.multimodal_repository import add_multimodal

load_dotenv()
logger = get_logger(__name__)

def extract_json(response) -> str:
    return response.choices[0].message.content.strip()

def map_response(response) -> AnalysisResult:
    json_str = extract_json(response)
    return AnalysisResult.model_validate_json(json_str)

async def main() -> None:
    config = Config()

    # Setup logging
    setup_logging(
        level=config.log_level,
        json_format=config.log_json_format,
        log_file=config.log_file,
    )

    logger.info("Starting Image Indexer")
    indexing_time = time.time()

    client = get_client()
    logger.info("Initialized LLM client", extra={
        "llm_model": config.llm_model,
        "llm_provider": config.llm_provider,
    })

    prompt_provider = PromptProvider('ai/prompts')
    prompt = await prompt_provider.get_prompt_async('image-analysis')

    base_path = Path(config.photos_base_path)
    logger.info("Starting image processing", extra={"base_path": str(base_path)})

    processed_images = 0
    for p in base_path.rglob("*"):
        if p.is_file() and (p.suffix in ['.jpg', '.png']):
            logger.info("Processing image", extra={"file_path": str(p)})
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
            analysis_duration = time.time() - timer
            log_performance("llm_analysis", analysis_duration, logger)

            thumbnail = await create_thumbnail_as_base64_async(image_data, config.thumbnail_width, config.thumbnail_height)

            timer = time.time()

            add_analysis(str(p), results, thumbnail)
            add_multimodal(str(p), results, thumbnail)

            storage_duration = time.time() - timer
            total_duration = time.time() - total_processing

            log_performance("embedding_and_storage", storage_duration, logger)
            log_performance("total_image_processing", total_duration, logger)

    indexing_duration = time.time() - indexing_time
    logger.info("Indexing completed", extra={
        "processed_images": processed_images,
        "total_duration_seconds": indexing_duration,
    })

asyncio.run(main())