"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from models.api_models import SearchResult, SearchResultsMcp, TextSearchRequest
from models.indexing_models import AnalysisResult, ColorData, Metadata, TagData
from tests.fixtures.test_data import TestImages, TestSearchData


class TestTagData:
    """Test TagData model."""

    @pytest.mark.unit
    def test_valid_tag_data(self):
        """Test creating TagData with valid data."""
        tag = TagData(tag="flower", confidence=0.95)
        assert tag.tag == "flower"
        assert tag.confidence == 0.95

    @pytest.mark.unit
    def test_confidence_validation(self):
        """Test confidence must be between 0 and 1."""
        # Valid confidence values
        TagData(tag="test", confidence=0.0)
        TagData(tag="test", confidence=1.0)
        TagData(tag="test", confidence=0.5)

        # Invalid confidence values should raise ValidationError
        with pytest.raises(ValidationError):
            TagData(tag="test", confidence=-0.1)

        with pytest.raises(ValidationError):
            TagData(tag="test", confidence=1.1)

    @pytest.mark.unit
    def test_tag_string_validation(self):
        """Test tag must be a non-empty string."""
        # Valid tag
        TagData(tag="valid_tag", confidence=0.8)

        # Invalid tags
        with pytest.raises(ValidationError):
            TagData(tag="", confidence=0.8)  # Empty string

        with pytest.raises(ValidationError):
            TagData(tag=123, confidence=0.8)  # Not a string


class TestColorData:
    """Test ColorData model."""

    @pytest.mark.unit
    def test_valid_color_data(self):
        """Test creating ColorData with valid data."""
        color = ColorData(color="red", frequency=45)
        assert color.color == "red"
        assert color.frequency == 45

    @pytest.mark.unit
    def test_frequency_validation(self):
        """Test frequency must be between 0 and 100."""
        # Valid frequency values
        ColorData(color="red", frequency=0)
        ColorData(color="red", frequency=100)
        ColorData(color="red", frequency=50)

        # Invalid frequency values
        with pytest.raises(ValidationError):
            ColorData(color="red", frequency=-1)

        with pytest.raises(ValidationError):
            ColorData(color="red", frequency=101)

    @pytest.mark.unit
    def test_color_string_validation(self):
        """Test color must be a non-empty string."""
        # Valid color
        ColorData(color="blue", frequency=30)

        # Invalid colors
        with pytest.raises(ValidationError):
            ColorData(color="", frequency=30)

        with pytest.raises(ValidationError):
            ColorData(color=None, frequency=30)


class TestAnalysisResult:
    """Test AnalysisResult model."""

    @pytest.mark.unit
    def test_valid_analysis_result(self):
        """Test creating AnalysisResult with valid data."""
        tags = [
            TagData(tag="flower", confidence=0.95),
            TagData(tag="red", confidence=0.85)
        ]
        colors = [
            ColorData(color="red", frequency=45),
            ColorData(color="green", frequency=30)
        ]

        result = AnalysisResult(
            description="A beautiful red flower",
            tags=tags,
            colors=colors
        )

        assert result.description == "A beautiful red flower"
        assert len(result.tags) == 2
        assert len(result.colors) == 2
        assert result.tags[0].tag == "flower"
        assert result.colors[0].color == "red"

    @pytest.mark.unit
    def test_empty_lists_allowed(self):
        """Test that empty tag and color lists are allowed."""
        result = AnalysisResult(
            description="Test description",
            tags=[],
            colors=[]
        )
        assert result.tags == []
        assert result.colors == []

    @pytest.mark.unit
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        tags = [TagData(tag="test", confidence=0.9)]
        colors = [ColorData(color="blue", frequency=50)]

        original = AnalysisResult(
            description="Test image",
            tags=tags,
            colors=colors
        )

        # Serialize to JSON
        json_data = original.model_dump_json()

        # Deserialize from JSON
        reconstructed = AnalysisResult.model_validate_json(json_data)

        assert reconstructed.description == original.description
        assert len(reconstructed.tags) == len(original.tags)
        assert reconstructed.tags[0].tag == original.tags[0].tag
        assert reconstructed.colors[0].color == original.colors[0].color


class TestMetadata:
    """Test Metadata model."""

    @pytest.mark.unit
    def test_valid_metadata(self):
        """Test creating Metadata with valid data."""
        thumbnail = TestImages.create_thumbnail_base64()
        metadata = Metadata(
            tags="flower,red,garden",
            colors="red,green,pink",
            thumbnail=thumbnail
        )

        assert metadata.tags == "flower,red,garden"
        assert metadata.colors == "red,green,pink"
        assert metadata.thumbnail == thumbnail

    @pytest.mark.unit
    def test_empty_strings_allowed(self):
        """Test that empty strings are allowed for tags and colors."""
        metadata = Metadata(
            tags="",
            colors="",
            thumbnail="test_thumbnail"
        )
        assert metadata.tags == ""
        assert metadata.colors == ""


class TestSearchResult:
    """Test SearchResult model."""

    @pytest.mark.unit
    def test_valid_search_result(self):
        """Test creating SearchResult with valid data."""
        result = TestSearchData.create_search_result()

        assert result.image_path == "/test/path/image1.jpg"
        assert result.description == "Test image description"
        assert result.distance == 0.1
        assert result.thumbnail.startswith("data:image/png;base64,")

    @pytest.mark.unit
    def test_distance_validation(self):
        """Test distance must be non-negative."""
        # Valid distance
        TestSearchData.create_search_result(distance=0.0)
        TestSearchData.create_search_result(distance=0.5)
        TestSearchData.create_search_result(distance=1.0)

        # Invalid distance
        with pytest.raises(ValidationError):
            SearchResult(
                image_path="/test/path",
                description="test",
                thumbnail="test_thumb",
                distance=-0.1
            )

    @pytest.mark.unit
    def test_json_serialization(self):
        """Test JSON serialization."""
        original = TestSearchData.create_search_result()
        json_data = original.model_dump_json()
        reconstructed = SearchResult.model_validate_json(json_data)

        assert reconstructed.image_path == original.image_path
        assert reconstructed.description == original.description
        assert reconstructed.distance == original.distance
        assert reconstructed.thumbnail == original.thumbnail


class TestSearchResultsMcp:
    """Test SearchResultsMcp model."""

    @pytest.mark.unit
    def test_valid_mcp_result(self):
        """Test creating SearchResultsMcp with valid data."""
        result = TestSearchData.create_mcp_search_result()

        assert result.image_path.startswith("http://")
        assert result.description == "Test MCP image description"

    @pytest.mark.unit
    def test_url_validation(self):
        """Test that image_path can be a valid URL."""
        valid_urls = [
            "http://localhost:5173/path/image.jpg",
            "https://example.com/image.png",
            "/relative/path/image.jpg"
        ]

        for url in valid_urls:
            result = SearchResultsMcp(
                image_path=url,
                description="Test description"
            )
            assert result.image_path == url


class TestTextSearchRequest:
    """Test TextSearchRequest model."""

    @pytest.mark.unit
    def test_valid_search_request(self):
        """Test creating TextSearchRequest with valid data."""
        request = TestSearchData.create_text_search_request()

        assert request.search_text == "test query"
        assert request.multimodal is False
        assert request.threshold == "small"

    @pytest.mark.unit
    def test_default_values(self):
        """Test default values for optional fields."""
        request = TextSearchRequest(search_text="test")

        assert request.multimodal is False
        assert request.threshold == "small"

    @pytest.mark.unit
    def test_threshold_validation(self):
        """Test threshold must be one of allowed values."""
        valid_thresholds = ["small", "medium", "yuge"]

        for threshold in valid_thresholds:
            request = TextSearchRequest(
                search_text="test",
                threshold=threshold
            )
            assert request.threshold == threshold

        # Invalid threshold
        with pytest.raises(ValidationError):
            TextSearchRequest(
                search_text="test",
                threshold="invalid"
            )

    @pytest.mark.unit
    def test_multimodal_boolean(self):
        """Test multimodal field accepts boolean values."""
        # True
        request = TextSearchRequest(
            search_text="test",
            multimodal=True
        )
        assert request.multimodal is True

        # False
        request = TextSearchRequest(
            search_text="test",
            multimodal=False
        )
        assert request.multimodal is False

    @pytest.mark.unit
    def test_empty_search_text(self):
        """Test that empty search text is invalid."""
        with pytest.raises(ValidationError):
            TextSearchRequest(search_text="")

        with pytest.raises(ValidationError):
            TextSearchRequest(search_text="   ")  # Whitespace only