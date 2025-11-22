from typing import List

from pydantic import BaseModel

class TagData(BaseModel):
    tag: str
    confidence: float

class ColorData(BaseModel):
    color: str
    frequency: float

class AnalysisResult(BaseModel):
    description: str
    tags: List[TagData]
    colors: List[ColorData]
