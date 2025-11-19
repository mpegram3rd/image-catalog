import os

from openai import OpenAI, AsyncOpenAI

# using os.environ because I want the system to bomb if not properly configured
model_provider=os.environ['MODEL_PROVIDER']
model_url=os.environ['MODEL_URL']
model_api_key=os.getenv('MODEL_API_KEY', '')

def get_client():
    """
    Creates and returns an instance of the `OpenAI` compatible client configured with the
    specified base URL and API key.

    The function retrieves configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `OpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: OpenAI
    """
    print(f"Using model provider: {model_provider}")
    return OpenAI(
        base_url=model_url,
        api_key=model_api_key
    )

def get_async_client():
    """
    Creates and returns an instance of the `AsyncOpenAI` compatible client configured with the
    specified base URL and API key.

    The function retrieves configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `AsyncOpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: AsyncOpenAI
    """
    print(f"Using model provider: {model_provider}")
    return AsyncOpenAI(
        base_url=model_url,
        api_key=model_api_key
    )
