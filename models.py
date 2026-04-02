# models.py
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

class ValidateRequest(BaseModel):
    board: Board
    rectangles: List[Rectangle]