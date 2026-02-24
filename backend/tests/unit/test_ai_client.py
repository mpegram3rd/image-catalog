"""Unit tests for AI client provider functionality."""

from unittest.mock import MagicMock, patch

import pytest
from openai import AsyncOpenAI, OpenAI

from ai.client_provider import get_async_client, get_client
from tests.conftest import TestConfig


class TestClientProvider:
    """Test AI client provider functionality."""

    def setup_method(self):
        """Reset client cache before each test."""
        # Import and reset the cache
        from ai import client_provider

        client_provider.client_cache = {"sync": None, "async": None}

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.OpenAI")
    def test_get_client_creates_new_client(self, mock_openai_class, mock_config):
        """Test that get_client creates a new OpenAI client."""
        # Setup mock config
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        # Setup mock OpenAI class
        mock_client = MagicMock(spec=OpenAI)
        mock_openai_class.return_value = mock_client

        # Call get_client
        result = get_client()

        # Verify OpenAI was called with correct parameters
        mock_openai_class.assert_called_once_with(
            base_url=test_config.llm_url, api_key=test_config.llm_api_key
        )

        # Verify result
        assert result is mock_client

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.OpenAI")
    def test_get_client_caches_client(self, mock_openai_class, mock_config):
        """Test that get_client caches the created client."""
        # Setup mocks
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        mock_client = MagicMock(spec=OpenAI)
        mock_openai_class.return_value = mock_client

        # First call
        result1 = get_client()

        # Second call
        result2 = get_client()

        # OpenAI should only be called once (caching)
        mock_openai_class.assert_called_once()

        # Both results should be the same cached instance
        assert result1 is result2
        assert result1 is mock_client

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.logger")
    @patch("ai.client_provider.OpenAI")
    def test_get_client_logs_creation(self, mock_openai_class, mock_logger, mock_config):
        """Test that get_client logs client creation."""
        # Setup mocks
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        mock_client = MagicMock(spec=OpenAI)
        mock_openai_class.return_value = mock_client

        # Call get_client
        get_client()

        # Verify logging
        mock_logger.debug.assert_called_once_with(
            "Creating new sync OpenAI client",
            extra={
                "provider": test_config.llm_provider,
                "base_url": test_config.llm_url,
            },
        )

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.AsyncOpenAI")
    def test_get_async_client_creates_new_client(self, mock_async_openai_class, mock_config):
        """Test that get_async_client creates a new AsyncOpenAI client."""
        # Setup mock config
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        # Setup mock AsyncOpenAI class
        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_async_openai_class.return_value = mock_client

        # Call get_async_client
        result = get_async_client()

        # Verify AsyncOpenAI was called with correct parameters
        mock_async_openai_class.assert_called_once_with(
            base_url=test_config.llm_url, api_key=test_config.llm_api_key
        )

        # Verify result
        assert result is mock_client

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.AsyncOpenAI")
    def test_get_async_client_caches_client(self, mock_async_openai_class, mock_config):
        """Test that get_async_client caches the created client."""
        # Setup mocks
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_async_openai_class.return_value = mock_client

        # First call
        result1 = get_async_client()

        # Second call
        result2 = get_async_client()

        # AsyncOpenAI should only be called once (caching)
        mock_async_openai_class.assert_called_once()

        # Both results should be the same cached instance
        assert result1 is result2
        assert result1 is mock_client

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.logger")
    @patch("ai.client_provider.AsyncOpenAI")
    def test_get_async_client_logs_creation(
        self, mock_async_openai_class, mock_logger, mock_config
    ):
        """Test that get_async_client logs client creation."""
        # Setup mocks
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_async_openai_class.return_value = mock_client

        # Call get_async_client
        get_async_client()

        # Verify logging
        mock_logger.debug.assert_called_once_with(
            "Creating new async OpenAI client",
            extra={
                "provider": test_config.llm_provider,
                "base_url": test_config.llm_url,
            },
        )

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.OpenAI")
    @patch("ai.client_provider.AsyncOpenAI")
    def test_sync_and_async_clients_are_independent(
        self, mock_async_openai, mock_openai, mock_config
    ):
        """Test that sync and async clients are cached independently."""
        # Setup mocks
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        mock_sync_client = MagicMock(spec=OpenAI)
        mock_async_client = MagicMock(spec=AsyncOpenAI)
        mock_openai.return_value = mock_sync_client
        mock_async_openai.return_value = mock_async_client

        # Get both clients
        sync_result = get_client()
        async_result = get_async_client()

        # Both should be called once
        mock_openai.assert_called_once()
        mock_async_openai.assert_called_once()

        # Results should be different objects
        assert sync_result is not async_result
        assert sync_result is mock_sync_client
        assert async_result is mock_async_client

        # Subsequent calls should return cached instances
        sync_result2 = get_client()
        async_result2 = get_async_client()

        assert sync_result2 is sync_result
        assert async_result2 is async_result

        # No additional calls should be made
        assert mock_openai.call_count == 1
        assert mock_async_openai.call_count == 1

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.OpenAI")
    def test_get_client_with_different_configs(self, mock_openai_class, mock_config):
        """Test that get_client works with different configuration values."""
        # Test different URL formats
        test_urls = ["http://localhost:8080", "https://api.openai.com", "http://127.0.0.1:11434"]

        for url in test_urls:
            # Reset cache
            from ai import client_provider

            client_provider.client_cache = {"sync": None, "async": None}

            # Setup mock config
            mock_config.llm_provider = "test-provider"
            mock_config.llm_url = url
            mock_config.llm_api_key = "test-key"

            mock_client = MagicMock(spec=OpenAI)
            mock_openai_class.return_value = mock_client

            # Call get_client
            result = get_client()

            # Verify correct URL was used
            mock_openai_class.assert_called_with(base_url=url, api_key="test-key")
            assert result is mock_client

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    def test_config_module_import(self, mock_config):
        """Test that config is properly imported and used."""
        # This test ensures the config is imported at module level
        # and used correctly in the functions

        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        with patch("ai.client_provider.OpenAI") as mock_openai:
            mock_client = MagicMock(spec=OpenAI)
            mock_openai.return_value = mock_client

            get_client()

            # Verify config values were used
            mock_openai.assert_called_once_with(
                base_url=test_config.llm_url, api_key=test_config.llm_api_key
            )

    @pytest.mark.unit
    def test_client_cache_structure(self):
        """Test that client cache has the expected structure."""
        from ai import client_provider

        # Reset cache
        client_provider.client_cache = {"sync": None, "async": None}

        # Verify initial structure
        assert "sync" in client_provider.client_cache
        assert "async" in client_provider.client_cache
        assert client_provider.client_cache["sync"] is None
        assert client_provider.client_cache["async"] is None

    @pytest.mark.unit
    @patch("ai.client_provider.config")
    @patch("ai.client_provider.OpenAI")
    def test_openai_import_error_handling(self, mock_openai_class, mock_config):
        """Test handling of OpenAI import/creation errors."""
        # Setup config
        test_config = TestConfig()
        mock_config.llm_provider = test_config.llm_provider
        mock_config.llm_url = test_config.llm_url
        mock_config.llm_api_key = test_config.llm_api_key

        # Mock OpenAI to raise an exception
        mock_openai_class.side_effect = Exception("OpenAI initialization failed")

        # The exception should be propagated
        with pytest.raises(Exception, match="OpenAI initialization failed"):
            get_client()

    @pytest.mark.unit
    def test_module_level_imports(self):
        """Test that all required modules are imported correctly."""
        # This is primarily a smoke test to ensure imports work
        from ai.client_provider import client_cache, config, get_async_client, get_client, logger

        # Basic type/existence checks
        assert callable(get_client)
        assert callable(get_async_client)
        assert config is not None
        assert logger is not None
        assert isinstance(client_cache, dict)
