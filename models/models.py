from typing import List
from pydantic import BaseModel

class TagData(BaseModel):
    tag: str
    confidence: float

class ColorData(BaseModel):
    color: str
    frequency: float

class Metadata(BaseModel):
    tags: List[TagData]
    colors: List[ColorData]

class AnalysisResult(Metadata):
    description: str


