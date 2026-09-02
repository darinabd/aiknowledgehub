from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.user import User
from app.schemas.chat import AskQuestionRequest, AskQuestionResponse

from app.security import get_current_user
from app.services.rag_service import (
    find_relevant_chunks,
    generate_answer,
    generate_document_summary,
    generate_document_questions,
)


router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)


@router.post(
    "/documents/{document_id}/ask",
    response_model=AskQuestionResponse,
)
def ask_document_question(
    document_id: int,
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this document",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document has no text chunks",
        )

    try:
        relevant_chunks = find_relevant_chunks(
            question=request.question,
            chunks=chunks,
            limit=5,
        )

        answer = generate_answer(
            question=request.question,
            relevant_chunks=relevant_chunks,
        )

    except Exception as error:
        print("AI ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI answer",
        )

    return {
        "document_id": document.id,
        "question": request.question,
        "answer": answer,
        "sources": relevant_chunks,
    }

@router.post("/documents/{document_id}/summary")
def summarize_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this document",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document has no text chunks",
        )

    try:
        summary = generate_document_summary(chunks)
    except Exception as error:
        print("SUMMARY ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate document summary",
        )

    return {
        "document_id": document.id,
        "summary": summary,
    }


@router.post("/documents/{document_id}/questions")
def create_document_questions(
    document_id: int,
    amount: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if amount < 1 or amount > 20:
        raise HTTPException(
            status_code=400,
            detail="Amount must be between 1 and 20",
        )

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this document",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document has no text chunks",
        )

    try:
        questions = generate_document_questions(
            chunks=chunks,
            amount=amount,
        )
    except Exception as error:
        print("QUESTIONS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate questions",
        )

    return {
        "document_id": document.id,
        "amount": amount,
        "questions": questions,
    }