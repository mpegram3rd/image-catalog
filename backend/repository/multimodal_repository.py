from typing import Final

import chromadb
from PIL import Image
from chromadb import QueryResult
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

from configuration.config import Config
from models.models import AnalysisResult, SearchResult
import numpy as np

## Threshold distance values for filtering results
SMALL_CUTOFF_THRESHOLD: Final = 0.05
MEDIUM_CUTOFF_THRESHOLD: Final = 0.1
YUGE_CUTOFF_THRESHOLD: Final = 0.3

config = Config()

dbclient = chromadb.PersistentClient(path=f"{config.db_base_path}/multimodal.db")
data_loader = ImageLoader()
embedding_function = OpenCLIPEmbeddingFunction()

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

def add_multimodal(image_path: str, data: AnalysisResult):
    multimodal_collection.add(
        ids=[image_path],
        uris=[image_path],
        metadatas=[{"description": data.description}]
    )

def transform(results: QueryResult, cutoff_threshold: float) -> list[SearchResult]:

    search_results: list[SearchResult] = []

    # Chroma Structure is wonky, so we're going to save some processing
    # by pre-fetching the first result from each category we want to work with
    # for mapping.  This is viable because we only submit 1 search request at a time
    ids = results['ids'][0]
    metadata = results['metadatas'][0]
    distances = results['distances'][0]

    # The closest distance to our search item.  We're going to use this distance
    # to calculate a threshold by which search results are "too far away" to be worth consideration.
    initial_distance = distances[0]

    index = 0
    while index < len(ids):

        # Calculate a relative distance from the closest result to determine if we
        # should stop processing results.  The value represents roughly a measure of
        # the distance difference between the closest result and the current as a percentage
        # of the total distance of the closest result to the search item.
        # The key idea is that as results diverge further they're significantly less relevant
        if initial_distance != 0.0:
           relative_distance = abs(distances[index] - initial_distance) / abs(initial_distance)
        else:
            relative_distance = distances[index]

        if relative_distance >= cutoff_threshold:
            break

        search_results.append(
            SearchResult(
                image_path=ids[index],
                description=metadata[index]['description'],
                distance = distances[index]
            )
        )

        index += 1

    return search_results


def find_by_image(image_data: Image.Image, cutoff_threshold: float) -> list[SearchResult]:
    img_array = np.array(image_data)
    results = multimodal_collection.query(
        query_images=[img_array]
    )

    search_results = transform(results, cutoff_threshold)

    return search_results

