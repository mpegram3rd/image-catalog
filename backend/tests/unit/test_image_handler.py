"""Unit tests for image processing functionality."""

import asyncio
import base64
import io
from unittest.mock import patch

import pytest
from PIL import Image

from images.image_handler import (
    BASE64_PNG_PREFIX,
    create_thumbnail_as_base64_async,
    encode_image_async,
)
from tests.fixtures.test_data import TestImages


class TestEncodeImageAsync:
    """Test async image encoding functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_encode_valid_jpeg(self, sample_image_file):
        """Test encoding a valid JPEG file."""
        # Ensure the file is saved as JPEG
        image = TestImages.create_test_image()
        image.save(sample_image_file, format="JPEG")

        result = await encode_image_async(str(sample_image_file))

        # Result should be valid base64
        assert isinstance(result, str)
        assert len(result) > 0

        # Verify it's valid base64 that can be decoded
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

        # Verify the decoded data can be opened as an image
        test_image = Image.open(io.BytesIO(decoded))
        assert test_image.format == "JPEG"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_encode_valid_png(self, temp_dir):
        """Test encoding a valid PNG file."""
        png_file = temp_dir / "test.png"
        image = TestImages.create_test_image()
        image.save(png_file, format="PNG")

        result = await encode_image_async(str(png_file))

        # Verify result
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        test_image = Image.open(io.BytesIO(decoded))
        assert test_image.format == "PNG"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_encode_nonexistent_file(self, temp_dir):
        """Test encoding a non-existent file raises FileNotFoundError."""
        nonexistent_file = temp_dir / "does_not_exist.jpg"

        with pytest.raises(FileNotFoundError):
            await encode_image_async(str(nonexistent_file))

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_encode_empty_file(self, temp_dir):
        """Test encoding an empty file."""
        empty_file = temp_dir / "empty.jpg"
        empty_file.touch()  # Create empty file

        result = await encode_image_async(str(empty_file))

        # Should return empty base64 string
        assert result == ""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_encode_different_image_sizes(self, temp_dir):
        """Test encoding images of different sizes."""
        sizes = [(50, 50), (200, 150), (1000, 1000)]

        for width, height in sizes:
            image_file = temp_dir / f"test_{width}x{height}.jpg"
            image = TestImages.create_test_image(width, height)
            image.save(image_file, format="JPEG")

            result = await encode_image_async(str(image_file))

            assert isinstance(result, str)
            assert len(result) > 0

            # Larger images should produce longer base64 strings
            decoded = base64.b64decode(result)
            reconstructed = Image.open(io.BytesIO(decoded))
            assert reconstructed.size == (width, height)


class TestCreateThumbnailAsBase64Async:
    """Test async thumbnail creation functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_thumbnail_from_jpeg_base64(self):
        """Test creating thumbnail from JPEG base64 data."""
        # Create test image and encode it
        original_image = TestImages.create_test_image(400, 300, "blue")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        # Create thumbnail
        result = await create_thumbnail_as_base64_async(base64_data, 100, 100)

        # Verify result format
        assert isinstance(result, str)
        assert result.startswith(BASE64_PNG_PREFIX)

        # Decode and verify thumbnail
        thumbnail_data = result[len(BASE64_PNG_PREFIX) :]
        decoded = base64.b64decode(thumbnail_data)
        thumbnail = Image.open(io.BytesIO(decoded))

        assert thumbnail.format == "PNG"
        # Thumbnail should maintain aspect ratio, so it won't be exactly 100x100
        assert thumbnail.size[0] <= 100
        assert thumbnail.size[1] <= 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_thumbnail_from_png_base64(self):
        """Test creating thumbnail from PNG base64 data."""
        original_image = TestImages.create_test_image(200, 200, "green")
        base64_data = TestImages.image_to_base64(original_image, "PNG")

        result = await create_thumbnail_as_base64_async(base64_data, 50, 50)

        assert result.startswith(BASE64_PNG_PREFIX)

        # Verify thumbnail dimensions
        thumbnail_data = result[len(BASE64_PNG_PREFIX) :]
        decoded = base64.b64decode(thumbnail_data)
        thumbnail = Image.open(io.BytesIO(decoded))

        assert thumbnail.size[0] <= 50
        assert thumbnail.size[1] <= 50

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_aspect_ratio_preservation(self):
        """Test that thumbnails preserve aspect ratio."""
        # Create a wide image (2:1 aspect ratio)
        original_image = TestImages.create_test_image(400, 200, "red")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        # Request square thumbnail
        result = await create_thumbnail_as_base64_async(base64_data, 100, 100)

        # Decode thumbnail
        thumbnail_data = result[len(BASE64_PNG_PREFIX) :]
        decoded = base64.b64decode(thumbnail_data)
        thumbnail = Image.open(io.BytesIO(decoded))

        # Should maintain 2:1 aspect ratio
        width, height = thumbnail.size
        aspect_ratio = width / height
        assert abs(aspect_ratio - 2.0) < 0.1  # Allow small floating point errors

        # The constraining dimension should be width (100)
        assert width == 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_tall_image(self):
        """Test thumbnail creation for tall images."""
        # Create a tall image (1:2 aspect ratio)
        original_image = TestImages.create_test_image(200, 400, "yellow")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        result = await create_thumbnail_as_base64_async(base64_data, 100, 100)

        # Decode thumbnail
        thumbnail_data = result[len(BASE64_PNG_PREFIX) :]
        decoded = base64.b64decode(thumbnail_data)
        thumbnail = Image.open(io.BytesIO(decoded))

        # Should maintain 1:2 aspect ratio
        width, height = thumbnail.size
        aspect_ratio = width / height
        assert abs(aspect_ratio - 0.5) < 0.1

        # The constraining dimension should be height (100)
        assert height == 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_different_target_sizes(self):
        """Test creating thumbnails with different target dimensions."""
        original_image = TestImages.create_test_image(300, 300, "purple")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        target_sizes = [(50, 50), (150, 100), (200, 300)]

        for target_width, target_height in target_sizes:
            result = await create_thumbnail_as_base64_async(
                base64_data, target_width, target_height
            )

            # Decode and check size
            thumbnail_data = result[len(BASE64_PNG_PREFIX) :]
            decoded = base64.b64decode(thumbnail_data)
            thumbnail = Image.open(io.BytesIO(decoded))

            # Thumbnail should not exceed target dimensions
            assert thumbnail.size[0] <= target_width
            assert thumbnail.size[1] <= target_height

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_invalid_base64_data(self):
        """Test thumbnail creation with invalid base64 data."""
        invalid_data = "not_valid_base64_data"

        with pytest.raises(Exception):  # Could be various exceptions
            await create_thumbnail_as_base64_async(invalid_data, 100, 100)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_empty_base64_data(self):
        """Test thumbnail creation with empty base64 data."""
        with pytest.raises(Exception):
            await create_thumbnail_as_base64_async("", 100, 100)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_corrupted_image_data(self):
        """Test thumbnail creation with corrupted image data."""
        # Create valid base64 data that doesn't represent a valid image
        corrupted_data = base64.b64encode(b"This is not image data").decode()

        with pytest.raises(Exception):
            await create_thumbnail_as_base64_async(corrupted_data, 100, 100)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_zero_dimensions(self):
        """Test thumbnail creation with zero target dimensions."""
        original_image = TestImages.create_test_image(100, 100, "cyan")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        # This should handle edge cases gracefully
        with pytest.raises(Exception):
            await create_thumbnail_as_base64_async(base64_data, 0, 100)

        with pytest.raises(Exception):
            await create_thumbnail_as_base64_async(base64_data, 100, 0)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_performance_timing(self):
        """Test that thumbnail creation includes performance logging."""
        original_image = TestImages.create_test_image(500, 500, "orange")
        base64_data = TestImages.image_to_base64(original_image, "JPEG")

        # Mock the logger to capture performance logging
        with patch("images.image_handler.log_performance") as mock_log_perf:
            result = await create_thumbnail_as_base64_async(base64_data, 100, 100)

            # Verify performance was logged
            mock_log_perf.assert_called_once()
            call_args = mock_log_perf.call_args[0]
            assert call_args[0] == "thumbnail_generation"
            assert isinstance(call_args[1], float)  # duration
            assert call_args[1] > 0  # should take some time

        # Verify result is still valid
        assert result.startswith(BASE64_PNG_PREFIX)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_thumbnail_concurrent_creation(self):
        """Test creating multiple thumbnails concurrently."""
        # Create multiple test images
        images_data = []
        for i in range(3):
            image = TestImages.create_test_image(200, 200, ["red", "green", "blue"][i])
            base64_data = TestImages.image_to_base64(image, "JPEG")
            images_data.append(base64_data)

        # Create thumbnails concurrently
        tasks = [create_thumbnail_as_base64_async(data, 50, 50) for data in images_data]

        results = await asyncio.gather(*tasks)

        # All results should be valid
        assert len(results) == 3
        for result in results:
            assert isinstance(result, str)
            assert result.startswith(BASE64_PNG_PREFIX)


class TestImageHandlerConstants:
    """Test image handler constants and utilities."""

    @pytest.mark.unit
    def test_base64_png_prefix(self):
        """Test BASE64_PNG_PREFIX constant."""
        assert BASE64_PNG_PREFIX == "data:image/png;base64,"
        assert BASE64_PNG_PREFIX.startswith("data:image/png")
        assert BASE64_PNG_PREFIX.endswith("base64,")

    @pytest.mark.unit
    def test_base64_prefix_usage(self):
        """Test that BASE64_PNG_PREFIX is used correctly in thumbnails."""
        # This is tested indirectly through thumbnail creation tests
        # but we can verify the constant structure
        assert len(BASE64_PNG_PREFIX) > 0
        assert "," in BASE64_PNG_PREFIX  # Should end with comma separator
