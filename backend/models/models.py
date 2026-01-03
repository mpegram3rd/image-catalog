from typing import List
from pydantic import BaseModel

class TagData(BaseModel):
    tag: str
    confidence: float

class ColorData(BaseModel):
    color: str
    frequency: float

class Metadata(BaseModel):
    tags: str
    colors: str

class AnalysisResult(BaseModel):
    tags: List[TagData]
    colors: List[ColorData]
    description: str

class SearchResult(BaseModel):
    image_path: str
    description: str
    distance: float


