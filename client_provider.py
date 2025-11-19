import os

from openai import OpenAI, AsyncOpenAI

# using os.environ because I want the system to bomb if not properly configured
model_provider=os.environ['MODEL_PROVIDER']
model_url=os.environ['MODEL_URL']
model_api_key=os.getenv('MODEL_API_KEY', '')

def get_client():
    print(f"Using model provider: {model_provider}")
    return OpenAI(
        base_url=model_url,
        api_key=model_api_key
    )

def get_async_client():
    print(f"Using model provider: {model_provider}")
    return AsyncOpenAI(
        base_url=model_url,
        api_key=model_api_key
    )
