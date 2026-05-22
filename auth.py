                         
from fastapi import APIRouter, Depends, HTTPException
import bcrypt
import jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from db_model import Player
from models import RegisterRequest

SECRET_KEY = "your-secret-key"                                                  

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Verificar si el usuario ya existe para evitar duplicados
    user_exists = db.query(Player).filter(Player.username == request.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    # 2. Hashear la contraseña (nunca guardes contraseñas en texto plano)
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 3. Crear el nuevo registro y guardarlo
    new_player = Player(username=request.username, password=hashed_password)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return {"message": "Usuario registrado exitosamente", "user_id": new_player.id}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == username).first()
    if not player or not bcrypt.checkpw(password.encode('utf-8'), player.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = jwt.encode({"sub": player.id}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}