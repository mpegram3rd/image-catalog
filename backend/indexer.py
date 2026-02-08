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


class Indexer:
    """Encapsulates image indexing logic.

    The original implementation was a standalone async function.  Replacing it with a class
    gives the caller an instance that holds the client, config and prompt.  It also
    allows the processing loop to be split into smaller methods.
    """

    def __init__(self):
        self.config = Config()
        self.client = get_client()
        self.prompt = None

    @staticmethod
    def _extract_json(response: object) -> str:
        return response.choices[0].message.content.strip()

    @staticmethod
    def _map_response(response: object) -> AnalysisResult:
        json_str = Indexer._extract_json(response)
        return AnalysisResult.model_validate_json(json_str)

    async def _load_prompt(self) -> str:
        prompt_provider = PromptProvider('ai/prompts')
        return await prompt_provider.get_prompt_async('image-analysis')

    async def _process_image(self, p: Path):
        print(f"Processing {p}...")
        total_processing = time.time()
        timer = time.time()

        image_data = await encode_image_async(p)

        response = self.client.chat.completions.parse(
            model=self.config.llm_model,
            response_format=AnalysisResult,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        ChatCompletionContentPartTextParam(type="text", text=self.prompt),
                        ChatCompletionContentPartImageParam(
                            type="image_url",
                            image_url=ImageURL(url=f"data:image/jpeg;base64,{image_data}"),
                        ),
                    ],
                )
            ],
        )

        results = self._map_response(response)

        print(f"- Model analysis took {time.time() - timer:.4f} seconds")

        thumbnail = await create_thumbnail_as_base64_async(
            image_data, self.config.thumbnail_width, self.config.thumbnail_height
        )

        timer = time.time()

        add_analysis(str(p), results, thumbnail)
        add_multimodal(str(p), results, thumbnail)

        print(f"- Embedding and storing took {time.time() - timer:.4f} seconds")
        print(f"- Total Processing Time: {time.time() - total_processing:.4f} seconds\n")

    async def run(self):
        print("Starting Indexer")
        indexing_time = time.time()
        print(
            f"Using LLM model (for Image Analysis): {self.config.llm_model}\n-------\n"
        )
        self.prompt = await self._load_prompt()

        base_path = Path(self.config.photos_base_path)
        processed_images = 0
        for p in base_path.rglob("*"):
            if p.is_file() and p.suffix in [".jpg", ".png"]:
                processed_images += 1
                await self._process_image(p)

        indexing_end = time.time()
        print(
            f"Indexing {processed_images} images took {indexing_end - indexing_time:.4f} seconds"
        )


if __name__ == "__main__":
    asyncio.run(Indexer().run())
