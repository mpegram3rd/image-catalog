"""Integration tests for repository layer."""

from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from models.indexing_models import AnalysisResult, TagData, ColorData
from tests.fixtures.test_data import MockChromaDBData, TestImages, MockLLMResponses


class TestSearchTransformer:
    """Test search result transformation."""

    @pytest.mark.integration
    def test_transform_chromadb_results(self):
        """Test transforming ChromaDB results to SearchResult objects."""
        from repository.search_transformer import transform

        # Create mock ChromaDB response
        chromadb_response = MockChromaDBData.create_query_response(2, 0.1)
        threshold = 0.2

        # Transform results
        search_results = transform(chromadb_response, threshold)

        # Verify transformation
        assert len(search_results) == 2
        assert search_results[0].image_path == "http://localhost:5173/test/image1.jpg"
        assert search_results[0].description == "Test description for image 1"
        assert search_results[0].distance == pytest.approx(0.1)
        assert search_results[0].thumbnail.startswith("data:image/png;base64,")

    @pytest.mark.integration
    def test_transform_with_threshold_filtering(self):
        """Test that threshold filtering works correctly."""
        from repository.search_transformer import transform

        # Create response with varying distances
        response = {
            "ids": [["image1", "image2", "image3"]],
            "distances": [[0.05, 0.15, 0.25]],  # Only first two should pass threshold 0.2
            "documents": [["desc1", "desc2", "desc3"]],
            "metadatas": [[
                {"thumbnail": "thumb1"},
                {"thumbnail": "thumb2"},
                {"thumbnail": "thumb3"}
            ]]
        }

        results = transform(response, 0.2)

        # Should only return first two results
        assert len(results) == 2
        assert results[0].distance == pytest.approx(0.05)
        assert results[1].distance == pytest.approx(0.15)


class TestRepositoryIntegration:
    """Test repository integration with mock ChromaDB."""

    @pytest.mark.integration
    @patch('repository.metadata_repository.description_collection')
    def test_metadata_repository_search(self, mock_collection):
        """Test metadata repository search functionality."""
        from repository.metadata_repository import find_by_text

        # Configure mock
        mock_collection.query.return_value = MockChromaDBData.create_query_response(1, 0.1)

        # Perform search
        results = find_by_text("test query", 0.2)

        # Verify query was called
        mock_collection.query.assert_called_once_with(query_texts=["test query"])

        # Verify results
        assert len(results) == 1
        assert results[0].description == "Test description for image 1"

    @pytest.mark.integration
    @patch('repository.multimodal_repository.multimodal_collection')
    def test_multimodal_repository_image_search(self, mock_collection):
        """Test multimodal repository image search."""
        from repository.multimodal_repository import find_by_image
        import numpy as np

        # Configure mock
        mock_collection.query.return_value = MockChromaDBData.create_query_response(1, 0.1)

        # Create test image
        test_image = TestImages.create_test_image()

        # Perform search
        results = find_by_image(test_image, 0.2)

        # Verify query was called with image array
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert "query_images" in call_args.kwargs
        assert len(call_args.kwargs["query_images"]) == 1
        assert isinstance(call_args.kwargs["query_images"][0], np.ndarray)

        # Verify results
        assert len(results) == 1

    @pytest.mark.integration
    @patch('repository.multimodal_repository.multimodal_collection')
    def test_multimodal_repository_text_search(self, mock_collection):
        """Test multimodal repository text search."""
        from repository.multimodal_repository import find_by_text_mm

        # Configure mock
        mock_collection.query.return_value = MockChromaDBData.create_query_response(2, 0.05)

        # Perform search
        results = find_by_text_mm("landscape", 0.1)

        # Verify query was called
        mock_collection.query.assert_called_once_with(query_texts=["landscape"])

        # Verify results
        assert len(results) == 2

    @pytest.mark.integration
    @patch('repository.metadata_repository.description_collection')
    def test_metadata_repository_add_analysis(self, mock_collection):
        """Test adding analysis to metadata repository."""
        from repository.metadata_repository import add_analysis

        # Create test data
        analysis = MockLLMResponses.get_analysis_result("rose")
        thumbnail = TestImages.create_thumbnail_base64()
        image_path = "/tmp/test/image.jpg"

        # Add analysis
        add_analysis(image_path, analysis, thumbnail)

        # Verify add was called
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args

        # Check arguments
        assert len(call_args.kwargs["ids"]) == 1
        assert len(call_args.kwargs["documents"]) == 1
        assert len(call_args.kwargs["metadatas"]) == 1

        # Verify document content
        assert call_args.kwargs["documents"][0] == analysis.description

        # Verify metadata structure
        metadata = call_args.kwargs["metadatas"][0]
        assert "tags" in metadata
        assert "colors" in metadata
        assert "thumbnail" in metadata