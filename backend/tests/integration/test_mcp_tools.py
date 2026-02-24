"""Integration tests for MCP tools."""

from unittest.mock import AsyncMock, patch

import pytest

from models.api_models import TextSearchRequest
from tests.fixtures.test_data import MockChromaDBData, TestSearchData


class TestMCPToolsIntegration:
    """Test MCP tools integration."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_find_by_text_mcp_success(self, mock_repositories):
        """Test MCP text search tool with successful results."""
        from mcp_tools.image_catalog_mcp import find_by_text_mcp

        # Configure mock to return search results
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_query_response(2, 0.1)

        # Mock the search_by_text function
        with patch('mcp_tools.image_catalog_mcp.search_by_text') as mock_search:
            # Create mock search results
            search_results = TestSearchData.create_search_results_list(2)
            mock_search.return_value = search_results

            # Call MCP function
            results = await find_by_text_mcp("test query")

            # Verify search was called with correct parameters
            mock_search.assert_called_once()
            call_args = mock_search.call_args[0][0]  # First argument (TextSearchRequest)
            assert isinstance(call_args, TextSearchRequest)
            assert call_args.search_text == "test query"
            assert call_args.threshold == "yuge"
            assert call_args.multimodal is True

            # Verify results are converted to MCP format
            assert len(results) == 2
            for i, result in enumerate(results):
                assert result.image_path.startswith("http://localhost:5173/")
                assert result.description == f"Test image {i+1} description"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_find_by_text_mcp_empty_results(self, mock_repositories):
        """Test MCP text search with no results."""
        from mcp_tools.image_catalog_mcp import find_by_text_mcp

        # Configure mock for empty results
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_empty_response()

        with patch('mcp_tools.image_catalog_mcp.search_by_text') as mock_search:
            mock_search.return_value = []

            results = await find_by_text_mcp("nonexistent query")

            assert len(results) == 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_find_displayable_images_mcp_success(self, mock_repositories):
        """Test MCP displayable image search tool."""
        from mcp_tools.image_catalog_mcp import find_displayable_images_mcp

        # Configure mock
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_query_response(1, 0.05)

        with patch('mcp_tools.image_catalog_mcp.search_by_text') as mock_search:
            # Create mock search results with thumbnails
            search_results = TestSearchData.create_search_results_list(1)
            mock_search.return_value = search_results

            # Call MCP function
            results = await find_displayable_images_mcp("test query")

            # Verify search was called with "small" threshold
            call_args = mock_search.call_args[0][0]
            assert call_args.threshold == "small"
            assert call_args.multimodal is True

            # Verify results are Image objects
            assert len(results) == 1
            # Note: The actual Image type checking would depend on FastMCP's Image type

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_url_conversion(self, mock_repositories):
        """Test that MCP tools convert relative paths to full URLs."""
        from mcp_tools.image_catalog_mcp import find_by_text_mcp

        with patch('mcp_tools.image_catalog_mcp.search_by_text') as mock_search:
            # Create search result with relative path
            search_result = TestSearchData.create_search_result(
                image_path="/relative/path/image.jpg",
                description="Test image"
            )
            mock_search.return_value = [search_result]

            results = await find_by_text_mcp("test")

            # Verify URL conversion
            assert len(results) == 1
            assert results[0].image_path == "http://localhost:5173//relative/path/image.jpg"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_tools_error_handling(self, mock_repositories):
        """Test MCP tools error handling."""
        from mcp_tools.image_catalog_mcp import find_by_text_mcp

        with patch('mcp_tools.image_catalog_mcp.search_by_text') as mock_search:
            # Simulate an exception in search
            mock_search.side_effect = Exception("Search failed")

            # The exception should be propagated
            with pytest.raises(Exception, match="Search failed"):
                await find_by_text_mcp("test query")


class TestMCPIntegrationWithAPI:
    """Test MCP tools integration with API layer."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_calls_api_correctly(self, mock_repositories):
        """Test that MCP tools call the API layer correctly."""
        from mcp_tools.image_catalog_mcp import find_by_text_mcp

        # This test ensures the integration between MCP tools and API routes
        mock_repositories["multimodal"].query.return_value = MockChromaDBData.create_query_response(1, 0.1)

        # Import the actual search function to ensure integration
        with patch('api_routes.image_catalog_router.find_by_text_mm') as mock_repo_search:
            mock_repo_search.return_value = TestSearchData.create_search_results_list(1)

            results = await find_by_text_mcp("integration test")

            # Verify the repository search was called through the API
            mock_repo_search.assert_called_once()

            # Verify results
            assert len(results) == 1