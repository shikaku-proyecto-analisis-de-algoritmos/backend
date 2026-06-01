                         
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
import bcrypt
import jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from db_model import LoginEvent, Player, PlayerProfile
from models import RegisterRequest, LoginRequest

SECRET_KEY = "your-secret-key"                                                  

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_sub": False})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalido")

def get_current_player(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")

    payload = _decode_token(authorization.replace("Bearer ", "", 1))
    player_id = payload.get("sub")
    player = db.query(Player).filter(Player.id == int(player_id)).first() if player_id is not None else None
    if not player:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return player

def get_optional_player(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        return None

    payload = _decode_token(authorization.replace("Bearer ", "", 1))
    player_id = payload.get("sub")
    if player_id is None:
        return None
    return db.query(Player).filter(Player.id == int(player_id)).first()

def ensure_profile(player: Player, db: Session):
    profile = db.query(PlayerProfile).filter(PlayerProfile.player_id == player.id).first()
    if not profile:
        profile = PlayerProfile(player_id=player.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Verificar si el usuario ya existe para evitar duplicados
    user_exists = db.query(Player).filter(Player.username == request.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    # 2. Hashear la contraseña
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 3. Crear el nuevo registro y guardarlo
    new_player = Player(username=request.username, password=hashed_password)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    ensure_profile(new_player, db)
    return {"message": "Usuario registrado exitosamente", "user_id": new_player.id}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Usamos strip() para eliminar espacios accidentales al inicio o final
    username = request.username.strip()
    print(f"DEBUG: Intentando login para usuario: '{username}'")
    
    player = db.query(Player).filter(Player.username == username).first()
    
    if not player:
        print(f"DEBUG: Usuario '{username}' no encontrado en la BD.")
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Verificación de contraseña con bcrypt
    try:
        is_valid = bcrypt.checkpw(request.password.encode('utf-8'), player.password.encode('utf-8'))
    except Exception as e:
        print(f"DEBUG: Error al verificar hash: {e}")
        raise HTTPException(status_code=500, detail="Error en el sistema de seguridad")

    if not is_valid:
        print(f"DEBUG: Contraseña incorrecta para el usuario: '{username}'")
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    print(f"DEBUG: Login exitoso para: '{username}'")
    
    ensure_profile(player, db)
    db.add(LoginEvent(player_id=player.id, logged_at=datetime.now()))
    db.commit()
    
    token = jwt.encode({"sub": str(player.id)}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "username": player.username}