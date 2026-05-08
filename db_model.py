# models.py
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Player(Base):
    __tablename__ = "players"
    id       = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)  # hashear con bcrypt
    score    = Column(Integer, default=0)

class GameRecord(Base):
    __tablename__ = "game_records"
    id         = Column(Integer, primary_key=True)
    player_id  = Column(Integer)
    difficulty = Column(String)
    time_secs  = Column(Integer)
    completed  = Column(DateTime)