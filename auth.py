# auth.py - login con JWT
from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt
import jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from db_model import Player

SECRET_KEY = "your-secret-key"  # Cambia esto por una clave segura en producción

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == username).first()
    if not player or not bcrypt.verify(password, player.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = jwt.encode({"sub": player.id}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}