from database import engine, Base
from models import Player, GameRecord

Base.metadata.create_all(bind=engine)
print("Base de datos creada exitosamente!")