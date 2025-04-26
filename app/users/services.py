from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.users import crud, schemas
from app.core.security import verify_password, create_access_token, create_refresh_token


def register_new_user(db: Session, user_data: schemas.UserCreate):
    if crud.get_user_by_email(db, email=user_data.email):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    return crud.create_user(db=db, user=user_data)

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_tokens(user_id: int):
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer"
    }