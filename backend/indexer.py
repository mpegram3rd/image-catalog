import asyncio
from pathlib import Path
import re
import time

from openai.types.chat.completion_create_params import ResponseFormat

from ai.client_provider import get_client
from config import Config
from images.image_handler import encode_image_async
from repository.metadata_repository import add_analysis, list_contents
from models.models import AnalysisResult
from ai.prompt_provider import PromptProvider

def extract_json(response) -> str:
    # pattern = r"```(?:json)?\s*(.*?)\s*```"
    # match = re.search(pattern, response.choices[0].message.content, flags=re.DOTALL)
    #
    # if not match:
    #     raise ValueError("No JSON code block found in the supplied text.")
    #
    # json_str = match.group(1).strip()
    return response.choices[0].message.content.strip()

def map_response(response) -> AnalysisResult:
    json_str = extract_json(response)
    return AnalysisResult.model_validate_json(json_str)

async def main() -> None:

    config = Config('.env')

    client = get_client()
    prompt_provider = PromptProvider('ai/prompts')
    prompt = await prompt_provider.get_prompt_async('image-analysis')

    base_path = Path('../photos/') # TODO Put this in the environment
    for p in base_path.rglob("*"):
        if p.is_file() and (p.suffix in ['.jpg', '.png']):
            print(f"Processing {p}...")
            start_time = time.time()  # Record start time

            image_data = await encode_image_async(p)

            response = client.chat.completions.parse(
                model=config.llm_model,
                response_format=AnalysisResult,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{prompt}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                ]
            )

            results = map_response(response)
            print(results.model_dump_json(indent=2))
            add_analysis(str(p), results)

            end_time = time.time()  # Record end time

            execution_time = end_time - start_time
            print(f"Processing {p} took {execution_time:.4f} seconds")
    list_contents()

asyncio.run(main())