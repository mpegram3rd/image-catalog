# =============================================================================
# Metadata Repository Module
# =============================================================================
# This module handles the storage and retrieval of image metadata using ChromaDB.
# It provides two main operations: adding analysis results to the database and
# searching for images based on text queries.
# =============================================================================

import time

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration

from configuration.config import Config
from models.api_models import SearchResult
from models.indexing_models import AnalysisResult, Metadata
from repository.search_transformer import transform

print("Initializing Metadata Repository")
config = Config()

# The embedding model for text data uses any OpenAI compatible embedding model.
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
    """
    Adds an image analysis result to the ChromaDB description collection.

    :param image_path: The path to the original image file (used as document ID)
    :param data: AnalysisResult containing AI-generated description, tags, and colors
    :param thumbnail: Base64-encoded thumbnail of the image

    :return: None (side effect - adds data to database)
    """

    # Transform input model to the storage model
    metadata = Metadata(
        tags = ", ".join(list(map(lambda tag: tag.tag, data.tags))),
        colors=", ".join(list(map(lambda color: color.color, data.colors))),
        thumbnail=thumbnail
    )

    server_friendly_path = config.photos_url_base + image_path[len(config.photos_base_path):]

    timer = time.time()
    description_collection.add (
        ids=[server_friendly_path],
        documents=[data.description],
        metadatas=[metadata.model_dump()]
    )
    print(f"  - Adding to Description collection took took {time.time() - timer:.4f} seconds")

def find_by_text(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    """
    Searches for images whose descriptions are similar to the provided input text using a vector based search.

    :param search_text: The text query to search for (e.g., "beach sunset")
    :param cutoff_threshold: Minimum similarity threshold to filter results

    :return: List of SearchResult objects matching the query
    """
    results = description_collection.query(
        query_texts=[search_text]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results

