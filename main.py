# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Board, SolveRequest, ValidateRequest
from boards import boards
from auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/board")
def get_board(difficulty: str = "easy"):
    return { "board": boards[difficulty] }

@app.post("/solve")
def solve(request: SolveRequest):
    # por ahora retorna vacío, luego conectamos el solver
    return { "solution": [] }

@app.post("/validate")
def validate(request: ValidateRequest):
    # por ahora siempre retorna inválido
    return { "valid": False }