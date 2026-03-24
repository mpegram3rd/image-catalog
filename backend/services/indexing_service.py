"""Indexing service for managing the image indexing pipeline."""

import asyncio
import time
from pathlib import Path
from typing import Optional

from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL

from ai.client_provider import get_client
from ai.prompt_provider import PromptProvider
from configuration.config import Config
from configuration.logging_config import get_logger, log_performance
from core.exceptions import AIServiceError, ValidationError
from core.retry import AI_SERVICE_RETRY, ai_service_circuit_breaker, retry_on_failure
from models.indexing_models import AnalysisResult
from services.image_service import ImageService

logger = get_logger(__name__)


class IndexingService:
    """Service for managing the image indexing pipeline.

    This service coordinates the entire indexing process from image processing
    through AI analysis to storage in the search repositories.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        image_service: Optional[ImageService] = None,
        metadata_repository=None,
        multimodal_repository=None,
    ):
        """Initialize the indexing service.

        Args:
            config: Application configuration
            image_service: Image processing service
            metadata_repository: Repository for metadata storage
            multimodal_repository: Repository for multimodal storage
        """
        self.config = config or Config()
        self.image_service = image_service or ImageService(
            thumbnail_width=self.config.thumbnail_width,
            thumbnail_height=self.config.thumbnail_height,
        )
        self.metadata_repository = metadata_repository
        self.multimodal_repository = multimodal_repository

        # Initialize AI components
        self.client = None
        self.prompt_provider = None
        self._analysis_prompt = None

    async def initialize(self) -> None:
        """Initialize AI components and load prompts.

        This method should be called before using the indexing service.

        Raises:
            ConfigurationError: If configuration is invalid
            AIServiceError: If AI service initialization fails
        """
        try:
            logger.info("Initializing indexing service")

            # Initialize AI client
            self.client = get_client()

            # Initialize prompt provider and load analysis prompt
            self.prompt_provider = PromptProvider("ai/prompts")
            self._analysis_prompt = await self.prompt_provider.get_prompt_async("image-analysis")

            logger.info(
                "Indexing service initialized successfully",
                extra={
                    "llm_model": self.config.llm_model,
                    "llm_provider": self.config.llm_provider,
                    "prompt_loaded": bool(self._analysis_prompt),
                },
            )

        except Exception as e:
            logger.error("Failed to initialize indexing service", extra={"error": str(e)})
            raise AIServiceError(
                "Failed to initialize indexing service",
                service="indexing",
                context={"llm_model": self.config.llm_model},
            ) from e

    @retry_on_failure(AI_SERVICE_RETRY, "analyze_image")
    @ai_service_circuit_breaker
    async def analyze_image(self, base64_image_data: str) -> AnalysisResult:
        """Analyze an image using AI to extract description, tags, and colors.

        Args:
            base64_image_data: Base64 encoded image data

        Returns:
            Analysis results with description, tags, and colors

        Raises:
            ValidationError: If image data is invalid
            AIServiceError: If AI analysis fails
        """
        if not base64_image_data:
            raise ValidationError(
                "Image data is required for analysis",
                field="base64_image_data",
                context={"size": len(base64_image_data) if base64_image_data else 0},
            )

        if not self.client:
            raise AIServiceError(
                "AI client not initialized",
                service="openai",
                context={"operation": "analyze_image"},
            )

        if not self._analysis_prompt:
            raise AIServiceError(
                "Analysis prompt not loaded",
                service="indexing",
                context={"operation": "analyze_image"},
            )

        start_time = time.time()

        try:
            logger.debug(
                "Starting image analysis",
                extra={
                    "data_size_kb": len(base64_image_data) / 1024,
                    "model": self.config.llm_model,
                },
            )

            # Prepare the message for the AI model
            message = ChatCompletionUserMessageParam(
                role="user",
                content=[
                    ChatCompletionContentPartTextParam(type="text", text=self._analysis_prompt),
                    ChatCompletionContentPartImageParam(
                        type="image_url",
                        image_url=ImageURL(url=f"data:image/jpeg;base64,{base64_image_data}"),
                    ),
                ],
            )

            # Call the AI model
            response = self.client.chat.completions.parse(
                model=self.config.llm_model,
                response_format=AnalysisResult,
                messages=[message],
            )

            # Extract and validate the response
            if not response.choices or not response.choices[0].message.content:
                raise AIServiceError(
                    "Empty response from AI model",
                    service="openai",
                    model=self.config.llm_model,
                    context={"operation": "analyze_image"},
                )

            # Parse the structured response
            json_content = response.choices[0].message.content.strip()
            result = AnalysisResult.model_validate_json(json_content)

            analysis_time = time.time() - start_time
            log_performance("ai_image_analysis", analysis_time, logger)

            logger.info(
                "Image analysis completed successfully",
                extra={
                    "analysis_time_seconds": analysis_time,
                    "description_length": len(result.description),
                    "tags_count": len(result.tags),
                    "colors_count": len(result.colors),
                    "model": self.config.llm_model,
                },
            )

            return result

        except (ValidationError, AIServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            analysis_time = time.time() - start_time
            logger.error(
                "Image analysis failed",
                extra={
                    "analysis_time_seconds": analysis_time,
                    "model": self.config.llm_model,
                    "error": str(e),
                },
            )
            raise AIServiceError(
                "Image analysis failed",
                service="openai",
                model=self.config.llm_model,
                context={"operation": "analyze_image", "error_type": type(e).__name__},
            ) from e

    async def index_image_file(self, image_path: str) -> AnalysisResult:
        """Index a single image file.

        Args:
            image_path: Path to the image file

        Returns:
            Analysis results

        Raises:
            NotFoundError: If image file doesn't exist
            ImageProcessingError: If image processing fails
            AIServiceError: If AI analysis fails
        """
        start_time = time.time()
        logger.info("Starting image indexing", extra={"image_path": image_path})

        try:
            # Process the image file
            base64_data, thumbnail = await self.image_service.process_image_file(image_path)

            # Analyze the image with AI
            analysis = await self.analyze_image(base64_data)

            # Store in repositories
            await self._store_analysis(image_path, analysis, thumbnail)

            indexing_time = time.time() - start_time
            log_performance("image_indexing_complete", indexing_time, logger)

            logger.info(
                "Image indexing completed successfully",
                extra={
                    "image_path": image_path,
                    "indexing_time_seconds": indexing_time,
                    "description": analysis.description[:100] + "..."
                    if len(analysis.description) > 100
                    else analysis.description,
                },
            )

            return analysis

        except Exception as e:
            indexing_time = time.time() - start_time
            logger.error(
                "Image indexing failed",
                extra={
                    "image_path": image_path,
                    "indexing_time_seconds": indexing_time,
                    "error": str(e),
                },
            )
            raise

    async def batch_index_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        max_concurrent: int = 3,
        supported_extensions: Optional[list[str]] = None,
    ) -> tuple[list[str], list[str]]:
        """Index all images in a directory.

        Args:
            directory_path: Path to the directory containing images
            recursive: Whether to search subdirectories
            max_concurrent: Maximum concurrent indexing operations
            supported_extensions: List of supported file extensions

        Returns:
            Tuple of (successful_files, failed_files)

        Raises:
            ValidationError: If directory path is invalid
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            raise ValidationError(
                f"Invalid directory path: {directory_path}",
                field="directory_path",
                value=directory_path,
            )

        supported_exts = supported_extensions or [".jpg", ".jpeg", ".png"]
        semaphore = asyncio.Semaphore(max_concurrent)

        # Find all image files
        if recursive:
            image_files = [
                str(f)
                for f in directory.rglob("*")
                if f.is_file() and f.suffix.lower() in supported_exts
            ]
        else:
            image_files = [
                str(f)
                for f in directory.iterdir()
                if f.is_file() and f.suffix.lower() in supported_exts
            ]

        logger.info(
            "Starting batch indexing",
            extra={
                "directory": directory_path,
                "total_files": len(image_files),
                "recursive": recursive,
                "max_concurrent": max_concurrent,
            },
        )

        successful = []
        failed = []

        async def index_single_file(file_path: str) -> bool:
            async with semaphore:
                try:
                    await self.index_image_file(file_path)
                    successful.append(file_path)
                    return True
                except Exception as e:
                    logger.warning(
                        "Failed to index file in batch",
                        extra={"file_path": file_path, "error": str(e)},
                    )
                    failed.append(file_path)
                    return False

        start_time = time.time()

        # Process all files concurrently
        tasks = [index_single_file(file_path) for file_path in image_files]
        await asyncio.gather(*tasks, return_exceptions=True)

        batch_time = time.time() - start_time
        success_rate = len(successful) / len(image_files) if image_files else 0

        logger.info(
            "Batch indexing completed",
            extra={
                "directory": directory_path,
                "total_files": len(image_files),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": success_rate,
                "batch_time_seconds": batch_time,
            },
        )

        return successful, failed

    async def _store_analysis(
        self, image_path: str, analysis: AnalysisResult, thumbnail: str
    ) -> None:
        """Store analysis results in the repositories.

        Args:
            image_path: Path to the original image
            analysis: Analysis results
            thumbnail: Base64 encoded thumbnail

        Raises:
            DatabaseError: If storage fails
        """
        try:
            # Store in metadata repository
            if self.metadata_repository:
                self.metadata_repository.add_analysis(image_path, analysis, thumbnail)
            else:
                # Fallback import
                from repository.metadata_repository import add_analysis

                add_analysis(image_path, analysis, thumbnail)

            # Store in multimodal repository
            if self.multimodal_repository:
                self.multimodal_repository.add_multimodal(image_path, analysis, thumbnail)
            else:
                # Fallback import
                from repository.multimodal_repository import add_multimodal

                add_multimodal(image_path, analysis, thumbnail)

            logger.debug(
                "Analysis stored successfully",
                extra={"image_path": image_path, "thumbnail_size": len(thumbnail)},
            )

        except Exception as e:
            logger.error(
                "Failed to store analysis results",
                extra={"image_path": image_path, "error": str(e)},
            )
            # Import here to avoid circular imports
            from core.exceptions import DatabaseError

            raise DatabaseError(
                "Failed to store analysis results",
                operation="store_analysis",
                context={"image_path": image_path},
            ) from e

    def get_indexing_stats(self) -> dict:
        """Get indexing service statistics.

        Returns:
            Dictionary with service statistics
        """
        return {
            "llm_model": self.config.llm_model,
            "llm_provider": self.config.llm_provider,
            "initialized": bool(self.client and self._analysis_prompt),
            "supported_formats": self.image_service.get_supported_formats(),
            "thumbnail_size": f"{self.config.thumbnail_width}x{self.config.thumbnail_height}",
        }
