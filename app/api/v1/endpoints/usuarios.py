from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.analisis import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash # La que creamos con passlib

router = APIRouter()

@router.post("/register", response_model=UserOut, tags=["Usuarios"])
def registrar_usuario(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Verificar si ya existe
    user_db = db.query(User).filter(User.email == user_in.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # 2. Hashear password y crear objeto
    hashed_pw = get_password_hash(user_in.password)
    nuevo_usuario = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario