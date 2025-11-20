import asyncio

from client_provider import get_client
from config import Config
from indexer.image_handler import encode_image_async
from prompt_provider import PromptProvider

async def main() -> None:

    config = Config('../.env')

    client = get_client(config)
    prompt_provider = PromptProvider('../prompts')
    prompt = await prompt_provider.get_prompt_async('image-analysis')


    image_data = await encode_image_async('../images/rotunda.jpg')

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

    print(response.choices[0].message.content)

asyncio.run(main())