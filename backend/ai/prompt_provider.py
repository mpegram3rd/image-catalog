import aiofiles


class PromptProvider:
    """
    Manages loading and caching of prompt templates from a directory.

    This provider reads markdown files containing prompt templates from the specified
    directory and caches them in memory for efficient reuse across multiple requests.
    The caching mechanism prevents redundant file I/O operations when the same prompt
    is requested multiple times.

    Attributes:
        _prompt_dir (str): The directory path where prompt markdown files are stored.
        _prompts (dict): An in-memory cache storing loaded prompts keyed by their name.
    """
    def __init__(self, prompt_dir: str = 'prompts') -> None:
        """
        Initialize the PromptProvider with a directory path for prompt templates.

        Args:
            prompt_dir (str): The relative or absolute path to the directory containing
                             prompt markdown files. Defaults to 'prompts'.

        Note:
            The directory should contain .md files with prompt templates. Each file's
            name (without extension) will be used as the identifier when retrieving prompts.
        """
        self._prompt_dir = prompt_dir
        self._prompts = dict[str, str] = {} # prompt cache

    async def get_prompt_async(self, name: str) -> str:
        """
        Asynchronously retrieves a prompt template by its name.

        This method first checks the in-memory cache for an existing prompt.
        If not found, it reads the corresponding .md file from disk and caches it.

        Args:
            name (str): The identifier/name of the prompt template to retrieve.

        Returns:
            str: The content of the requested prompt as a string.

        Raises:
            FileNotFoundError: If no prompt with the given name exists in the directory.
        """
        prompt = self._prompts.get(name, None)
        if prompt:
            return prompt

        try:

            async with aiofiles.open(self._prompt_dir + '/' + name + '.md', 'r') as garb_in:
                prompt = await garb_in.read()
            self._prompts[name] = prompt
            return prompt
        except FileNotFoundError:
            print(f"Error: Could not load requested prompt '{name}'.")
            raise FileNotFoundError(
                f"No prompt template found for name: '{name}' in directory '{self._prompt_dir}'"
            )
