from openai import OpenAI, AsyncOpenAI

from config import Config

config = Config('../.env')
client_cache = {
    "sync": None,
    "async": None
}

def get_client() -> OpenAI:
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
    if client_cache["sync"] is None:
        client_cache["sync"] = OpenAI(
            base_url=config.llm_url,
            api_key=config.llm_api_key
        )
    return client_cache["sync"]

def get_async_client(self) -> AsyncOpenAI:
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
    if client_cache["async"]is None:
        client_cache["async"] = AsyncOpenAI(
            base_url=self._config.llm_url,
            api_key=self._config.llm_api_key
        )
    return client_cache["async"]
