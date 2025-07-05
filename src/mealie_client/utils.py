"""
Utility functions for the Mealie SDK.

This module contains helper functions and utilities used throughout the SDK
for URL handling, data validation, formatting, and other common operations.
"""

import os
import re
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


def normalize_base_url(base_url: str) -> str:
    """
    Normalize a base URL to ensure it's properly formatted.

    Args:
        base_url: The base URL to normalize

    Returns:
        Normalized base URL ending with /api

    Raises:
        ValueError: If the URL is invalid
    """
    if not base_url:
        raise ValueError("Base URL cannot be empty")

    # Remove trailing slashes
    base_url = base_url.rstrip("/")

    # Add protocol if missing
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    # Validate URL format
    parsed = urlparse(base_url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL format: {base_url}")

    # Add /api path if not present
    if not parsed.path.endswith("/api"):
        if parsed.path and not parsed.path.endswith("/"):
            parsed = parsed._replace(path=f"{parsed.path}/api")
        else:
            parsed = parsed._replace(path=f"{parsed.path}api")

    return urlunparse(parsed)


def build_url(base_url: str, *path_parts: str, **query_params: Any) -> str:
    """
    Build a complete URL from base URL, path parts, and query parameters.

    Args:
        base_url: The base URL
        *path_parts: Path segments to join
        **query_params: Query parameters to add

    Returns:
        Complete URL string
    """
    # Join path parts
    path = "/".join(str(part).strip("/") for part in path_parts if part)

    # Build the URL
    url = urljoin(base_url.rstrip("/") + "/", path)

    # Add query parameters
    if query_params:
        # Filter out None values
        filtered_params = {k: v for k, v in query_params.items() if v is not None}
        if filtered_params:
            parsed = urlparse(url)
            query_dict = parse_qs(parsed.query)
            
            # Add new parameters
            for key, value in filtered_params.items():
                if isinstance(value, (list, tuple)):
                    query_dict[key] = [str(v) for v in value]
                else:
                    query_dict[key] = [str(value)]
            
            # Rebuild query string
            query_string = urlencode(query_dict, doseq=True)
            url = urlunparse(parsed._replace(query=query_string))

    return url


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to convert to slug

    Returns:
        URL-friendly slug
    """
    if not text:
        return ""

    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    
    return slug.strip("-")


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracking API calls.

    Returns:
        Unique request ID string
    """
    return str(uuid.uuid4())


def format_datetime(dt: Union[datetime, date, str, None]) -> Optional[str]:
    """
    Format datetime objects for API requests.

    Args:
        dt: Datetime object, date object, ISO string, or None

    Returns:
        ISO formatted datetime string or None
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        # Assume it's already formatted
        return dt
    elif isinstance(dt, date) and not isinstance(dt, datetime):
        # Convert date to datetime at midnight
        dt = datetime.combine(dt, datetime.min.time())
    elif isinstance(dt, datetime):
        pass
    else:
        raise ValueError(f"Unsupported datetime type: {type(dt)}")
    
    return dt.isoformat()


def parse_duration(duration: Optional[str]) -> Optional[int]:
    """
    Parse ISO 8601 duration string to minutes.

    Args:
        duration: ISO 8601 duration string (e.g., "PT30M", "PT1H30M")

    Returns:
        Duration in minutes or None if parsing fails
    """
    if not duration:
        return None
    
    if not duration.startswith("PT"):
        return None
    
    # Simple regex for parsing PT<hours>H<minutes>M format
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration)
    if not match:
        return None
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    
    return hours * 60 + minutes


def format_duration(minutes: Optional[int]) -> Optional[str]:
    """
    Format minutes to ISO 8601 duration string.

    Args:
        minutes: Duration in minutes

    Returns:
        ISO 8601 duration string or None
    """
    if minutes is None or minutes < 0:
        return None
    
    if minutes == 0:
        return "PT0M"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}H")
    if remaining_minutes > 0:
        parts.append(f"{remaining_minutes}M")
    
    return "PT" + "".join(parts)


def extract_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract information about a file for upload operations.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not valid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    return {
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "size": path.stat().st_size,
        "mime_type": get_mime_type(path.suffix),
    }


def get_mime_type(file_extension: str) -> str:
    """
    Get MIME type for a file extension.

    Args:
        file_extension: File extension (with or without dot)

    Returns:
        MIME type string
    """
    extension = file_extension.lower().lstrip(".")
    
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "svg": "image/svg+xml",
        "pdf": "application/pdf",
        "txt": "text/plain",
        "json": "application/json",
        "xml": "application/xml",
        "zip": "application/zip",
    }
    
    return mime_types.get(extension, "application/octet-stream")


def clean_dict(data: Dict[str, Any], remove_none: bool = True, remove_empty: bool = False) -> Dict[str, Any]:
    """
    Clean a dictionary by removing None values and optionally empty values.

    Args:
        data: Dictionary to clean
        remove_none: Whether to remove None values
        remove_empty: Whether to remove empty strings, lists, and dicts

    Returns:
        Cleaned dictionary
    """
    cleaned = {}
    
    for key, value in data.items():
        # Skip None values if requested
        if remove_none and value is None:
            continue
            
        # Skip empty values if requested
        if remove_empty and not value and value != 0 and value is not False:
            continue
            
        cleaned[key] = value
    
    return cleaned


def validate_slug(slug: str) -> bool:
    """
    Validate that a string is a proper slug format.

    Args:
        slug: String to validate

    Returns:
        True if valid slug, False otherwise
    """
    if not slug:
        return False
    
    # Slug should only contain lowercase letters, numbers, and hyphens
    # Should not start or end with hyphen
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, slug))


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email, False otherwise
    """
    if not email:
        return False
    
    # Simple email validation regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default and validation.

    Args:
        key: Environment variable key
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required variable is not found
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' not found")
    
    return value


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Maximum size of each chunk

    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later dicts taking precedence.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def deep_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split(".")
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}" 