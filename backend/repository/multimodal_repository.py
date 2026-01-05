import time
from typing import Final

import chromadb
from PIL import Image
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

from configuration.config import Config
from models.models import AnalysisResult, SearchResult
import numpy as np

from repository.search_transformer import transform

print("Initializing Multimodal Repository")
config = Config()

# Fetch embedding model for multimodal data
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
    server_friendly_path = config.photos_url_base + image_path[len(config.photos_base_path):]

    timer = time.time()
    multimodal_collection.add(
        ids=[server_friendly_path],
        uris=[image_path],
        metadatas=[{"description": data.description, 'thumbnail': thumbnail}],
    )
    print(f"  - Adding to Multimodal collection took took {time.time() - timer:.4f} seconds")

def find_by_image(image_data: Image.Image, cutoff_threshold: float) -> list[SearchResult]:
    img_array = np.array(image_data)
    results = multimodal_collection.query(
        query_images=[img_array]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results

def find_by_text_mm(search_text: str, cutoff_threshold: float) -> list[SearchResult]:
    results = multimodal_collection.query(
        query_texts=[search_text]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results
