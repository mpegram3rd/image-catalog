import chromadb
from openai.types import CreateEmbeddingResponse

from client_provider import get_client
from config import Config

config = Config('../.env')

dbclient = chromadb.PersistentClient(path="./data/metadata.db")

eb_client = get_client(config)

def generate_embeddings(text: str) -> CreateEmbeddingResponse:
    embeddings = eb_client.embeddings.create(
        input = text,
        model="text-embedding-qwen3-embedding-0.6b"
    )

    return embeddings