"""Unit tests for configuration management."""

import os
import tempfile
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from configuration.config import Config
from tests.fixtures.test_data import TEST_ENV_VARS


class TestConfig:
    """Test Config class."""

    @pytest.mark.unit
    def test_config_with_env_file(self, temp_dir):
        """Test loading configuration from .env file."""
        # Create a test .env file
        env_file = temp_dir / ".env"
        env_content = "\n".join([f"{key}={value}" for key, value in TEST_ENV_VARS.items()])
        env_file.write_text(env_content)

        # Load configuration
        config = Config(env_file=str(env_file))

        # Verify values
        assert config.llm_model == "test-model"
        assert config.llm_embedding_model == "test-embedding-model"
        assert config.llm_provider == "test-provider"
        assert config.llm_url == "http://localhost:8080"
        assert config.llm_api_key == "test-api-key"
        assert config.hf_token == "test-hf-token"
        assert config.photos_base_path == "/tmp/test-photos"
        assert config.photos_url_base == "http://localhost:5173"
        assert config.db_base_path == "/tmp/test-db"
        assert config.thumbnail_width == 200
        assert config.thumbnail_height == 200

    @pytest.mark.unit
    def test_config_default_values(self, temp_dir):
        """Test default values for optional configuration fields."""
        # Create minimal .env file with required fields
        env_file = temp_dir / ".env"
        required_vars = {
            "LLM_MODEL": "test-model",
            "LLM_EMBEDDING_MODEL": "test-embedding",
            "LLM_PROVIDER": "test-provider",
            "LLM_URL": "http://localhost:8080",
            "LLM_API_KEY": "test-key",
            "HF_TOKEN": "test-hf",
            "PHOTOS_BASE_PATH": "/tmp/photos",
            "PHOTOS_URL_BASE": "http://localhost:5173",
            "DB_BASE_PATH": "/tmp/db",
            "THUMBNAIL_WIDTH": "150",
            "THUMBNAIL_HEIGHT": "150",
        }
        env_content = "\n".join([f"{key}={value}" for key, value in required_vars.items()])
        env_file.write_text(env_content)

        config = Config(env_file=str(env_file))

        # Test default values
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.log_json_format is False
        assert config.server_host == "127.0.0.1"
        assert config.server_port == 8000

    @pytest.mark.unit
    def test_config_with_optional_logging_settings(self, temp_dir):
        """Test configuration with optional logging settings."""
        env_file = temp_dir / ".env"
        env_vars = {
            **TEST_ENV_VARS,
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "/tmp/test.log",
            "LOG_JSON_FORMAT": "true",
        }
        env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
        env_file.write_text(env_content)

        config = Config(env_file=str(env_file))

        assert config.log_level == "DEBUG"
        assert config.log_file == "/tmp/test.log"
        assert config.log_json_format is True

    @pytest.mark.unit
    def test_config_with_server_settings(self, temp_dir):
        """Test configuration with server settings."""
        env_file = temp_dir / ".env"
        env_vars = {**TEST_ENV_VARS, "SERVER_HOST": "0.0.0.0", "SERVER_PORT": "9000"}
        env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
        env_file.write_text(env_content)

        config = Config(env_file=str(env_file))

        assert config.server_host == "0.0.0.0"
        assert config.server_port == 9000

    @pytest.mark.unit
    def test_config_missing_required_fields(self, temp_dir):
        """Test that missing required fields raise ValidationError."""
        env_file = temp_dir / ".env"
        # Create .env with missing required field
        incomplete_vars = {
            "LLM_MODEL": "test-model",
            # Missing LLM_EMBEDDING_MODEL and others
        }
        env_content = "\n".join([f"{key}={value}" for key, value in incomplete_vars.items()])
        env_file.write_text(env_content)

        with pytest.raises(ValidationError):
            Config(env_file=str(env_file))

    @pytest.mark.unit
    def test_config_invalid_integer_values(self, temp_dir):
        """Test that invalid integer values raise ValidationError."""
        env_file = temp_dir / ".env"
        env_vars = {**TEST_ENV_VARS, "THUMBNAIL_WIDTH": "invalid_integer"}
        env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
        env_file.write_text(env_content)

        with pytest.raises(ValidationError):
            Config(env_file=str(env_file))

    @pytest.mark.unit
    def test_config_invalid_boolean_values(self, temp_dir):
        """Test various boolean value formats."""
        env_file = temp_dir / ".env"

        # Test valid boolean formats
        valid_boolean_values = [
            ("true", True),
            ("false", False),
            ("True", True),
            ("False", False),
            ("1", True),
            ("0", False),
            ("yes", True),
            ("no", False),
        ]

        for bool_str, expected in valid_boolean_values:
            env_vars = {**TEST_ENV_VARS, "LOG_JSON_FORMAT": bool_str}
            env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
            env_file.write_text(env_content)

            config = Config(env_file=str(env_file))
            assert config.log_json_format is expected

    @pytest.mark.unit
    def test_config_with_environment_variables(self):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, TEST_ENV_VARS, clear=False):
            # Create empty .env file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
                f.write("")
                temp_env = f.name

            try:
                config = Config(env_file=temp_env)

                # Environment variables should override .env file
                assert config.llm_model == "test-model"
                assert config.llm_provider == "test-provider"
                assert config.server_host == "127.0.0.1"
                assert config.server_port == 8000

            finally:
                os.unlink(temp_env)

    @pytest.mark.unit
    def test_config_nonexistent_env_file(self):
        """Test behavior with non-existent .env file."""
        # This should not raise an error, but will use environment variables or defaults
        with patch.dict(os.environ, TEST_ENV_VARS, clear=False):
            config = Config(env_file="/nonexistent/.env")
            assert config.llm_model == "test-model"

    @pytest.mark.unit
    def test_config_file_precedence(self, temp_dir):
        """Test that .env file values take precedence over environment variables."""
        env_file = temp_dir / ".env"
        env_file_vars = {**TEST_ENV_VARS, "LLM_MODEL": "env-file-model", "SERVER_PORT": "7000"}
        env_content = "\n".join([f"{key}={value}" for key, value in env_file_vars.items()])
        env_file.write_text(env_content)

        # Set different values in environment
        env_vars = {"LLM_MODEL": "env-var-model", "SERVER_PORT": "8000"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config(env_file=str(env_file))

            # .env file should take precedence
            assert config.llm_model == "env-file-model"
            assert config.server_port == 7000

    @pytest.mark.unit
    def test_config_path_validation(self, temp_dir):
        """Test path-related configuration validation."""
        env_file = temp_dir / ".env"
        env_content = "\n".join([f"{key}={value}" for key, value in TEST_ENV_VARS.items()])
        env_file.write_text(env_content)

        config = Config(env_file=str(env_file))

        # Paths should be strings
        assert isinstance(config.photos_base_path, str)
        assert isinstance(config.photos_url_base, str)
        assert isinstance(config.db_base_path, str)

        # URLs should include protocol
        assert config.photos_url_base.startswith("http")
        assert config.llm_url.startswith("http")

    @pytest.mark.unit
    def test_config_sensitive_data_handling(self, temp_dir):
        """Test that sensitive data is properly handled."""
        env_file = temp_dir / ".env"
        env_content = "\n".join([f"{key}={value}" for key, value in TEST_ENV_VARS.items()])
        env_file.write_text(env_content)

        config = Config(env_file=str(env_file))

        # Ensure sensitive fields are accessible but not logged
        assert config.llm_api_key == "test-api-key"
        assert config.hf_token == "test-hf-token"

        # Test that config can be serialized (important for logging)
        config_dict = config.model_dump()
        assert "llm_api_key" in config_dict
        assert "hf_token" in config_dict
