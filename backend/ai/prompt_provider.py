import aiofiles


class PromptProvider:
    """A utility class for managing and retrieving prompt templates asynchronously.

    This class provides a simple interface to load markdown-based prompt files
    from a specified directory, with built-in caching for improved performance.
    It's designed to work efficiently in async environments by minimizing disk I/O.

    Attributes:
        _prompt_dir (str): The directory path where prompt files are stored.
        _prompts (dict): An internal cache storing loaded prompts by name.
    """

    def __init__(self, prompt_dir: str = "prompts") -> None:
        """Initialize the PromptProvider with an optional directory path.

        Args:
            prompt_dir (str): The relative or absolute path to the directory containing
                prompt files. Defaults to "prompts".

        Note:
            The class expects prompt files to have a .md extension. If a requested
            prompt file doesn't exist, it will raise a FileNotFoundError.
        """

        self._prompt_dir = prompt_dir
        self._prompts = {}  # prompt cache

    async def get_prompt_async(self, name: str) -> str:
        """Retrieve a prompt template by its name with automatic caching.

        This method first checks the internal cache for an existing prompt.
        If not found, it reads the file from disk and stores it in cache for future use.
        This lazy-loading approach ensures prompts are only loaded when needed,
        improving performance for repeated requests.

        Args:
            name (str): The unique identifier/name of the prompt to retrieve.

        Returns:
            str: The full content of the requested prompt file as a string.

        Raises:
            FileNotFoundError: If no prompt with the given name exists in the directory.

        Note:
            The method is async and should be awaited when called.
            File paths are constructed by appending ".md" to the provided name.

        """

        prompt = self._prompts.get(name, None)
        if prompt:
            return prompt

        try:
            async with aiofiles.open(self._prompt_dir + "/" + name + ".md") as garbin:
                prompt = await garbin.read()
            self._prompts[name] = prompt
            return prompt
        except FileNotFoundError:
            print(f"Error: Could not load requested prompt '{name}'.")
            raise
