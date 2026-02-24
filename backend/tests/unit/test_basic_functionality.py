"""Basic functionality tests to verify test infrastructure works."""

import pytest

from models.api_models import TextSearchRequest
from models.indexing_models import AnalysisResult, ColorData, TagData
from tests.fixtures.test_data import MockLLMResponses, TestImages, TestSearchData


class TestBasicFunctionality:
    """Test basic model creation and functionality."""

    @pytest.mark.unit
    def test_tag_data_creation(self):
        """Test creating TagData objects."""
        tag = TagData(tag="flower", confidence=0.95)
        assert tag.tag == "flower"
        assert tag.confidence == 0.95

    @pytest.mark.unit
    def test_color_data_creation(self):
        """Test creating ColorData objects."""
        color = ColorData(color="red", frequency=45)
        assert color.color == "red"
        assert color.frequency == 45

    @pytest.mark.unit
    def test_analysis_result_creation(self):
        """Test creating AnalysisResult objects."""
        analysis = MockLLMResponses.get_analysis_result("rose")

        assert analysis.description == "A beautiful red rose in full bloom with green leaves"
        assert len(analysis.tags) == 4
        assert len(analysis.colors) == 4
        assert analysis.tags[0].tag == "flower"
        assert analysis.colors[0].color == "red"

    @pytest.mark.unit
    def test_search_result_creation(self):
        """Test creating SearchResult objects."""
        result = TestSearchData.create_search_result()

        assert result.image_path == "/test/path/image1.jpg"
        assert result.description == "Test image description"
        assert result.distance == 0.1
        assert result.thumbnail.startswith("data:image/png;base64,")

    @pytest.mark.unit
    def test_text_search_request_creation(self):
        """Test creating TextSearchRequest objects."""
        request = TestSearchData.create_text_search_request()

        assert request.search_text == "test query"
        assert request.multimodal is False
        assert request.threshold == "small"

    @pytest.mark.unit
    def test_text_search_request_defaults(self):
        """Test TextSearchRequest default values."""
        request = TextSearchRequest(search_text="test")

        assert request.multimodal is False
        assert request.threshold == "small"

    @pytest.mark.unit
    def test_json_serialization(self):
        """Test JSON serialization works."""
        analysis = MockLLMResponses.get_analysis_result("landscape")

        # Serialize to JSON
        json_data = analysis.model_dump_json()
        assert isinstance(json_data, str)
        assert "mountain landscape" in json_data

        # Deserialize from JSON
        reconstructed = AnalysisResult.model_validate_json(json_data)
        assert reconstructed.description == analysis.description
        assert len(reconstructed.tags) == len(analysis.tags)

    @pytest.mark.unit
    def test_test_images_utility(self):
        """Test our test image creation utilities."""
        image = TestImages.create_test_image(200, 100, "blue")

        assert image.size == (200, 100)
        assert image.mode == "RGB"

        # Convert to base64
        base64_str = TestImages.image_to_base64(image)
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

    @pytest.mark.unit
    def test_mock_llm_responses(self):
        """Test mock LLM response generation."""
        # Test different response types
        rose_analysis = MockLLMResponses.get_analysis_result("rose")
        landscape_analysis = MockLLMResponses.get_analysis_result("landscape")

        assert rose_analysis.description != landscape_analysis.description
        assert "rose" in rose_analysis.description.lower()
        assert "mountain" in landscape_analysis.description.lower()

    @pytest.mark.unit
    def test_search_results_list_creation(self):
        """Test creating lists of search results."""
        results = TestSearchData.create_search_results_list(5)

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.image_path == f"/test/path/image{i+1}.jpg"
            assert result.distance == 0.1 + (i * 0.05)
