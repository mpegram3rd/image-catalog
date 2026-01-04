import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration

from configuration.config import Config
from models.models import AnalysisResult, Metadata, SearchResult
from repository.search_transformer import transform

print("Initializing Metadata Repository")
config = Config()

# Fetch embedding model for multimodal data
print("- Initializing OpenAI compatible embedding model")
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
                api_key=config.llm_api_key,
                api_base=config.llm_url,
                api_type=config.llm_provider,
                api_version="v1",
                model_name=config.llm_embedding_model
            )

print("- Connecting to DB")
dbclient = chromadb.PersistentClient(path=f"{config.db_base_path}/image_data.db")

print("- Setting up Metadata Collection")
metadata_collection = dbclient.get_or_create_collection(
    name="metadata",
    embedding_function=embedding_func,
    configuration = CreateCollectionConfiguration(
        hnsw = CreateHNSWConfiguration(
                space = "cosine",
                ef_construction = 200
        )
    )
)

print("- Setting up Description Collection")
description_collection = dbclient.get_or_create_collection(
    name="descriptions",
    embedding_function=embedding_func,
    configuration=CreateCollectionConfiguration(
        hnsw=CreateHNSWConfiguration(
            space="cosine",
            ef_construction=200
        )
    )
)

print()

def add_analysis(image_path: str, data: AnalysisResult, thumbnail: str):

    # metadata = {
    #     "tags": ", ".join(list(map(lambda tag: tag.tag, data.tags))),
    #     "colors": ", ".join(list(map(lambda color: color.color, data.colors)))
    # }
    # metadata = {
    #     "tags": list(map(lambda tag: tag.tag, data.tags)),
    #     "colors": list(map(lambda color: color.color, data.colors))
    # }
    metadata = Metadata(
        tags = ", ".join(list(map(lambda tag: tag.tag, data.tags))),
        colors=", ".join(list(map(lambda color: color.color, data.colors))),
        thumbnail=thumbnail
    )

    # metadata_str = metadata.model_dump_json()
    server_friendly_path = image_path[len(config.photos_base_path):]

    description_collection.add (
        ids=[server_friendly_path],
        documents=[data.description],
        metadatas=[metadata.model_dump()]
    )

    metadata_collection.add(
        ids=[image_path],
        documents=[data.model_dump_json()]
    )


def find_by_text(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    results = description_collection.query(
        query_texts=[search_text]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results

def list_contents():
    batch= description_collection.get(
        include=["metadatas", "documents"]
    )
    print(batch)

    result = description_collection.query(
        include=["metadatas", "documents", "distances"],
        query_texts=["Fall leaves"]
    )
    print (result)

    result2 = metadata_collection.query(
        include=["metadatas", "documents", "distances"],
        query_texts=["\"color\":\"brown\""]
    )
    print (result2)
