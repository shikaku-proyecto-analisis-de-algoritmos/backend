import random
from typing import List, Dict, Tuple, Optional


def generate_board(
    n: int,
    seed: Optional[int] = None,
    min_clues: Optional[int] = None,
    max_clues: Optional[int] = None,
    max_retries: int = 100
) -> Dict:
       
    if min_clues is None:
        min_clues = n * n // 4
    if max_clues is None:
        max_clues = n * n // 2

    for attempt in range(max_retries):
        board, _ = generate_board_with_solution(n, seed, min_clues, max_clues)
        if board is not None:
            return board

                                                 
    board, _ = generate_board_with_solution(n, seed)
    return board


def generate_board_with_solution(
    n: int,
    seed: Optional[int] = None,
    min_clues: Optional[int] = None,
    max_clues: Optional[int] = None
) -> Tuple[Optional[Dict], List[Dict]]:    
    if min_clues is None:
        min_clues = n * n // 4
    if max_clues is None:
        max_clues = n * n // 2

    rng = random.Random(seed)

                                                           
    assignment = [[None for _ in range(n)] for _ in range(n)]
    rectangles: List[Dict] = []
    rect_id = 0

                                                           
    while True:
                                               
        free_cell = _find_first_free_cell(assignment, n)
        if free_cell is None:
            break                  

        sr, sc = free_cell

                                                          
        valid_rects = _enumerate_valid_rectangles(assignment, n, sr, sc)

        if not valid_rects:
            raise RuntimeError(
                f"No valid rectangles found for free cell ({sr}, {sc}). "
                "This shouldn't happen with sequential placement."
            )

                                                                  
        max_area = min(n * n // 2, 9)
        valid_rects = [r for r in valid_rects if r["area"] <= max_area]

        if not valid_rects:
            raise RuntimeError(
                f"No valid rectangles after area filtering at ({sr}, {sc}). "
                "Decrease max_area or adjust clue constraints."
            )

                                       
        chosen = rng.choice(valid_rects)
        r1, c1, r2, c2 = (
            chosen["r1"],
            chosen["c1"],
            chosen["r2"],
            chosen["c2"],
        )
        area = chosen["area"]

                                      
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                assignment[r][c] = rect_id

                                      
        rectangles.append(
            {
                "startRow": r1,
                "startCol": c1,
                "endRow": r2,
                "endCol": c2,
            }
        )

        rect_id += 1

                                                       
    num_rects = len(rectangles)
    if not (min_clues <= num_rects <= max_clues):
        return None, []                                   

                                 
    cells = [[0 for _ in range(n)] for _ in range(n)]
    for rect in rectangles:
        r1, c1, r2, c2 = (
            rect["startRow"],
            rect["startCol"],
            rect["endRow"],
            rect["endCol"],
        )
        area = (r2 - r1 + 1) * (c2 - c1 + 1)

                                                        
        positions = [
            (r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)
        ]
        clue_r, clue_c = rng.choice(positions)
        cells[clue_r][clue_c] = area

    board = {"rows": n, "cols": n, "cells": cells}

    return board, rectangles


def _find_first_free_cell(
    assignment: List[List[Optional[int]]], n: int
) -> Optional[Tuple[int, int]]:
    for r in range(n):
        for c in range(n):
            if assignment[r][c] is None:
                return (r, c)
    return None


def _enumerate_valid_rectangles(
    assignment: List[List[Optional[int]]], n: int, sr: int, sc: int
) -> List[Dict]:  
    valid = []

    for r1 in range(sr + 1):
        for r2 in range(sr, n):
            for c1 in range(sc + 1):
                for c2 in range(sc, n):
                                                                       
                    all_free = True
                    for r in range(r1, r2 + 1):
                        for c in range(c1, c2 + 1):
                            if assignment[r][c] is not None:
                                all_free = False
                                break
                        if not all_free:
                            break

                    if all_free:
                        area = (r2 - r1 + 1) * (c2 - c1 + 1)
                        valid.append(
                            {
                                "r1": r1,
                                "c1": c1,
                                "r2": r2,
                                "c2": c2,
                                "area": area,
                            }
                        )

    return valid
