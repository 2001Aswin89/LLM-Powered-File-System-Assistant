"""
File system tools for the Resume File Assistant.
"""


def read_file(filepath: str) -> dict:
    """
    Read a supported file and return its content and metadata.

    Args:
        filepath: Path to the file.

    Returns:
        {
            "success": bool,
            "content": str,
            "metadata": dict,
            "error": str | None,
        }
    """
    raise NotImplementedError


def list_files(directory: str, extension: str = None) -> list:
    """
    List files in a directory.

    Args:
        directory: Directory path.
        extension: Optional extension filter.

    Returns:
        List of dictionaries describing each file.
    """
    raise NotImplementedError


def write_file(filepath: str, content: str) -> dict:
    """
    Write text content to a file.

    Args:
        filepath: Destination path.
        content: Text to write.

    Returns:
        {
            "success": bool,
            "path": str,
            "error": str | None,
        }
    """
    raise NotImplementedError


def search_in_file(filepath: str, keyword: str) -> dict:
    """
    Search for a keyword within a supported file.

    Args:
        filepath: File path.
        keyword: Search keyword.

    Returns:
        {
            "success": bool,
            "matches": list,
            "count": int,
        }
    """
    raise NotImplementedError