import asyncio
from pathlib import Path
import re
import time

from client_provider import get_client
from config import Config
from indexer.image_handler import encode_image_async
from metadata_repository import generate_embeddings
from models.analysis_result import AnalysisResult
from prompt_provider import PromptProvider

def extract_json(response) -> str:
    pattern = r"```(?:json)?\s*(.*?)\s*```"
    match = re.search(pattern, response.choices[0].message.content, flags=re.DOTALL)

    if not match:
        raise ValueError("No JSON code block found in the supplied text.")

    json_str = match.group(1).strip()
    return json_str

def map_response(response) -> AnalysisResult:
    json_str = extract_json(response)
    return AnalysisResult.model_validate_json(json_str)

async def main() -> None:

    config = Config('../.env')

    client = get_client(config)
    prompt_provider = PromptProvider('../prompts')
    prompt = await prompt_provider.get_prompt_async('image-analysis')

    base_path = Path('../images/')
    for p in base_path.rglob("*"):
        if p.is_file() and p.suffix == '.jpg':
            print(f"Processing {p}...")
            start_time = time.time()  # Record start time

            image_data = await encode_image_async(p)

            response = client.chat.completions.create(
                model=config.llm_model,
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

            embeddings = generate_embeddings(results.description)
            # print(response.choices[0].message.content)
            end_time = time.time()  # Record end time

            execution_time = end_time - start_time
            print(f"Processing {p} took {execution_time:.4f} seconds")

asyncio.run(main())