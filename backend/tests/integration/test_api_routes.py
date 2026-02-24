"""Integration tests for API routes."""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.fixtures.test_data import TestImages, TestSearchData, MockChromaDBData


class TestImageSearchAPI:
    """Test image search API endpoint."""

    @pytest.mark.integration
    def test_search_by_image_success(self, client: TestClient, mock_repositories):
        """Test successful image search."""
        # Create test image file
        test_image = TestImages.create_test_image(100, 100, "red")
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Configure mock response
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_query_response(2)

        # Make request
        response = client.post(
            "/api/search/image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        for result in data:
            assert "image_path" in result
            assert "description" in result
            assert "thumbnail" in result
            assert "distance" in result

    @pytest.mark.integration
    def test_search_by_image_empty_results(self, client: TestClient, mock_repositories):
        """Test image search with no results."""
        test_image = TestImages.create_test_image()
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Configure mock for empty results
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_empty_response()

        response = client.post(
            "/api/search/image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.integration
    def test_search_by_image_invalid_file(self, client: TestClient):
        """Test image search with invalid file."""
        # Send non-image file
        text_content = io.BytesIO(b"This is not an image")

        response = client.post(
            "/api/search/image",
            files={"file": ("test.txt", text_content, "text/plain")}
        )

        # Should return an error (PIL will fail to open)
        assert response.status_code == 500 or response.status_code == 422


class TestTextSearchAPI:
    """Test text search API endpoint."""

    @pytest.mark.integration
    def test_search_by_text_success(self, client: TestClient, mock_repositories):
        """Test successful text search."""
        # Configure mock response
        mock_repositories["metadata"].query.return_value = MockChromaDBData.create_query_response(3)

        search_request = {
            "search_text": "red flower",
            "multimodal": False,
            "threshold": "medium"
        }

        response = client.post("/api/search/text", json=search_request)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.integration
    def test_search_by_text_multimodal(self, client: TestClient, mock_repositories):
        """Test multimodal text search."""
        # Configure mock response
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_query_response(2)

        search_request = {
            "search_text": "mountain landscape",
            "multimodal": True,
            "threshold": "small"
        }

        response = client.post("/api/search/text", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.integration
    def test_search_by_text_validation_error(self, client: TestClient):
        """Test text search with validation errors."""
        # Missing required field
        invalid_request = {
            "multimodal": False,
            "threshold": "small"
            # missing search_text
        }

        response = client.post("/api/search/text", json=invalid_request)
        assert response.status_code == 422

        # Invalid threshold
        invalid_request = {
            "search_text": "test",
            "threshold": "invalid_threshold"
        }

        response = client.post("/api/search/text", json=invalid_request)
        assert response.status_code == 422

    @pytest.mark.integration
    def test_search_by_text_empty_query(self, client: TestClient):
        """Test text search with empty query."""
        search_request = {
            "search_text": "",
            "multimodal": False
        }

        response = client.post("/api/search/text", json=search_request)
        assert response.status_code == 422