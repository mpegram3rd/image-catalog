import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from openai.types import CreateEmbeddingResponse

from ai.client_provider import get_client
from config import Config
from models.models import AnalysisResult, Metadata

config = Config('.env')

dbclient = chromadb.PersistentClient(path="./data/metadata.db")

embedding_func = embedding_functions.OpenAIEmbeddingFunction(
                api_key=config.llm_api_key,
                api_base=config.llm_url,
                api_type=config.llm_provider,
                api_version="v1",
                model_name=config.llm_embedding_model
            )

metadata_collection = dbclient.get_or_create_collection(
    name="metadata",
    embedding_function=embedding_func,
    configuration = {
        "hnsw": {
            "space": "cosine",
            "ef_construction": 200
        }
    }
)


def add_analysis(image_path: str, data: AnalysisResult):

    # metadata = {
    #     "tags": ", ".join(list(map(lambda tag: tag.tag, data.tags))),
    #     "colors": ", ".join(list(map(lambda color: color.color, data.colors)))
    # }
    metadata = {
        "tags": list(map(lambda tag: tag.tag, data.tags)),
        "colors": list(map(lambda color: color.color, data.colors))
    }
    # metadata = Metadata(
    #     tags = ", ".join(list(map(lambda tag: tag.tag, data.tags))),
    #     colors=", ".join(list(map(lambda color: color.color, data.colors)))
    # )

    # metadata_str = metadata.model_dump_json()

    metadata_collection.add (
        ids=[image_path],
        documents=[data.description],
        metadatas=[{
            "tags": ["python", "vector-db", "chromadb"],
            "scores": [0.5, 0.8, 0.9],
            "misc": {"nested": ["a", "b", "c"]}  # nested structures also allowed
        }]
    )

def list_contents():
    batch= metadata_collection.get(
        include=["metadatas", "documents"]
    )
    print(batch)

    result = metadata_collection.query(
        include=["metadatas", "documents"],
        query_texts=["Fall leaves"]
    )
    print (result)

    result2 = metadata_collection.query(
        query_texts=[""],
        where={
            "colors": "red"
        }
    )
    print (result2)
