from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.security import get_current_user, hash_password, verify_password
from app.utils import user_to_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_to_response(current_user, db)


@router.put("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.email and payload.email != current_user.email:
        existing = (
            db.query(models.User)
            .filter(models.User.email == payload.email, models.User.id != current_user.id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = payload.email

    if payload.username:
        current_user.username = payload.username

    db.commit()
    db.refresh(current_user)

    return user_to_response(current_user, db)


@router.put("/me/password")
def change_password(
    payload: PasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
