# =============================================================================
# Multimodal Repository Module
# =============================================================================
# This module handles the storage and retrieval of Multimodal data in ChromaDB
# It provides three operations.
# 1. Add multimodal embeddings to the vector DB
# 2. Search the multimodal embeddings by text similarity
# 3. Search the multimodal embeddings by image similarity
# =============================================================================
import time

import chromadb
import numpy as np
from PIL import Image
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from dotenv import load_dotenv

from configuration.config import Config
from models.api_models import SearchResult
from models.indexing_models import AnalysisResult
from repository.search_transformer import transform

print("Initializing Multimodal Repository")
config = Config()

# Necessary to get HF_TOKEN into the environment and quiet down some "scary" looking logs from
# the OpenCLIP model download
load_dotenv()

# This uses OpenCLIP for embedding. Note that if not previously cached
# this will trigger a download of the model.  This is the only time the internet is
# Needed when running the app.
print("- Initializing Multimodal embedding model")
embedding_function = OpenCLIPEmbeddingFunction()

print("- Connecting to DB")
dbclient = chromadb.PersistentClient(path=f"{config.db_base_path}/multimodal.db")
data_loader = ImageLoader()

print("- Setting up Multimodal Collection")
multimodal_collection =  dbclient.get_or_create_collection(
    name='multimodal_collection',
    embedding_function=embedding_function,
    data_loader=data_loader,
    configuration = CreateCollectionConfiguration(
        hnsw=CreateHNSWConfiguration(
            space="cosine",
            ef_construction=200
        )
    )
)

print()

def add_multimodal(image_path: str, data: AnalysisResult, thumbnail: str):
    """
    Adds a multimodal image entry to the ChromaDB collection.

    :param image_path: The original path to the image file in the storage system
    :param data: AnalysisResult containing AI-generated description, tags, colors, etc.
    :param thumbnail: Base64-encoded string of the image thumbnail

    :return: None (side effect - adds data to database)
    """
    server_friendly_path = config.photos_url_base + image_path[len(config.photos_base_path):]

    timer = time.time()
    multimodal_collection.add(
        ids=[server_friendly_path],
        uris=[image_path],
        metadatas=[{"description": data.description, 'thumbnail': thumbnail}],
    )
    print(f"  - Adding to Multimodal collection took took {time.time() - timer:.4f} seconds")

def find_by_image(image_data: Image.Image, cutoff_threshold: float) -> list[SearchResult]:
    """
    Searches for images in the catalog that are visually similar to the provided image.

    :param image_data: PIL Image object representing the query image
    :param cutoff_threshold: Minimum similarity threshold (0.0 to 1.0) for filtering results

    :return: List of SearchResult objects containing matching images ranked by similarity
    """
    img_array = np.array(image_data)
    results = multimodal_collection.query(
        query_images=[img_array]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results

def find_by_text_mm(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    """
    Searches for images in the catalog whose multimodal embeddings match the provided text.

    :param search_text: Text query to search for (e.g., "beach sunset", "mountain landscape")
    :param cutoff_threshold: Minimum similarity threshold (0.0 to 1.0) for filtering results

    :return: List of SearchResult objects containing matching images ranked by similarity
    """
    results = multimodal_collection.query(
        query_texts=[search_text]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results
