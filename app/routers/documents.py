import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.models.chunk import DocumentChunk
from app.services.file_service import save_file, delete_file, extract_text_from_pdf
from app.services.pdf_service import get_page_count
from app.services.text_service import split_text
from app.security import get_current_user
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentStats

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _get_owned_document(document_id: int, db: Session, current_user: User) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    return document


@router.post("/upload", response_model=DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    stored_path, original_name = save_file(file)
    size = os.path.getsize(stored_path)

    if size > MAX_FILE_SIZE:
        delete_file(stored_path)
        raise HTTPException(status_code=400, detail="File exceeds the 50MB limit")

    text = extract_text_from_pdf(stored_path)
    chunks = split_text(text)
    print(f"Chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):
        print("=" * 50)
        print(f"CHUNK {i + 1}")
        print(chunk)

    print("=" * 50)
    print("TEXT FROM PDF:")
    print(text[:1000])   
    print("=" * 50)
    
    document = Document(
        filename=original_name,
        file_path=stored_path,
        file_type=file.content_type,
        size=size,
        page_count=get_page_count(stored_path),
        owner_id=current_user.id,
        text=text,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunks = split_text(text)

    for index, chunk_text in enumerate(chunks):
        chunk = DocumentChunk(
            content=chunk_text,
            chunk_index=index,
            document_id=document.id,
        )

        db.add(chunk)
    db.commit()

    return document


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    search: Optional[str] = Query(None, description="Search by filename"),
    file_type: Optional[str] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|filename|size)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.owner_id == current_user.id)

    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    if file_type:
        query = query.filter(Document.file_type == file_type)

    sort_column = getattr(Document, sort_by)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    documents = query.all()

    return {"total": len(documents), "items": documents}


@router.get("/stats", response_model=DocumentStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    total_size = sum(d.size or 0 for d in documents)

    return {
        "total_documents": len(documents),
        "storage_used_bytes": total_size,
        "storage_used_mb": round(total_size / (1024 * 1024), 2),
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_document(document_id, db, current_user)


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document(document_id, db, current_user)

    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        document.file_path,
        filename=document.filename,
        media_type=document.file_type or "application/octet-stream",
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document(document_id, db, current_user)

    delete_file(document.file_path)
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
