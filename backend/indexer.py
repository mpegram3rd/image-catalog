import asyncio
from pathlib import Path
import time

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionUserMessageParam, \
    ChatCompletionContentPartImageParam, ChatCompletionContentPartTextParam
from openai.types.chat.chat_completion_content_part_image_param import ImageURL

from ai.client_provider import get_client
from configuration.config import Config
from images.image_handler import encode_image_async, create_thumbnail_as_base64_async
from repository.metadata_repository import list_contents, add_analysis
from models.models import AnalysisResult
from ai.prompt_provider import PromptProvider
from repository.multimodal_repository import add_multimodal

load_dotenv()

def extract_json(response) -> str:
    return response.choices[0].message.content.strip()

def map_response(response) -> AnalysisResult:
    json_str = extract_json(response)
    return AnalysisResult.model_validate_json(json_str)

async def main() -> None:

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