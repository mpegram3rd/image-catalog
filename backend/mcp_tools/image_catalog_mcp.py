import base64

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from sympy import true

from api_routes.image_catalog_router import search_by_text
from models.api_models import SearchResultsMcp, TextSearchRequest

image_catalog_mcp = FastMCP("Image Catalog Tools")

@image_catalog_mcp.tool(name="find_images_by_text", description="Search for images using a text search query")
async def find_by_text_mcp(search_query: str) -> list[SearchResultsMcp]:
    """
    Searches for images that match the text described in the search query input parameter

    :param search_query:  The text to search for

    :return: a list of search results that are most similar to the search request
    """
    text_search = TextSearchRequest(
        searchText=search_query,
        threshold="yuge",
        multimodal=False
    )
    search_result = await search_by_text(text_search)
    mcp_results = list[SearchResultsMcp]()

    for result in search_result:
        mcp_results.append(SearchResultsMcp(
            image_path=f"http://localhost:5173/{result.image_path}",
            description=result.description
        ))

    return mcp_results


@image_catalog_mcp.tool(
    name="find_displayable_image",
    description="Searches for images using a text search query and returns the closest images it can find in the image "
                "catalog to what was requested so the image can be displayed in the AI. "
                "This function should be called to retrieve a displayable version of images from the catalog."
)
async def find_displayable_images_mcp(search_query: str) -> list[Image]:
    """
    Searches for an image which matches the text described in the search query input parameter.

    :param search_query:  The text to search for

    :return: 1 or more images of the top matching results in a format that can be displayed in the AI
    """
    text_search = TextSearchRequest(
        searchText=search_query,
        threshold="small",
        multimodal = False
    )

    search_result = await search_by_text(text_search)

    results = list[Image]()
    for result in search_result:
        image_data = base64.b64decode(result.thumbnail[len("data:image/png;base64,"):])
        results.append(Image(data=image_data, format="png"))

    return results


