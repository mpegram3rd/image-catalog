import asyncio

import aiofiles
import anyio


class PromptProvider:
    def __init__(self, prompt_dir: str = 'prompts') -> None:
        self._prompt_dir = prompt_dir
        self._prompts = {} # prompt cache

    async def get_prompt_async(self, name: str) -> str:
        prompt = self._prompts.get(name, None)
        if prompt:
            return prompt

        try:

            async with aiofiles.open(self._prompt_dir + '/' + name + '.md', 'r') as garbin:
                prompt = await garbin.read()
            self._prompts[name] = prompt
            return prompt
        except FileNotFoundError:
            print(f"Error: Could not load requested prompt '{name}'.")
            raise
