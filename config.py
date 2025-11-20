from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    llm_model: str
    llm_provider: str
    llm_base_url: str
    llm_api_key: str

    def __init__(self, env_file: str = '.env'):
        super().__init__()
        model_config = SettingsConfigDict(env_file=env_file)

