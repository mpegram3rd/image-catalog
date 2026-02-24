from openai import AsyncOpenAI, OpenAI

from configuration.config import Config
from configuration.logging_config import get_logger

config = Config(".env")
logger = get_logger(__name__)
client_cache = {"sync": None, "async": None}


def get_client() -> OpenAI:
    """Creates and returns an instance of the `OpenAI` compatible client.

    Configured with the specified base URL and API key. The function retrieves
    configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `OpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: OpenAI
    """
    if client_cache["sync"] is None:
        logger.debug(
            "Creating new sync OpenAI client",
            extra={
                "provider": config.llm_provider,
                "base_url": config.llm_url,
            },
        )
        client_cache["sync"] = OpenAI(base_url=config.llm_url, api_key=config.llm_api_key)
    return client_cache["sync"]


def get_async_client() -> AsyncOpenAI:
    """Creates and returns an instance of the `AsyncOpenAI` compatible client.

    Configured with the specified base URL and API key. The function retrieves
    configuration details such as the model provider,
    URL, and API key to initialize the `OpenAI` client instance.

    :return: An initialized `AsyncOpenAI` compatible client instance configured with the
        base URL and API key.
    :rtype: AsyncOpenAI
    """
    if client_cache["async"] is None:
        logger.debug(
            "Creating new async OpenAI client",
            extra={
                "provider": config.llm_provider,
                "base_url": config.llm_url,
            },
        )
        client_cache["async"] = AsyncOpenAI(base_url=config.llm_url, api_key=config.llm_api_key)
    return client_cache["async"]
