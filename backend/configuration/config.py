from pydantic_settings import BaseSettings


class Config(BaseSettings):
    llm_model: str
    llm_embedding_model: str
    llm_provider: str
    llm_url: str
    llm_api_key: str
    hf_token: str
    photos_base_path: str
    photos_url_base: str
    db_base_path: str
    thumbnail_width: int
    thumbnail_height: int

    def __init__(self, env_file: str = '.env') -> None:
        super().__init__(_env_file=env_file)


