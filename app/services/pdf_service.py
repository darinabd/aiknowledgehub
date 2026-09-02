from typing import Optional

from pypdf import PdfReader


def get_page_count(file_path: str) -> Optional[int]:
    """Return the number of pages in a PDF, or None if it can't be read."""
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception:
        return None
