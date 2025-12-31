import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api import CreateCollectionConfiguration
from chromadb.api.collection_configuration import CreateHNSWConfiguration

from config import Config
from models.models import AnalysisResult, Metadata

config = Config('.env')

dbclient = chromadb.PersistentClient(path="./data/image_data.db")

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
    configuration = CreateCollectionConfiguration(
        hnsw = CreateHNSWConfiguration(
                space = "cosine",
                ef_construction = 200
        )
    )
)

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


def add_analysis(image_path: str, data: AnalysisResult):

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
        colors=", ".join(list(map(lambda color: color.color, data.colors)))
    )

    # metadata_str = metadata.model_dump_json()

    description_collection.add (
        ids=[image_path],
        documents=[data.description],
        metadatas=[metadata.model_dump()]
    )

    metadata_collection.add(
        ids=[image_path],
        documents=[data.model_dump_json()]
    )

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
