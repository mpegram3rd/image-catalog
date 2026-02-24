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
    thumbnail: str


class AnalysisResult(BaseModel):
    tags: list[TagData]
    colors: list[ColorData]
    description: str
