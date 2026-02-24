"""Pytest configuration and shared fixtures for image-catalog tests."""

import asyncio
import base64
import io
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import BaseModel

from configuration.config import Config
from configuration.logging_config import setup_logging


class TestConfig(BaseModel):
    """Test configuration with safe defaults."""

    llm_model: str = "test-model"
    llm_embedding_model: str = "test-embedding-model"
    llm_provider: str = "test-provider"
    llm_url: str = "http://localhost:8080"
    llm_api_key: str = "test-api-key"
    hf_token: str = "test-hf-token"
    photos_base_path: str = "/tmp/test-photos"
    photos_url_base: str = "http://localhost:5173"
    db_base_path: str = "/tmp/test-db"
    thumbnail_width: int = 200
    thumbnail_height: int = 200
    log_level: str = "DEBUG"
    log_file: str | None = None
    log_json_format: bool = False
    server_host: str = "127.0.0.1"
    server_port: int = 8000


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration."""
    return TestConfig()


@pytest.fixture(autouse=True)
def setup_test_logging(test_config: TestConfig):
    """Setup logging for tests."""
    setup_logging(
        level=test_config.log_level,
        json_format=test_config.log_json_format,
        log_file=test_config.log_file,
    )


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_image() -> Image.Image:
    """Create a sample PIL Image for testing."""
    # Create a simple RGB image
    img = Image.new("RGB", (100, 100), color="red")
    return img


@pytest.fixture
def sample_image_bytes(sample_image: Image.Image) -> bytes:
    """Convert sample image to bytes."""
    buffer = io.BytesIO()
    sample_image.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def sample_image_base64(sample_image_bytes: bytes) -> str:
    """Convert sample image to base64 string."""
    return base64.b64encode(sample_image_bytes).decode("utf-8")


@pytest.fixture
def sample_image_file(temp_dir: Path, sample_image: Image.Image) -> Path:
    """Create a sample image file on disk."""
    image_path = temp_dir / "test_image.jpg"
    sample_image.save(image_path, format="JPEG")
    return image_path


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = MagicMock()

    # Mock structured output parsing
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"description": "A test image", "tags": [{"tag": "test", "confidence": 0.9}], "colors": [{"color": "red", "frequency": 50}]}'

    client.chat.completions.parse.return_value = mock_response
    return client


@pytest.fixture
def mock_async_openai_client():
    """Mock AsyncOpenAI client for testing."""
    client = AsyncMock()

    # Mock structured output parsing
    mock_response = AsyncMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"description": "A test image", "tags": [{"tag": "test", "confidence": 0.9}], "colors": [{"color": "red", "frequency": 50}]}'

    client.chat.completions.parse.return_value = mock_response
    return client


@pytest.fixture
def mock_chromadb_collection():
    """Mock ChromaDB collection for testing."""
    collection = MagicMock()

    # Mock query results
    collection.query.return_value = {
        "ids": [["test_id_1", "test_id_2"]],
        "distances": [[0.1, 0.3]],
        "documents": [["Test description 1", "Test description 2"]],
        "metadatas": [[
            {"tags": "test,image", "colors": "red,blue", "thumbnail": "test_thumbnail_1"},
            {"tags": "sample,photo", "colors": "green,yellow", "thumbnail": "test_thumbnail_2"}
        ]]
    }

    # Mock add operations
    collection.add.return_value = None

    return collection


@pytest.fixture
def mock_config(test_config: TestConfig):
    """Mock configuration for testing."""
    with patch('configuration.config.Config') as mock:
        mock.return_value = test_config
        yield test_config


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client for FastAPI app."""
    # Import here to avoid circular imports
    from server import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_repositories():
    """Mock all repository dependencies."""
    with patch('repository.metadata_repository.description_collection') as mock_desc, \
         patch('repository.multimodal_repository.multimodal_collection') as mock_mm:

        # Configure mock behavior
        mock_desc.query.return_value = {
            "ids": [["test_id"]],
            "distances": [[0.1]],
            "documents": [["Test description"]],
            "metadatas": [[{"thumbnail": "test_thumbnail"}]]
        }

        mock_mm.query.return_value = {
            "ids": [["test_id"]],
            "distances": [[0.1]],
            "documents": [["Test description"]],
            "metadatas": [[{"description": "Test description", "thumbnail": "test_thumbnail"}]]
        }

        yield {"metadata": mock_desc, "multimodal": mock_mm}


# Async test utilities
async def run_async_test(coro):
    """Helper to run async tests in sync context."""
    return await coro


# Custom markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )