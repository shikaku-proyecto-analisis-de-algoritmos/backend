from generator import generate_board, generate_board_with_solution
import json

print("=" * 60)
print("SHIKAKU BOARD GENERATOR - DEMO")
print("=" * 60)

                          
print("\n[1] Generating 6×6 board with seed=999")
board = generate_board(6, seed=999)
clue_count = sum(1 for row in board["cells"] for cell in row if cell > 0)
print(f"    ✓ Generated with {clue_count} clues")
print(f"    Board size: {board['rows']}×{board['cols']}")
print("\n    Grid layout:")
for i, row in enumerate(board["cells"]):
    print(f"    Row {i}: {row}")

                       
print("\n[2] Generating 5×5 board with solution")
board, solution = generate_board_with_solution(5, seed=42)
print(f"    ✓ Generated {len(solution)} rectangles")
print(f"    Solution:")
for i, rect in enumerate(solution):
    r1, c1, r2, c2 = rect["startRow"], rect["startCol"], rect["endRow"], rect["endCol"]
    area = (r2 - r1 + 1) * (c2 - c1 + 1)
    print(f"      [{i}] ({r1},{c1})-({r2},{c2}) area={area}")

                         
print("\n[3] Testing reproducibility (seed=123)")
b1 = generate_board(4, seed=123)
b2 = generate_board(4, seed=123)
match = b1["cells"] == b2["cells"]
print(f"    ✓ Same seed produces identical boards: {match}")

                           
print("\n[4] Different difficulty levels (seed=777)")
for difficulty in ["easy", "medium", "hard"]:
    from boards import get_board
    board = get_board(difficulty, seed=777)
    clues = sum(1 for row in board["cells"] for cell in row if cell > 0)
    print(f"    {difficulty:8} → {board['rows']}×{board['cols']} with {clues} clues")

print("\n" + "=" * 60)
print("✓ All demos completed successfully!")
print("=" * 60)
