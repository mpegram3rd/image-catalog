import time

import chromadb
import numpy as np
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from PIL import Image

from configuration.config import Config
from configuration.logging_config import get_logger, log_performance
from models.api_models import SearchResult
from models.indexing_models import AnalysisResult
from repository.search_transformer import transform

logger = get_logger(__name__)

logger.info("Initializing Multimodal Repository")
config = Config()

# Fetch embedding model for multimodal data
logger.info("Initializing OpenCLIP embedding model")
embedding_function = OpenCLIPEmbeddingFunction()

logger.info(
    "Connecting to ChromaDB",
    extra={
        "db_path": f"{config.db_base_path}/multimodal.db",
    },
)
dbclient = chromadb.PersistentClient(path=f"{config.db_base_path}/multimodal.db")
data_loader = ImageLoader()

logger.info("Setting up Multimodal Collection")
multimodal_collection = dbclient.get_or_create_collection(
    name="multimodal_collection",
    embedding_function=embedding_function,
    data_loader=data_loader,
    configuration=CreateCollectionConfiguration(
        hnsw=CreateHNSWConfiguration(space="cosine", ef_construction=200)
    ),
)


def add_multimodal(image_path: str, data: AnalysisResult, thumbnail: str):
    server_friendly_path = config.photos_url_base + image_path[len(config.photos_base_path) :]

    timer = time.time()
    multimodal_collection.add(
        ids=[server_friendly_path],
        uris=[image_path],
        metadatas=[{"description": data.description, "thumbnail": thumbnail}],
    )
    duration = time.time() - timer
    log_performance("multimodal_collection_add", duration, logger)


def find_by_image(image_data: Image.Image, cutoff_threshold: float) -> list[SearchResult]:
    img_array = np.array(image_data)
    results = multimodal_collection.query(query_images=[img_array])

    search_results = transform(results, cutoff_threshold)

    return search_results


def find_by_text_mm(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    results = multimodal_collection.query(query_texts=[search_text])

    search_results = transform(results, cutoff_threshold)

    return search_results
