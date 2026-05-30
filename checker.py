from typing import List
from models import Board, Rectangle

def check_solution(board: Board, rectangles: List[Rectangle]):
    rows = board.rows
    cols = board.cols
    cells = board.cells

    occupancy = [[0] * cols for _ in range(rows)]

    for r in rectangles:
        if r.startRow > r.endRow or r.startCol > r.endCol:
            return {"valid": False}

        clues_count = 0
        clue_value = 0
        area = (r.endRow - r.startRow + 1) * (r.endCol - r.startCol + 1)

        for i in range(r.startRow, r.endRow + 1):
            for j in range(r.startCol, r.endCol + 1):
                if i < 0 or i >= rows or j < 0 or j >= cols:
                    return {"valid": False}
                
                occupancy[i][j] += 1
                if occupancy[i][j] > 1:
                    return {"valid": False}
                
                if cells[i][j] > 0:
                    clues_count += 1
                    clue_value = cells[i][j]

        if clues_count != 1 or area != clue_value:
            return {"valid": False}

    for i in range(rows):
        for j in range(cols):
            if occupancy[i][j] != 1:
                return {"valid": False}

    return {"valid": True}