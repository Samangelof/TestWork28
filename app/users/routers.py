from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.deps import get_db
from app.core.config import settings
from app.users import schemas, services


router = APIRouter(tags=["auth"])

@router.post("/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.register_new_user(db, user_in)

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = services.authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    return services.create_user_tokens(user.id)

@router.post("/refresh", response_model=schemas.Token)
def refresh(token_data: schemas.RefreshToken, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token_data.refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")

    user = services.crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return services.create_user_tokens(user.id)