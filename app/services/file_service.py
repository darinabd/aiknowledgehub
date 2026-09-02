import os
import shutil
import uuid
from typing import Tuple

from fastapi import UploadFile
from pypdf import PdfReader

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(file: UploadFile) -> Tuple[str, str]:
    """Save an uploaded file under a unique name on disk.

    Returns a tuple of (stored_path, original_filename) so the original
    filename can still be shown to the user while avoiding collisions
    or overwrites on disk.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path, file.filename


def delete_file(file_path: str) -> None:
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

def extract_text_from_pdf(file_path: str)-> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"
    return text 