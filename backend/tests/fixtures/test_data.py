"""Test data fixtures and mock objects for image-catalog tests."""

import base64
import io
from typing import Any, Dict, List

from PIL import Image

from models.api_models import SearchResult, SearchResultsMcp, TextSearchRequest
from models.indexing_models import AnalysisResult, ColorData, TagData


class TestImages:
    """Test image data and utilities."""

    @staticmethod
    def create_test_image(width: int = 100, height: int = 100, color: str = "red") -> Image.Image:
        """Create a test PIL Image."""
        return Image.new("RGB", (width, height), color=color)

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def create_thumbnail_base64(width: int = 50, height: int = 50, color: str = "blue") -> str:
        """Create a base64 encoded thumbnail."""
        thumbnail = TestImages.create_test_image(width, height, color)
        return f"data:image/png;base64,{TestImages.image_to_base64(thumbnail, 'PNG')}"


class MockLLMResponses:
    """Mock responses from LLM for testing."""

    SAMPLE_ANALYSIS_JSON = {
        "description": "A beautiful red rose in full bloom with green leaves",
        "tags": [
            {"tag": "flower", "confidence": 0.95},
            {"tag": "rose", "confidence": 0.90},
            {"tag": "red", "confidence": 0.85},
            {"tag": "garden", "confidence": 0.70}
        ],
        "colors": [
            {"color": "red", "frequency": 45},
            {"color": "green", "frequency": 30},
            {"color": "pink", "frequency": 15},
            {"color": "brown", "frequency": 10}
        ]
    }

    SAMPLE_LANDSCAPE_JSON = {
        "description": "A serene mountain landscape with snow-capped peaks reflected in a crystal-clear lake",
        "tags": [
            {"tag": "landscape", "confidence": 0.98},
            {"tag": "mountain", "confidence": 0.95},
            {"tag": "lake", "confidence": 0.90},
            {"tag": "nature", "confidence": 0.88}
        ],
        "colors": [
            {"color": "blue", "frequency": 40},
            {"color": "white", "frequency": 25},
            {"color": "gray", "frequency": 20},
            {"color": "green", "frequency": 15}
        ]
    }

    SAMPLE_PORTRAIT_JSON = {
        "description": "Professional headshot of a person with a warm smile wearing business attire",
        "tags": [
            {"tag": "portrait", "confidence": 0.95},
            {"tag": "professional", "confidence": 0.85},
            {"tag": "business", "confidence": 0.80},
            {"tag": "person", "confidence": 0.90}
        ],
        "colors": [
            {"color": "navy", "frequency": 35},
            {"color": "beige", "frequency": 30},
            {"color": "white", "frequency": 25},
            {"color": "brown", "frequency": 10}
        ]
    }

    @classmethod
    def get_analysis_result(cls, response_type: str = "rose") -> AnalysisResult:
        """Get a mock AnalysisResult object."""
        data_map = {
            "rose": cls.SAMPLE_ANALYSIS_JSON,
            "landscape": cls.SAMPLE_LANDSCAPE_JSON,
            "portrait": cls.SAMPLE_PORTRAIT_JSON
        }

        json_data = data_map.get(response_type, cls.SAMPLE_ANALYSIS_JSON)

        return AnalysisResult(
            description=json_data["description"],
            tags=[TagData(**tag) for tag in json_data["tags"]],
            colors=[ColorData(**color) for color in json_data["colors"]]
        )

    @classmethod
    def get_openai_mock_response(cls, response_type: str = "rose") -> Dict[str, Any]:
        """Get a mock OpenAI API response."""
        analysis = cls.get_analysis_result(response_type)

        class MockChoice:
            class MockMessage:
                content = analysis.model_dump_json()

            message = MockMessage()

        class MockResponse:
            choices = [MockChoice()]

        return MockResponse()


class TestSearchData:
    """Test data for search functionality."""

    @staticmethod
    def create_search_result(
        image_path: str = "/test/path/image1.jpg",
        description: str = "Test image description",
        distance: float = 0.1
    ) -> SearchResult:
        """Create a SearchResult object for testing."""
        return SearchResult(
            image_path=image_path,
            description=description,
            thumbnail=TestImages.create_thumbnail_base64(),
            distance=distance
        )

    @staticmethod
    def create_search_results_list(count: int = 3) -> List[SearchResult]:
        """Create a list of SearchResult objects."""
        results = []
        for i in range(count):
            results.append(
                TestSearchData.create_search_result(
                    image_path=f"/test/path/image{i+1}.jpg",
                    description=f"Test image {i+1} description",
                    distance=0.1 + (i * 0.05)
                )
            )
        return results

    @staticmethod
    def create_mcp_search_result(
        image_path: str = "http://localhost:5173/test/path/image1.jpg",
        description: str = "Test MCP image description"
    ) -> SearchResultsMcp:
        """Create a SearchResultsMcp object for testing."""
        return SearchResultsMcp(
            image_path=image_path,
            description=description
        )

    @staticmethod
    def create_text_search_request(
        search_text: str = "test query",
        multimodal: bool = False,
        threshold: str = "small"
    ) -> TextSearchRequest:
        """Create a TextSearchRequest object for testing."""
        return TextSearchRequest(
            search_text=search_text,
            multimodal=multimodal,
            threshold=threshold
        )


class MockChromaDBData:
    """Mock ChromaDB query responses."""

    @staticmethod
    def create_query_response(
        count: int = 2,
        base_distance: float = 0.1
    ) -> Dict[str, Any]:
        """Create a mock ChromaDB query response."""
        ids = [f"http://localhost:5173/test/image{i+1}.jpg" for i in range(count)]
        distances = [base_distance + (i * 0.05) for i in range(count)]
        documents = [f"Test description for image {i+1}" for i in range(count)]
        metadatas = []

        for i in range(count):
            metadatas.append({
                "tags": f"test,image{i+1},sample",
                "colors": "red,blue,green",
                "thumbnail": TestImages.create_thumbnail_base64(),
                "description": f"Test description for image {i+1}"
            })

        return {
            "ids": [ids],
            "distances": [distances],
            "documents": [documents],
            "metadatas": [metadatas]
        }

    @staticmethod
    def create_empty_response() -> Dict[str, Any]:
        """Create an empty ChromaDB response."""
        return {
            "ids": [[]],
            "distances": [[]],
            "documents": [[]],
            "metadatas": [[]]
        }


class TestFileSystem:
    """Test file system utilities."""

    @staticmethod
    def create_test_images_structure(base_path: str, count: int = 3) -> List[str]:
        """Create a test directory structure with sample images."""
        from pathlib import Path
        import tempfile

        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)

        image_paths = []
        for i in range(count):
            # Create subdirectories
            subdir = base / f"category{i+1}"
            subdir.mkdir(exist_ok=True)

            # Create test image files
            image_path = subdir / f"test_image_{i+1}.jpg"
            test_image = TestImages.create_test_image()
            test_image.save(image_path, format="JPEG")

            image_paths.append(str(image_path))

        return image_paths


# Test constants
TEST_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
TEST_THRESHOLDS = ["small", "medium", "yuge"]
TEST_THUMBNAIL_SIZES = [(200, 200), (150, 150), (100, 100)]

# Sample environment variables for testing
TEST_ENV_VARS = {
    "LLM_MODEL": "test-model",
    "LLM_EMBEDDING_MODEL": "test-embedding-model",
    "LLM_PROVIDER": "test-provider",
    "LLM_URL": "http://localhost:8080",
    "LLM_API_KEY": "test-api-key",
    "HF_TOKEN": "test-hf-token",
    "PHOTOS_BASE_PATH": "/tmp/test-photos",
    "PHOTOS_URL_BASE": "http://localhost:5173",
    "DB_BASE_PATH": "/tmp/test-db",
    "THUMBNAIL_WIDTH": "200",
    "THUMBNAIL_HEIGHT": "200",
    "LOG_LEVEL": "DEBUG",
    "SERVER_HOST": "127.0.0.1",
    "SERVER_PORT": "8000"
}