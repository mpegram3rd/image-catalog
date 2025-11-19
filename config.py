from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm: str
    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    model_config = SettingsConfigDict(env_file='.env')
