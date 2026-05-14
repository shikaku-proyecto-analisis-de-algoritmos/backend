from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Board, SolveRequest, ValidateRequest, HintRequest
from boards import get_board
from auth import router as auth_router
from solver import solve_backtracking, solve_backtracking_cp
from hints import get_hint
from database import engine, Base  
import models as db_models 

app = FastAPI()

@app.on_event("startup") 

def startup():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/board")
def fetch_board(difficulty: str = "easy", seed: int = None):
    board = get_board(difficulty=difficulty, seed=seed)
    return {"board": board}

@app.post("/solve")
def solve(request: SolveRequest):
    board_dict = request.board.dict()
    if request.solver_type == "bt":
        solution = solve_backtracking(board_dict)
    else:
        solution = solve_backtracking_cp(board_dict)
    return {"solution": solution}

@app.post("/validate")
def validate(request: ValidateRequest):
    return { "valid": False }


@app.post("/hint")
def hint(request: HintRequest):
    result = get_hint(
        board=request.board.dict(),
        user_rectangles=[r.dict() for r in request.user_rectangles]
    )
    return result