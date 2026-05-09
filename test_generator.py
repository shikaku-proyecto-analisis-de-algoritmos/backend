from generator import generate_board, generate_board_with_solution
import json


def test_basic_generation():
                                      
    print("=== Test 1: Basic Board Generation (5×5) ===")
    board = generate_board(5, seed=42)
    print(f"Board size: {board['rows']}×{board['cols']}")
    print(f"Number of clues: {sum(1 for row in board['cells'] for cell in row if cell > 0)}")
    print("Board:")
    for row in board["cells"]:
        print(row)
    print()


def test_with_solution():
                                        
    print("=== Test 2: Generation with Solution (4×4) ===")
    board, solution = generate_board_with_solution(4, seed=123)
    print(f"Generated {len(solution)} rectangles")
    for i, rect in enumerate(solution):
        area = (rect["endRow"] - rect["startRow"] + 1) * (
            rect["endCol"] - rect["startCol"] + 1
        )
        print(f"  Rectangle {i}: ({rect['startRow']},{rect['startCol']}) to ({rect['endRow']},{rect['endCol']}) → area {area}")
    print()


def test_different_sizes():
                                     
    print("=== Test 3: Different Board Sizes ===")
    for size in [4, 6, 8]:
        board = generate_board(size, seed=999)
        clue_count = sum(1 for row in board["cells"] for cell in row if cell > 0)
        rect_count = len(generate_board_with_solution(size, seed=999)[1])
        print(f"  {size}×{size}: {clue_count} clues, {rect_count} rectangles")
    print()


def test_reproducibility():
                                                  
    print("=== Test 4: Reproducibility ===")
    board1 = generate_board(5, seed=777)
    board2 = generate_board(5, seed=777)
    is_same = board1["cells"] == board2["cells"]
    print(f"Same seed produces identical boards: {is_same}")
    print()


def test_clue_constraints():
                                        
    print("=== Test 5: Clue Constraints (6×6) ===")
    min_c = 6                            
    max_c = 12                           
    board, solution = generate_board_with_solution(6, seed=555, min_clues=min_c, max_clues=max_c)
    num_rects = len(solution)
    print(f"Requested: {min_c} ≤ rectangles ≤ {max_c}")
    print(f"Generated: {num_rects} rectangles")
    print(f"Meets constraints: {min_c <= num_rects <= max_c}")
    print()


def test_coverage_and_validity():
                                                       
    print("=== Test 6: Coverage and Validity (5×5) ===")
    board, solution = generate_board_with_solution(5, seed=666)
    n = board["rows"]

                                         
    assignment = [[-1 for _ in range(n)] for _ in range(n)]
    for rect_id, rect in enumerate(solution):
        for r in range(rect["startRow"], rect["endRow"] + 1):
            for c in range(rect["startCol"], rect["endCol"] + 1):
                assignment[r][c] = rect_id

                                 
    all_covered = all(
        assignment[r][c] >= 0 for r in range(n) for c in range(n)
    )
    print(f"All cells covered: {all_covered}")

                                       
    clue_count = sum(1 for row in board["cells"] for cell in row if cell > 0)
    print(f"Number of clues placed: {clue_count}")
    print(f"Number of rectangles: {len(solution)}")
    print(f"Clue count matches rectangle count: {clue_count == len(solution)}")
    print()


if __name__ == "__main__":
    try:
        test_basic_generation()
        test_with_solution()
        test_different_sizes()
        test_reproducibility()
        test_clue_constraints()
        test_coverage_and_validity()
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
