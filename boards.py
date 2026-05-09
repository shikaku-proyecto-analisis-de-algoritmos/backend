           
from generator import generate_board

def get_board(difficulty: str = "easy", seed: int = None) -> dict:  
    difficulty_config = {
        "easy": {"size": 5, "min_clues": 5, "max_clues": 8},
        "medium": {"size": 8, "min_clues": 12, "max_clues": 20},
        "hard": {"size": 10, "min_clues": 15, "max_clues": 25},
    }
    
    config = difficulty_config.get(difficulty, difficulty_config["easy"])
    board = generate_board(
        n=config["size"],
        seed=seed,
        min_clues=config["min_clues"],
        max_clues=config["max_clues"]
    )
    return board


                                                    
boards = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "cells": [
            [0, 0, 2, 0, 7],
            [0, 0, 0, 0, 3],
            [4, 0, 0, 0, 0],
            [0, 0, 0, 2, 0],
            [0, 0, 4, 0, 0],
        ]
    }
}