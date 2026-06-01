from pydantic import BaseModel
from typing import List, Optional


class Board(BaseModel):
    rows: int
    cols: int
    cells: List[List[int]]

class Rectangle(BaseModel):
    startRow: int
    startCol: int
    endRow: int
    endCol: int

class SolveRequest(BaseModel):
    board: Board
    solver_type: str = "cp"
    difficulty: Optional[str] = None
    level: Optional[int] = None
    elapsed_secs: Optional[int] = None


class ValidateRequest(BaseModel):
    board: Board
    rectangles: List[Rectangle]
    difficulty: Optional[str] = None
    level: Optional[int] = None
    time_secs: Optional[int] = None
    hints_used: Optional[int] = 0
    solve_used: Optional[bool] = False
    

class HintRequest(BaseModel):
    board: Board
    user_rectangles: List[Rectangle] = []
    difficulty: Optional[str] = None
    level: Optional[int] = None
    elapsed_secs: Optional[int] = None

class SessionStartRequest(BaseModel):
    difficulty: str
    level: int = 1


class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
