from pathlib import Path
from datetime import datetime

from docx import Document
from pypdf import PdfReader


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
    try:
        path = Path(filepath)

        if not path.exists():
            return {
                "success": False,
                "content": "",
                "metadata": {},
                "error": "File not found."
            }

        extension = path.suffix.lower()

        if extension == ".txt":
            content = path.read_text(encoding="utf-8")

        elif extension == ".docx":
            document = Document(path)

            content = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        elif extension == ".pdf":
            reader = PdfReader(str(path))
            pages = []

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    pages.append(text.strip())

            content = "\n\n".join(pages)

            if not content.strip():
                return {
                    "success": False,
                    "content": "",
                    "metadata": {},
                    "error": (
                        "PDF was opened successfully, but no extractable "
                        "text was found."
                    )
                }

        else:
            return {
                "success": False,
                "content": "",
                "metadata": {},
                "error": f"Unsupported file type: {extension}"
            }

        metadata = {
            "filename": path.name,
            "filepath": str(path.resolve()),
            "extension": extension,
            "size_bytes": path.stat().st_size,
            "modified": datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat()
        }

        return {
            "success": True,
            "content": content,
            "metadata": metadata,
            "error": None
        }

    except Exception as exc:
        return {
            "success": False,
            "content": "",
            "metadata": {},
            "error": str(exc)
        }
        
def list_files(directory: str, extension: str = None) -> list:
    """
    List files in a directory.

    Args:
        directory: Directory path.
        extension: Optional extension filter.

    Returns:
        List of dictionaries describing each file.
    """
    try:
        path = Path(directory)

        if not path.exists() or not path.is_dir():
            return []

        if extension:
            extension = extension.lower()
            if not extension.startswith("."):
                extension = "." + extension

        files = []

        for file in sorted(path.iterdir()):

            if not file.is_file():
                continue

            if extension and file.suffix.lower() != extension:
                continue

            files.append(
                {
                    "name": file.name,
                    "path": str(file.resolve()),
                    "size_bytes": file.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat(),
                }
            )

        return files

    except Exception:
        return []


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
    try:
        path = Path(filepath)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "path": str(path.resolve()),
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "path": filepath,
            "error": str(exc),
        }


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
    file_result = read_file(filepath)

    if not file_result["success"]:
        return {
            "success": False,
            "matches": [],
            "count": 0,
        }

    keyword_lower = keyword.lower()
    matches = []

    lines = file_result["content"].splitlines()

    for line_number, line in enumerate(lines, start=1):

        if keyword_lower in line.lower():

            matches.append(
                {
                    "line": line_number,
                    "context": line.strip(),
                }
            )

    return {
        "success": True,
        "matches": matches,
        "count": len(matches),
    }