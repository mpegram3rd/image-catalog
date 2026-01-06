from typing import List, Annotated, Literal

from fastmcp.utilities.types import Image
from mcp.types import ImageContent
from pydantic import BaseModel, Field


class TagData(BaseModel):
    tag: str
    confidence: float

class ColorData(BaseModel):
    color: str
    frequency: float

class Metadata(BaseModel):
    tags: str
    colors: str
    thumbnail: str

class AnalysisResult(BaseModel):
    tags: List[TagData]
    colors: List[ColorData]
    description: str

class SearchResult(BaseModel):
    """
    This represents the results of an image lookup regardless of whether it was done by image matching or text based search
    """
    image_path: Annotated[str, Field(description="The relative path to the full resolution image that can be used in a URL")]
    description: Annotated[str, Field(description="A detailed description of the image that can be used to describe it to someone visually impaired")]
    thumbnail: Annotated[str, Field(description="A Base64 encoded thumbnail version of the image in PNG format")]
    distance: Annotated[float, Field(description="The calculated distance in vector space between the search criteria and the result. The closer to 0.0 the better the result is.")]


class TextSearchRequest(BaseModel):
    """
    Text Search Request criteria
    """
    searchText: Annotated[str, Field(description="Text to used when searching images")]
    multimodal: Annotated[bool, Field(description="Determines if the search should be performed using the multimodal dataset. Default is to search on description")] = False
    threshold: Annotated[Literal["small", "medium", "yuge"], Field(description="Determines the threshold distance between the first result and subsequent results to use for filtering. Default is `small`")] = "small"

class SearchResultsMcp(BaseModel):
    """
    This represents the results of an image lookup regardless of whether it was done by image matching or text based search
    """
    image_path: Annotated[str, Field(description="The full URL to view the image that was found")]
    description: Annotated[str, Field(description="A detailed description of the image that can be used to describe it to someone visually impaired")]

