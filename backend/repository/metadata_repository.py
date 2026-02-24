import time

import chromadb
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils import embedding_functions

from configuration.config import Config
from configuration.logging_config import get_logger, log_performance
from models.api_models import SearchResult
from models.indexing_models import AnalysisResult, Metadata
from repository.search_transformer import transform

logger = get_logger(__name__)

logger.info("Initializing Metadata Repository")
config = Config()

# Fetch embedding model for multimodal data
logger.info(
    "Initializing OpenAI compatible embedding model",
    extra={
        "embedding_model": config.llm_embedding_model,
        "provider": config.llm_provider,
    },
)
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=config.llm_api_key,
    api_base=config.llm_url,
    api_type=config.llm_provider,
    api_version="v1",
    model_name=config.llm_embedding_model,
)

logger.info(
    "Connecting to ChromaDB",
    extra={
        "db_path": f"{config.db_base_path}/image_data.db",
    },
)
dbclient = chromadb.PersistentClient(path=f"{config.db_base_path}/image_data.db")

logger.info("Setting up Description Collection")
description_collection = dbclient.get_or_create_collection(
    name="descriptions",
    embedding_function=embedding_func,
    configuration=CreateCollectionConfiguration(
        hnsw=CreateHNSWConfiguration(space="cosine", ef_construction=200)
    ),
)


def add_analysis(image_path: str, data: AnalysisResult, thumbnail: str):
    metadata = Metadata(
        tags=", ".join(list(map(lambda tag: tag.tag, data.tags))),
        colors=", ".join(list(map(lambda color: color.color, data.colors))),
        thumbnail=thumbnail,
    )

    server_friendly_path = config.photos_url_base + image_path[len(config.photos_base_path) :]

    timer = time.time()
    description_collection.add(
        ids=[server_friendly_path], documents=[data.description], metadatas=[metadata.model_dump()]
    )
    duration = time.time() - timer
    log_performance("description_collection_add", duration, logger)


def find_by_text(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    results = description_collection.query(query_texts=[search_text])

    search_results = transform(results, cutoff_threshold)

    return search_results
