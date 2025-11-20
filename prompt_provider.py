from typing import Dict

from anyio import open_file


class PromptProvider:
    def __init__(self, prompt_dir: str = 'prompts') -> None:
        self._prompt_dir = prompt_dir
        self._prompts = Dict[str, str]() # prompt cache

    async def get_prompt_async(self, name: str):
        prompt = self._prompts[name]
        if prompt:
            return prompt

        try:

            async with open_file(self._prompt_dir + '/' + name + '.md', 'r') as garbin:
                prompt = await garbin.read()
            self._prompts[name] = prompt
            return prompt
        except FileNotFoundError:
            print(f"Error: Could not load requested prompt '{name}'.")
            raise
