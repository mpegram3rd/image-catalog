import uvicorn
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models.models import SearchResult
from repository.multimodal_repository import find_by_image

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

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
@app.post("/api/uploadfile")
async def create_upload_file(file: UploadFile) -> SearchResult:
    img = Image.open(file.file)
    print(f"Image Details: {img.format}")
    find_by_image(img)
    return SearchResult(
        image_path = file.filename,
        description = "This is a test description"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)