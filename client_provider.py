from openai import OpenAI, AsyncOpenAI

from config import Config


def get_client(config: Config):
    """
    Creates and returns an instance of the `OpenAI` compatible client configured with the
    specified base URL and API key.

    The function retrieves configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `OpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: OpenAI
    """
    print(f"Using model provider: {config.llm_provider}")
    return OpenAI(
        base_url=config.llm_url,
        api_key=config.llm_api_key
    )

def get_async_client(config: Config):
    """
    Creates and returns an instance of the `AsyncOpenAI` compatible client configured with the
    specified base URL and API key.

    The function retrieves configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `AsyncOpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: AsyncOpenAI
    """
    print(f"Using model provider: {config.llm_provider}")
    return AsyncOpenAI(
        base_url=config.llm_url,
        api_key=config.llm_api_key
    )
