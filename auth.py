                         
from datetime import datetime
import os
import re
from fastapi import APIRouter, Depends, Header, HTTPException
import bcrypt
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import SessionLocal
from db_model import LoginEvent, Player, PlayerProfile
from models import GoogleAuthRequest, RegisterRequest, LoginRequest

load_dotenv()

SECRET_KEY = "your-secret-key"                                                  

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

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

def _sanitize_username(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]", "", value).strip("._-")
    return slug[:30] if slug else "player"

def _build_unique_username(base: str, db: Session) -> str:
    root = _sanitize_username(base)
    if not db.query(Player).filter(Player.username == root).first():
        return root

    suffix = 1
    while True:
        candidate = f"{root}_{suffix}"
        if not db.query(Player).filter(Player.username == candidate).first():
            return candidate
        suffix += 1

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Verificar si el usuario ya existe para evitar duplicados
    username = request.username.strip()
    user_exists = db.query(Player).filter(Player.username == username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    email = request.email.lower().strip() if request.email else None
    if email:
        email_exists = db.query(Player).filter(Player.email == email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # 2. Hashear la contraseña
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 3. Crear el nuevo registro y guardarlo
    new_player = Player(
        username=username,
        password=hashed_password,
        email=email,
        auth_provider="local"
    )
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

    if not player.password:
        raise HTTPException(status_code=401, detail="Este usuario usa inicio de sesión con Google")

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
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": player.username,
        "avatar_url": player.avatar_url
    }

@router.post("/auth/google")
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth no está configurado en el servidor")

    try:
        token_payload = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido")

    google_id = token_payload.get("sub")
    email = (token_payload.get("email") or "").lower().strip()
    name = (token_payload.get("name") or "").strip()
    avatar_url = token_payload.get("picture")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="El token de Google no contiene datos requeridos")

    player = db.query(Player).filter(Player.google_id == google_id).first()

    if not player:
        player = db.query(Player).filter(Player.email == email).first()
        if player:
            player.google_id = google_id
            player.avatar_url = avatar_url
        else:
            username_seed = name or email.split("@")[0]
            username = _build_unique_username(username_seed, db)
            player = Player(
                username=username,
                password=None,
                email=email,
                google_id=google_id,
                auth_provider="google",
                avatar_url=avatar_url
            )
            db.add(player)
            db.flush()

    if not player.email:
        player.email = email
    if avatar_url:
        player.avatar_url = avatar_url

    ensure_profile(player, db)
    db.add(LoginEvent(player_id=player.id, logged_at=datetime.now()))
    db.commit()
    db.refresh(player)

    token = jwt.encode({"sub": str(player.id)}, SECRET_KEY, algorithm="HS256")
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": player.username,
        "avatar_url": player.avatar_url
    }