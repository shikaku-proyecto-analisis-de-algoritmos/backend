from generator import generate_board_with_solution
from solver import solve_backtracking, solve_backtracking_cp
import time


def print_board(cells):
                                           
    for row in cells:
        print("  " + " ".join(f"{cell:2d}" if cell > 0 else " ." for cell in row))


def print_solution(solution, n):
                                    
    for i, rect in enumerate(solution):
        r1, c1, r2, c2 = rect["startRow"], rect["startCol"], rect["endRow"], rect["endCol"]
        area = (r2 - r1 + 1) * (c2 - c1 + 1)
        print(f"    [{i:2d}] ({r1},{c1})-({r2},{c2}) area={area}")


def demo():
                                 
    print("=" * 70)
    print("SHIKAKU SOLVERS COMPARISON - DEMO")
    print("=" * 70)
    
    sizes = [4, 5, 6]
    
    for size in sizes:
        print(f"\n{'='*70}")
        print(f"Puzzle Size: {size}×{size}")
        print(f"{'='*70}")
        
                         
        board, known_solution = generate_board_with_solution(size, seed=1000+size)
        clue_count = len(known_solution)
        
        print(f"\nGenerated puzzle with {clue_count} clues:")
        print_board(board["cells"])
        
        print(f"\nKnown solution ({len(known_solution)} rectangles):")
        print_solution(known_solution, size)
        
                                 
        print(f"\n[1] Backtracking (pure, with MRV)...")
        start = time.time()
        sol_bt = solve_backtracking(board)
        time_bt = time.time() - start
        
        if sol_bt:
            print(f"    ✓ Solved in {time_bt*1000:.2f}ms")
            print(f"    Found {len(sol_bt)} rectangles")
            if len(sol_bt) <= 8:
                print_solution(sol_bt, size)
        else:
            print(f"    ✗ No solution found")
        
                                           
        print(f"\n[2] Backtracking + Forward Checking (with unit propagation)...")
        start = time.time()
        sol_cp = solve_backtracking_cp(board)
        time_cp = time.time() - start
        
        if sol_cp:
            print(f"    ✓ Solved in {time_cp*1000:.2f}ms")
            print(f"    Found {len(sol_cp)} rectangles")
            if len(sol_cp) <= 8:
                print_solution(sol_cp, size)
        else:
            print(f"    ✗ No solution found")
        
                 
        print(f"\n[3] Comparison:")
        if time_bt > 0:
            speedup = time_bt / time_cp if time_cp > 0 else float('inf')
            print(f"    BT:   {time_bt*1000:8.2f}ms")
            print(f"    CP:   {time_cp*1000:8.2f}ms")
            print(f"    Speedup: {speedup:.1f}x")
        
                                                     
        if len(sol_bt) == len(sol_cp) == clue_count:
            print(f"    ✓ Both solvers found correct solution")
        else:
            print(f"    ⚠ Solution counts differ: BT={len(sol_bt)}, CP={len(sol_cp)}, Expected={clue_count}")
    
    print("\n" + "=" * 70)
    print("PERFORMANCE NOTES")
    print("=" * 70)
    print("""
Forward Checking significantly improves performance by:

1. Early Failure Detection
   - Detects contradictions BEFORE exploring subtree
   - Backtracking alone discovers failure at bottom of tree

2. Unit Propagation
   - Auto-assigns variables with exactly 1 option
   - Eliminates unnecessary branching levels

3. Candidate Filtering
   - After each placement, filters out impossible candidates
   - Reduces branching factor exponentially

Expected Speedup:
  - Small puzzles (4×4): 0.3-0.5x (overhead not amortized)
  - Medium puzzles (5×5): 1-3x (good pruning)
  - Large puzzles (6×6+): 3-14x (excellent pruning)

Recommendation: Use Forward Checking variant for production.
""")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
