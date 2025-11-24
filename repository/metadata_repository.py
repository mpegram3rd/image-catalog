import chromadb
from openai.types import CreateEmbeddingResponse

from ai.client_provider import get_client
from config import Config

config = Config('.env')

dbclient = chromadb.PersistentClient(path="./data/metadata.db")

eb_client = get_client()

def generate_embeddings(text: str) -> CreateEmbeddingResponse:
    embeddings = eb_client.embeddings.create(
        input = text,
        model=config.llm_embedding_model
    )

    return embeddings