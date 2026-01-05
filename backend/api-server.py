import uvicorn
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models.models import SearchResult, TextSearchRequest
from repository.filtering_thresholds import SMALL_CUTOFF_THRESHOLD, MEDIUM_CUTOFF_THRESHOLD
from repository.metadata_repository import find_by_text
from repository.multimodal_repository import find_by_image, find_by_text_mm

app = FastAPI()

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
        results = find_by_text_mm(search.searchText, SMALL_CUTOFF_THRESHOLD)
    else:
        results = find_by_text(search.searchText, MEDIUM_CUTOFF_THRESHOLD)

    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)