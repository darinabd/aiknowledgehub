from sqlalchemy.orm import Session

from app import models


def user_to_response(user: "models.User", db: Session) -> dict:
    document_count = (
        db.query(models.Document)
        .filter(models.Document.owner_id == user.id)
        .count()
    )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "document_count": document_count,
    }
