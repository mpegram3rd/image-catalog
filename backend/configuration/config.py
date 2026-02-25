"""Configuration management with validation and environment support."""

import os
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Supported log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class Config(BaseSettings):
    """Application configuration with validation and environment support.

    This class manages all application configuration with proper validation,
    sensible defaults, and support for multiple environments.
    """

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment (development, test, production)",
    )

    # LLM Configuration
    llm_model: str = Field(
        ...,
        min_length=1,
        description="LLM model name for image analysis",
    )
    llm_embedding_model: str = Field(
        ...,
        min_length=1,
        description="Model name for text embeddings",
    )
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider (openai, anthropic, azure, local)",
    )
    llm_url: str = Field(
        ...,
        description="LLM API endpoint URL",
    )
    llm_api_key: str = Field(
        ...,
        min_length=1,
        description="API key for LLM service",
    )
    llm_timeout: int = Field(
        default=30,
        gt=0,
        le=300,
        description="LLM API timeout in seconds",
    )
    llm_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of LLM API retries",
    )

    # Hugging Face Configuration
    hf_token: str = Field(
        ...,
        min_length=1,
        description="Hugging Face API token for embeddings",
    )

    # File System Configuration
    photos_base_path: Annotated[Path, Field(description="Base path for photo storage")]
    photos_url_base: str = Field(
        ...,
        description="Base URL for serving photos",
    )
    db_base_path: Annotated[Path, Field(description="Base path for database storage")]

    # Image Processing Configuration
    thumbnail_width: int = Field(
        default=200,
        gt=0,
        le=1000,
        description="Thumbnail width in pixels",
    )
    thumbnail_height: int = Field(
        default=200,
        gt=0,
        le=1000,
        description="Thumbnail height in pixels",
    )
    max_image_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        gt=0,
        description="Maximum image file size in bytes",
    )
    supported_formats: List[str] = Field(
        default=[".jpg", ".jpeg", ".png"],
        description="Supported image file formats",
    )

    # Database Configuration
    chroma_host: str = Field(
        default="localhost",
        description="ChromaDB host",
    )
    chroma_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="ChromaDB port",
    )
    chroma_collection_prefix: str = Field(
        default="image_catalog",
        min_length=1,
        description="Prefix for ChromaDB collections",
    )

    # Logging Configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Application log level",
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (None for console only)",
    )
    log_json_format: bool = Field(
        default=False,
        description="Use JSON format for structured logging",
    )
    log_max_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        gt=0,
        description="Maximum log file size in bytes",
    )
    log_backup_count: int = Field(
        default=5,
        ge=0,
        description="Number of log backup files to keep",
    )

    # Server Configuration
    server_host: str = Field(
        default="127.0.0.1",
        description="Server bind address",
    )
    server_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="Server port",
    )
    server_workers: int = Field(
        default=1,
        gt=0,
        le=32,
        description="Number of server workers",
    )
    cors_origins: List[str] = Field(
        default=["*"],
        description="CORS allowed origins",
    )
    cors_credentials: bool = Field(
        default=True,
        description="Allow CORS credentials",
    )

    # Search Configuration
    default_search_threshold: str = Field(
        default="medium",
        description="Default search similarity threshold",
    )
    max_search_results: int = Field(
        default=100,
        gt=0,
        le=1000,
        description="Maximum number of search results",
    )

    # Performance Configuration
    max_concurrent_indexing: int = Field(
        default=3,
        gt=0,
        le=20,
        description="Maximum concurrent indexing operations",
    )
    max_concurrent_searches: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Maximum concurrent search operations",
    )

    # Development Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload in development",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @field_validator("photos_base_path", mode="before")
    @classmethod
    def validate_photos_path(cls, v: Union[str, Path]) -> Path:
        """Validate and convert photos base path."""
        path = Path(v)
        # In production, paths might not exist yet and will be created at runtime
        if not str(path).startswith("/app/") and not path.exists():
            raise ValueError(f"Photos base path does not exist: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Photos base path is not a directory: {path}")
        return path.resolve() if path.exists() else path

    @field_validator("db_base_path", mode="before")
    @classmethod
    def validate_db_path(cls, v: Union[str, Path]) -> Path:
        """Validate and convert database base path."""
        path = Path(v)
        # In production environments, we might not have permission to create directories
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path.resolve()
        except OSError:
            # Return the path as-is if we can't create it (e.g., in production validation)
            return path

    @field_validator("llm_url")
    @classmethod
    def validate_llm_url(cls, v: str) -> str:
        """Validate LLM URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("LLM URL must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("photos_url_base")
    @classmethod
    def validate_photos_url_base(cls, v: str) -> str:
        """Validate photos URL base format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Photos URL base must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("supported_formats")
    @classmethod
    def validate_supported_formats(cls, v: List[str]) -> List[str]:
        """Validate supported image formats."""
        formats = [fmt.lower() if fmt.startswith(".") else f".{fmt.lower()}" for fmt in v]
        valid_formats = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        invalid = set(formats) - valid_formats
        if invalid:
            raise ValueError(f"Unsupported image formats: {invalid}")
        return formats

    @model_validator(mode="after")
    def validate_thumbnail_dimensions(self) -> "Config":
        """Validate thumbnail dimensions are reasonable."""
        if self.thumbnail_width > 1000 or self.thumbnail_height > 1000:
            raise ValueError("Thumbnail dimensions should not exceed 1000x1000")
        return self

    @model_validator(mode="after")
    def validate_environment_specific_settings(self) -> "Config":
        """Apply environment-specific validation and defaults."""
        if self.environment == Environment.PRODUCTION:
            if self.debug:
                raise ValueError("Debug mode should not be enabled in production")
            if self.server_host == "0.0.0.0":
                # Allow in production but warn
                pass
            if self.log_level == LogLevel.DEBUG:
                # Upgrade to INFO in production
                self.log_level = LogLevel.INFO
        elif self.environment == Environment.DEVELOPMENT:
            # Enable debug features in development
            self.debug = True
            self.reload = True
        elif self.environment == Environment.TEST:
            # Test-specific settings
            self.log_level = LogLevel.WARNING
            self.debug = False
            self.reload = False

        return self

    def get_chroma_settings(self) -> Dict[str, Any]:
        """Get ChromaDB connection settings."""
        return {
            "host": self.chroma_host,
            "port": self.chroma_port,
            "collection_prefix": self.chroma_collection_prefix,
        }

    def get_server_settings(self) -> Dict[str, Any]:
        """Get server configuration settings."""
        return {
            "host": self.server_host,
            "port": self.server_port,
            "workers": self.server_workers,
            "debug": self.debug,
            "reload": self.reload,
        }

    def get_cors_settings(self) -> Dict[str, Any]:
        """Get CORS configuration settings."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    def get_llm_settings(self) -> Dict[str, Any]:
        """Get LLM configuration settings."""
        return {
            "model": self.llm_model,
            "embedding_model": self.llm_embedding_model,
            "provider": self.llm_provider.value,
            "url": self.llm_url,
            "api_key": self.llm_api_key,
            "timeout": self.llm_timeout,
            "max_retries": self.llm_max_retries,
        }

    def validate_configuration(self) -> List[str]:
        """Validate the complete configuration and return any warnings."""
        warnings = []

        # Check for development settings in production
        if self.environment == Environment.PRODUCTION:
            if self.server_host in ("0.0.0.0", "*"):
                warnings.append("Server is bound to all interfaces in production")
            if self.cors_origins == ["*"]:
                warnings.append("CORS allows all origins in production")

        # Check file system permissions
        try:
            test_file = self.db_base_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception:
            warnings.append(f"Database path may not be writable: {self.db_base_path}")

        # Check if paths are reasonable
        if self.max_image_size > 100 * 1024 * 1024:  # 100MB
            warnings.append("Maximum image size is very large")

        return warnings

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == Environment.TEST

    @classmethod
    def create_for_environment(
        cls,
        env: Environment,
        env_file: Optional[str] = None,
        **overrides: Any,
    ) -> "Config":
        """Create configuration for a specific environment.

        Args:
            env: Target environment
            env_file: Optional environment file path
            **overrides: Configuration overrides

        Returns:
            Configured Config instance
        """
        if env_file is None:
            env_file = f".env.{env.value}"
            if not os.path.exists(env_file):
                env_file = ".env"

        # Set environment in overrides
        overrides["environment"] = env

        # Create temporary instance to validate
        config = cls(_env_file=env_file, **overrides)
        return config

    def __repr__(self) -> str:
        """String representation hiding sensitive information."""
        return (
            f"Config(environment={self.environment.value}, "
            f"llm_provider={self.llm_provider.value}, "
            f"server={self.server_host}:{self.server_port})"
        )
