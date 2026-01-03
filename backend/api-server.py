import uvicorn
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models.models import SearchResult
from repository.multimodal_repository import find_by_image, SMALL_CUTOFF_THRESHOLD

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

@app.post("/api/uploadfile")
async def create_upload_file(file: UploadFile) -> list[SearchResult]:
    img = Image.open(file.file)

    results = find_by_image(img, SMALL_CUTOFF_THRESHOLD)
    print(f"Search Image Details: {img.format}, Found: {results[0].image_path} w/ Similarity: {results[0].distance}\nDescription: {results[0].description}")

    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)