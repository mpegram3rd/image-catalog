import base64

import uvicorn
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from models.models import SearchResult, TextSearchRequest, SearchResultsMcp
from repository.filtering_thresholds import MEDIUM_CUTOFF_THRESHOLD, VALID_THRESHOLDS
from repository.metadata_repository import find_by_text
from repository.multimodal_repository import find_by_image, find_by_text_mm

mcp = FastMCP("Image Catalog Tools")
mcp_app = mcp.http_app(path='/mcp')

app = FastAPI(title="Image Catalog Tools API", lifespan=mcp_app.lifespan)

app.mount("/ai", mcp_app)


origins = [
    "http://localhost",
    "http://localhost:5173",
]

# Enable CORS for all origins (DEVELOPMENT ONLY - NOT RECOMMENDED FOR PRODUCTION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@mcp.tool(name="find_images_by_text", description="Search for images using a text search query")
async def find_by_text_mcp(searchQuery: str) -> list[SearchResultsMcp]:
    """
    Searches for images that match the text described in the search query input parameter

    :param searchQuery:  The text to search for

    :return: a list of search results that are most similar to the search request
    """
    text_search = TextSearchRequest(
        searchText=searchQuery,
        threshold="yuge"
    )
    search_result = await search_by_text(text_search)
    mcp_results = list[SearchResultsMcp]()

    for result in search_result:
        mcp_results.append(SearchResultsMcp(
            image_path="http://localhost:5173/" + result.image_path,
            description=result.description

        ))
    return mcp_results


@mcp.tool(
    name="find_displayable_image",
    description="Searches for an image using a text search query and returns the closest image it can find in the image catalog to what was requested so the image can be displayed in the AI"
)
async def find_displayable_image_mcp(searchQuery: str) -> Image:
    """
    Searches for images that match the text described in the search query input parameter

    :param searchQuery:  The text to search for

    :return: a list of search results that are most similar to the search request
    """
    text_search = TextSearchRequest(
        searchText=searchQuery,
        threshold="yuge"
    )
    search_result = await search_by_text(text_search)
    image_data= base64.b64decode(search_result[0].thumbnail[len("data:image/png;base64,"):])

    return Image(data=image_data, format="png")


@app.post("/api/search/image")
async def search_by_image(file: UploadFile) -> list[SearchResult]:
    """
    Searches for images that are similar to the binary one provided in the 'file' input parameter.
    This utilizes the multimodal repository which has an index of all the available images to search for.

    :param file: a PNG or JPEG image file which will be converted to an embedding and used to search for similar images.
    :return: A list of search results that are most similar to the image provided.  The search results contain image_path, description and thumbnail
    """
    img = Image.open(file.file)

    results = find_by_image(img, MEDIUM_CUTOFF_THRESHOLD)
    print(f"Search Image Details: {img.format}, Found: {results[0].image_path} w/ Similarity: {results[0].distance}\nDescription: {results[0].description}")

    return results

@app.post("/api/search/text")
async def search_by_text(search: TextSearchRequest) -> list[SearchResult]:
    """
    Searches for images that match the provided 'searchText' in the 'search' input parameter. This endpoint can
    use either the `description` repository which is using text based embeddings to find a match, or it can search
    against the `multimodal` repository which searches the multimodal space generated from the binary image on embedding.
    :param search: The search criteria and an indication of which repository to perform the search
    :return: A list of search results that are most similar to the image provided.  The search results contain image_path, description and thumbnail
    """
    if search.multimodal:
        results = find_by_text_mm(search.searchText, VALID_THRESHOLDS[search.threshold])
    else:
        results = find_by_text(search.searchText, VALID_THRESHOLDS[search.threshold])

    return results



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)