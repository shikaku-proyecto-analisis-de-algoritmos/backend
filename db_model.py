           
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from database import Base

class Player(Base):
    __tablename__ = "players"
    id       = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    google_id = Column(String, unique=True, nullable=True, index=True)
    auth_provider = Column(String, default="local")
    avatar_url = Column(String, nullable=True)
    score    = Column(Integer, default=0)

class PlayerProfile(Base):
    __tablename__ = "player_profiles"
    id         = Column(Integer, primary_key=True)
    player_id  = Column(Integer, ForeignKey("players.id"), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GameRecord(Base):
    __tablename__ = "game_records"
    id         = Column(Integer, primary_key=True)
    player_id  = Column(Integer)
    difficulty = Column(String)
    time_secs  = Column(Integer)
    completed  = Column(DateTime)

class LoginEvent(Base):
    __tablename__ = "login_events"
    id        = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

class GameSession(Base):
    __tablename__ = "game_sessions"
    id          = Column(Integer, primary_key=True)
    player_id   = Column(Integer, ForeignKey("players.id"), index=True)
    difficulty  = Column(String, index=True)
    level       = Column(Integer, default=1)
    started_at  = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    completed   = Column(Boolean, default=False)
    manual      = Column(Boolean, default=True)
    time_secs   = Column(Integer, default=0)
    hints_used  = Column(Integer, default=0)
    solve_used  = Column(Boolean, default=False)

class SolveEvent(Base):
    __tablename__ = "solve_events"
    id                 = Column(Integer, primary_key=True)
    player_id          = Column(Integer, ForeignKey("players.id"), index=True)
    difficulty         = Column(String, index=True)
    level              = Column(Integer, default=1)
    solver_type        = Column(String, index=True)
    elapsed_before_secs = Column(Integer, default=0)
    created_at         = Column(DateTime, default=datetime.utcnow, index=True)

class HintEvent(Base):
    __tablename__ = "hint_events"
    id          = Column(Integer, primary_key=True)
    player_id   = Column(Integer, ForeignKey("players.id"), index=True)
    difficulty  = Column(String, index=True)
    level       = Column(Integer, default=1)
    elapsed_secs = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow, index=True)
