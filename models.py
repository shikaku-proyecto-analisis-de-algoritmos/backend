from pydantic import BaseModel
from typing import List


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


class ValidateRequest(BaseModel):
    board: Board
    rectangles: List[Rectangle]
    

class HintRequest(BaseModel):
    board: Board
    user_rectangles: List[Rectangle] = []


class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"