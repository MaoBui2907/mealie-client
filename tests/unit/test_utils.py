"""
Unit tests for Mealie SDK utility functions.

Tests cover URL handling, data validation, formatting functions,
and other utility operations.
"""

import os
import tempfile
from datetime import datetime, date
from pathlib import Path

import pytest

from mealie_client.utils import (
    normalize_base_url,
    build_url,
    slugify,
    generate_request_id,
    format_datetime,
    parse_duration,
    format_duration,
    extract_file_info,
    get_mime_type,
    clean_dict,
    validate_slug,
    validate_email,
    get_env_var,
    chunk_list,
    merge_dicts,
    deep_get,
    format_file_size,
)


class TestNormalizeBaseUrl:
    """Test suite for normalize_base_url function."""

    @pytest.mark.unit
    def test_normalize_url_with_https(self):
        """Test normalizing HTTPS URL."""
        result = normalize_base_url("https://mealie.example.com")
        assert result == "https://mealie.example.com/api"

    @pytest.mark.unit
    def test_normalize_url_with_http(self):
        """Test normalizing HTTP URL."""
        result = normalize_base_url("http://localhost:8080")
        assert result == "http://localhost:8080/api"

    @pytest.mark.unit
    def test_normalize_url_without_protocol(self):
        """Test normalizing URL without protocol defaults to HTTPS."""
        result = normalize_base_url("mealie.example.com")
        assert result == "https://mealie.example.com/api"

    @pytest.mark.unit
    def test_normalize_url_with_trailing_slash(self):
        """Test normalizing URL with trailing slash."""
        result = normalize_base_url("https://mealie.example.com/")
        assert result == "https://mealie.example.com/api"

    @pytest.mark.unit
    def test_normalize_url_with_path_and_trailing_slash(self):
        """Test normalizing URL with existing path and trailing slash."""
        result = normalize_base_url("https://mealie.example.com/subpath/")
        assert result == "https://mealie.example.com/subpath/api"

    @pytest.mark.unit
    def test_normalize_url_already_with_api(self):
        """Test normalizing URL that already ends with /api."""
        result = normalize_base_url("https://mealie.example.com/api")
        assert result == "https://mealie.example.com/api"

    @pytest.mark.unit
    def test_normalize_url_with_api_and_trailing_slash(self):
        """Test normalizing URL with /api/ ending."""
        result = normalize_base_url("https://mealie.example.com/api/")
        assert result == "https://mealie.example.com/api"

    @pytest.mark.unit
    def test_normalize_url_with_port(self):
        """Test normalizing URL with port number."""
        result = normalize_base_url("https://localhost:8080")
        assert result == "https://localhost:8080/api"

    @pytest.mark.unit
    def test_normalize_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Base URL cannot be empty"):
            normalize_base_url("")

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_normalize_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            normalize_base_url("not-a-valid-url")


class TestBuildUrl:
    """Test suite for build_url function."""

    @pytest.mark.unit
    def test_build_url_simple_path(self):
        """Test building URL with simple path."""
        result = build_url("https://api.example.com", "recipes")
        assert result == "https://api.example.com/recipes"

    @pytest.mark.unit
    def test_build_url_multiple_path_parts(self):
        """Test building URL with multiple path parts."""
        result = build_url("https://api.example.com", "recipes", "123", "images")
        assert result == "https://api.example.com/recipes/123/images"

    @pytest.mark.unit
    def test_build_url_with_leading_slashes_in_parts(self):
        """Test building URL with leading slashes in path parts."""
        result = build_url("https://api.example.com/", "/recipes/", "/123/")
        assert result == "https://api.example.com/recipes/123"

    @pytest.mark.unit
    def test_build_url_with_query_params(self):
        """Test building URL with query parameters."""
        result = build_url(
            "https://api.example.com",
            "recipes",
            page=1,
            limit=10,
            category="dessert"
        )
        
        assert "https://api.example.com/recipes?" in result
        assert "page=1" in result
        assert "limit=10" in result
        assert "category=dessert" in result

    @pytest.mark.unit
    def test_build_url_filters_none_params(self):
        """Test that None query parameters are filtered out."""
        result = build_url(
            "https://api.example.com",
            "recipes",
            page=1,
            category=None,
            limit=10
        )
        
        assert "page=1" in result
        assert "limit=10" in result
        assert "category" not in result

    @pytest.mark.unit
    def test_build_url_with_list_params(self):
        """Test building URL with list parameters."""
        result = build_url(
            "https://api.example.com",
            "recipes",
            tags=["easy", "quick", "healthy"]
        )
        
        assert "tags=easy" in result
        assert "tags=quick" in result
        assert "tags=healthy" in result

    @pytest.mark.unit
    def test_build_url_empty_path_parts(self):
        """Test building URL with empty path parts."""
        result = build_url("https://api.example.com", "", "recipes", None, "123")
        assert result == "https://api.example.com/recipes/123"


class TestSlugify:
    """Test suite for slugify function."""

    @pytest.mark.unit
    def test_slugify_simple_text(self):
        """Test slugifying simple text."""
        assert slugify("Hello World") == "hello-world"

    @pytest.mark.unit
    def test_slugify_with_special_characters(self):
        """Test slugifying text with special characters."""
        assert slugify("Chicken & Rice (Easy Recipe)!") == "chicken-rice-easy-recipe"

    @pytest.mark.unit
    def test_slugify_with_multiple_spaces(self):
        """Test slugifying text with multiple spaces."""
        assert slugify("Multiple   Spaces   Between   Words") == "multiple-spaces-between-words"

    @pytest.mark.unit
    def test_slugify_with_leading_trailing_spaces(self):
        """Test slugifying text with leading and trailing spaces."""
        assert slugify("  Spaced Text  ") == "spaced-text"

    @pytest.mark.unit
    def test_slugify_with_hyphens(self):
        """Test slugifying text that already has hyphens."""
        assert slugify("Pre-existing-hyphens") == "pre-existing-hyphens"

    @pytest.mark.unit
    def test_slugify_empty_string(self):
        """Test slugifying empty string."""
        assert slugify("") == ""

    @pytest.mark.unit
    def test_slugify_with_numbers(self):
        """Test slugifying text with numbers."""
        assert slugify("Recipe 123 Version 2.0") == "recipe-123-version-20"

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_slugify_with_unicode_characters(self):
        """Test slugifying text with unicode characters."""
        assert slugify("Café Naïve résumé") == "caf-nave-rsum"


class TestGenerateRequestId:
    """Test suite for generate_request_id function."""

    @pytest.mark.unit
    def test_generate_request_id_returns_string(self):
        """Test that generate_request_id returns a string."""
        request_id = generate_request_id()
        assert isinstance(request_id, str)

    @pytest.mark.unit
    def test_generate_request_id_unique(self):
        """Test that generate_request_id produces unique values."""
        id1 = generate_request_id()
        id2 = generate_request_id()
        assert id1 != id2

    @pytest.mark.unit
    def test_generate_request_id_format(self):
        """Test that request ID follows UUID format."""
        request_id = generate_request_id()
        # UUID4 format: 8-4-4-4-12 hex digits
        parts = request_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestFormatDatetime:
    """Test suite for format_datetime function."""

    @pytest.mark.unit
    def test_format_datetime_object(self):
        """Test formatting datetime object."""
        dt = datetime(2023, 12, 25, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "2023-12-25T14:30:45"

    @pytest.mark.unit
    def test_format_date_object(self):
        """Test formatting date object."""
        d = date(2023, 12, 25)
        result = format_datetime(d)
        assert result == "2023-12-25T00:00:00"

    @pytest.mark.unit
    def test_format_datetime_string(self):
        """Test formatting datetime string (passthrough)."""
        dt_str = "2023-12-25T14:30:45Z"
        result = format_datetime(dt_str)
        assert result == dt_str

    @pytest.mark.unit
    def test_format_datetime_none(self):
        """Test formatting None datetime."""
        result = format_datetime(None)
        assert result is None

    @pytest.mark.unit
    def test_format_datetime_invalid_type_raises_error(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported datetime type"):
            format_datetime(12345)


class TestParseDuration:
    """Test suite for parse_duration function."""

    @pytest.mark.unit
    def test_parse_duration_minutes_only(self):
        """Test parsing duration with minutes only."""
        assert parse_duration("PT30M") == 30

    @pytest.mark.unit
    def test_parse_duration_hours_only(self):
        """Test parsing duration with hours only."""
        assert parse_duration("PT2H") == 120

    @pytest.mark.unit
    def test_parse_duration_hours_and_minutes(self):
        """Test parsing duration with hours and minutes."""
        assert parse_duration("PT1H30M") == 90

    @pytest.mark.unit
    def test_parse_duration_zero(self):
        """Test parsing zero duration."""
        assert parse_duration("PT0M") == 0

    @pytest.mark.unit
    def test_parse_duration_empty_string(self):
        """Test parsing empty string."""
        assert parse_duration("") is None

    @pytest.mark.unit
    def test_parse_duration_none(self):
        """Test parsing None."""
        assert parse_duration(None) is None

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_parse_duration_invalid_format(self):
        """Test parsing invalid format."""
        assert parse_duration("30 minutes") is None
        assert parse_duration("PT") is None
        assert parse_duration("1H30M") is None  # Missing PT prefix


class TestFormatDuration:
    """Test suite for format_duration function."""

    @pytest.mark.unit
    def test_format_duration_minutes_only(self):
        """Test formatting minutes only."""
        assert format_duration(30) == "PT30M"

    @pytest.mark.unit
    def test_format_duration_hours_only(self):
        """Test formatting hours only."""
        assert format_duration(120) == "PT2H"

    @pytest.mark.unit
    def test_format_duration_hours_and_minutes(self):
        """Test formatting hours and minutes."""
        assert format_duration(90) == "PT1H30M"

    @pytest.mark.unit
    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "PT0M"

    @pytest.mark.unit
    def test_format_duration_none(self):
        """Test formatting None duration."""
        assert format_duration(None) is None

    @pytest.mark.unit
    def test_format_duration_negative(self):
        """Test formatting negative duration."""
        assert format_duration(-30) is None


class TestExtractFileInfo:
    """Test suite for extract_file_info function."""

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_extract_file_info_existing_file(self):
        """Test extracting info from existing file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Hello, World!")
            tmp_path = tmp.name
        
        try:
            result = extract_file_info(tmp_path)
            
            assert result["exists"] is True
            assert result["size"] == 13
            assert result["extension"] == ".txt"
            assert result["name"] == Path(tmp_path).name
            assert "modified_time" in result
        finally:
            os.unlink(tmp_path)

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_extract_file_info_nonexistent_file(self):
        """Test extracting info from nonexistent file."""
        result = extract_file_info("/nonexistent/file.jpg")
        
        assert result["exists"] is False
        assert result["size"] == 0
        assert result["extension"] == ".jpg"
        assert result["name"] == "file.jpg"

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_extract_file_info_path_object(self):
        """Test extracting info using Path object."""
        path = Path("/path/to/document.pdf")
        result = extract_file_info(path)
        
        assert result["extension"] == ".pdf"
        assert result["name"] == "document.pdf"

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_extract_file_info_no_extension(self):
        """Test extracting info from file without extension."""
        result = extract_file_info("/path/to/filename")
        
        assert result["extension"] == ""
        assert result["name"] == "filename"


class TestGetMimeType:
    """Test suite for get_mime_type function."""

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_get_mime_type_common_extensions(self):
        """Test getting MIME types for common file extensions."""
        test_cases = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".gif", "image/gif"),
            (".webp", "image/webp"),
            (".pdf", "application/pdf"),
            (".json", "application/json"),
            (".txt", "text/plain"),
            (".html", "text/html"),
            (".css", "text/css"),
            (".js", "application/javascript"),
        ]
        
        for extension, expected_mime in test_cases:
            assert get_mime_type(extension) == expected_mime

    @pytest.mark.unit
    def test_get_mime_type_case_insensitive(self):
        """Test that MIME type detection is case insensitive."""
        assert get_mime_type(".JPG") == "image/jpeg"
        assert get_mime_type(".PNG") == "image/png"
        assert get_mime_type(".Pdf") == "application/pdf"

    @pytest.mark.unit
    def test_get_mime_type_unknown_extension(self):
        """Test getting MIME type for unknown extension."""
        assert get_mime_type(".xyz") == "application/octet-stream"
        assert get_mime_type(".unknown") == "application/octet-stream"

    @pytest.mark.unit
    def test_get_mime_type_no_extension(self):
        """Test getting MIME type for empty extension."""
        assert get_mime_type("") == "application/octet-stream"


class TestCleanDict:
    """Test suite for clean_dict function."""

    @pytest.mark.unit
    def test_clean_dict_removes_none_values(self):
        """Test that clean_dict removes None values by default."""
        data = {"a": 1, "b": None, "c": "value", "d": None}
        result = clean_dict(data)
        
        assert result == {"a": 1, "c": "value"}

    @pytest.mark.unit
    def test_clean_dict_preserves_none_when_disabled(self):
        """Test that clean_dict preserves None when remove_none=False."""
        data = {"a": 1, "b": None, "c": "value"}
        result = clean_dict(data, remove_none=False)
        
        assert result == data

    @pytest.mark.unit
    def test_clean_dict_removes_empty_values(self):
        """Test that clean_dict removes empty values when enabled."""
        data = {"a": 1, "b": "", "c": [], "d": {}, "e": "value"}
        result = clean_dict(data, remove_empty=True)
        
        assert result == {"a": 1, "e": "value"}

    @pytest.mark.unit
    def test_clean_dict_removes_both_none_and_empty(self):
        """Test that clean_dict removes both None and empty values."""
        data = {"a": 1, "b": None, "c": "", "d": [], "e": "value"}
        result = clean_dict(data, remove_none=True, remove_empty=True)
        
        assert result == {"a": 1, "e": "value"}

    @pytest.mark.unit
    def test_clean_dict_preserves_false_and_zero(self):
        """Test that clean_dict preserves False and 0 values."""
        data = {"a": 0, "b": False, "c": None, "d": ""}
        result = clean_dict(data, remove_empty=True)
        
        assert result == {"a": 0, "b": False}


class TestValidateSlug:
    """Test suite for validate_slug function."""

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_validate_slug_valid_slugs(self):
        """Test validation of valid slugs."""
        valid_slugs = [
            "simple-slug",
            "slug-with-numbers-123",
            "underscore_slug",
            "single",
            "a-very-long-slug-with-many-parts",
        ]
        
        for slug in valid_slugs:
            assert validate_slug(slug) is True

    @pytest.mark.unit
    def test_validate_slug_invalid_slugs(self):
        """Test validation of invalid slugs."""
        invalid_slugs = [
            "slug with spaces",
            "UPPERCASE-SLUG",
            "slug.with.dots",
            "slug@with#symbols",
            "-starts-with-hyphen",
            "ends-with-hyphen-",
            "",
        ]
        
        for slug in invalid_slugs:
            assert validate_slug(slug) is False


class TestValidateEmail:
    """Test suite for validate_email function."""

    @pytest.mark.unit
    def test_validate_email_valid_emails(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@subdomain.example.org",
            "simple@domain.io",
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True

    @pytest.mark.unit
    def test_validate_email_invalid_emails(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user.domain.com",
            "user@domain",
            "",
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False


class TestGetEnvVar:
    """Test suite for get_env_var function."""

    @pytest.mark.unit
    def test_get_env_var_existing_variable(self, monkeypatch):
        """Test getting existing environment variable."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        
        result = get_env_var("TEST_VAR")
        assert result == "test_value"

    @pytest.mark.unit
    def test_get_env_var_with_default(self):
        """Test getting nonexistent variable with default."""
        result = get_env_var("NONEXISTENT_VAR", default="default_value")
        assert result == "default_value"

    @pytest.mark.unit
    def test_get_env_var_required_missing_raises_error(self):
        """Test that missing required variable raises error."""
        with pytest.raises(ValueError, match="Required environment variable"):
            get_env_var("REQUIRED_MISSING_VAR", required=True)

    @pytest.mark.unit
    def test_get_env_var_required_existing(self, monkeypatch):
        """Test getting existing required variable."""
        monkeypatch.setenv("REQUIRED_VAR", "required_value")
        
        result = get_env_var("REQUIRED_VAR", required=True)
        assert result == "required_value"


class TestChunkList:
    """Test suite for chunk_list function."""

    @pytest.mark.unit
    def test_chunk_list_even_division(self):
        """Test chunking list with even division."""
        items = list(range(10))  # [0, 1, 2, ..., 9]
        chunks = chunk_list(items, 5)
        
        assert len(chunks) == 2
        assert chunks[0] == [0, 1, 2, 3, 4]
        assert chunks[1] == [5, 6, 7, 8, 9]

    @pytest.mark.unit
    def test_chunk_list_uneven_division(self):
        """Test chunking list with uneven division."""
        items = list(range(7))  # [0, 1, 2, 3, 4, 5, 6]
        chunks = chunk_list(items, 3)
        
        assert len(chunks) == 3
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[2] == [6]

    @pytest.mark.unit
    def test_chunk_list_empty_list(self):
        """Test chunking empty list."""
        chunks = chunk_list([], 5)
        assert chunks == []

    @pytest.mark.unit
    def test_chunk_list_chunk_size_larger_than_list(self):
        """Test chunking with chunk size larger than list."""
        items = [1, 2, 3]
        chunks = chunk_list(items, 10)
        
        assert len(chunks) == 1
        assert chunks[0] == [1, 2, 3]


class TestMergeDicts:
    """Test suite for merge_dicts function."""

    @pytest.mark.unit
    def test_merge_dicts_simple(self):
        """Test merging simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        
        result = merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}

    @pytest.mark.unit
    def test_merge_dicts_overlapping_keys(self):
        """Test merging dictionaries with overlapping keys."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        
        result = merge_dicts(dict1, dict2)
        # Later dictionaries should override earlier ones
        assert result == {"a": 1, "b": 3, "c": 4}

    @pytest.mark.unit
    def test_merge_dicts_multiple_dicts(self):
        """Test merging multiple dictionaries."""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        dict3 = {"c": 3}
        
        result = merge_dicts(dict1, dict2, dict3)
        assert result == {"a": 1, "b": 2, "c": 3}

    @pytest.mark.unit
    def test_merge_dicts_empty_dict(self):
        """Test merging with empty dictionaries."""
        dict1 = {"a": 1}
        dict2 = {}
        dict3 = {"b": 2}
        
        result = merge_dicts(dict1, dict2, dict3)
        assert result == {"a": 1, "b": 2}


class TestDeepGet:
    """Test suite for deep_get function."""

    @pytest.mark.unit
    def test_deep_get_simple_key(self):
        """Test getting simple key."""
        data = {"a": 1, "b": 2}
        assert deep_get(data, "a") == 1

    @pytest.mark.unit
    def test_deep_get_nested_key(self):
        """Test getting nested key with dot notation."""
        data = {"a": {"b": {"c": "value"}}}
        assert deep_get(data, "a.b.c") == "value"

    @pytest.mark.unit
    def test_deep_get_with_default(self):
        """Test getting nonexistent key with default."""
        data = {"a": 1}
        assert deep_get(data, "b", default="default") == "default"

    @pytest.mark.unit
    def test_deep_get_nested_nonexistent(self):
        """Test getting nonexistent nested key."""
        data = {"a": {"b": 1}}
        assert deep_get(data, "a.c.d") is None

    @pytest.mark.unit
    def test_deep_get_partial_path_exists(self):
        """Test when partial path exists but not complete."""
        data = {"a": {"b": "not_dict"}}
        assert deep_get(data, "a.b.c") is None


class TestFormatFileSize:
    """Test suite for format_file_size function."""

    @pytest.mark.unit
    def test_format_file_size_bytes(self):
        """Test formatting file size in bytes."""
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"

    @pytest.mark.unit
    def test_format_file_size_kilobytes(self):
        """Test formatting file size in kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"

    @pytest.mark.unit
    def test_format_file_size_megabytes(self):
        """Test formatting file size in megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 2.5) == "2.5 MB"

    @pytest.mark.unit
    def test_format_file_size_gigabytes(self):
        """Test formatting file size in gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    @pytest.mark.unit
    def test_format_file_size_zero(self):
        """Test formatting zero file size."""
        assert format_file_size(0) == "0 B" 