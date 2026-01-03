import chromadb
from PIL import Image
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

from config import Config
from models.models import AnalysisResult, Metadata
import numpy as np


config = Config('.env')

dbclient = chromadb.PersistentClient(path="./data/multimodal.db")
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

def find_by_image(image_data: Image):
    img_array = np.array(image_data)
    result = multimodal_collection.query(
        query_images=[img_array]
    )
    print(result)
    for i, item in enumerate(result['ids'][0]):
        print(f"Id: {item} / Distance: {result['distances'][0][i]}")
        print(f"Description: \n {result['metadatas'][0][i]['description']}")
    return result

