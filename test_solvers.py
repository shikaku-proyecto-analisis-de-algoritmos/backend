from solver import precompute_candidates, solve_backtracking, solve_backtracking_cp
import time


def validate_solution(board, solution):     
    n = board["rows"]
    cells = board["cells"]
    
                                                                 
    occupancy = [[None] * n for _ in range(n)]
    clue_mapping = {}                                
    
    for rect_idx, rect in enumerate(solution):
        r1, c1, r2, c2 = rect["startRow"], rect["startCol"], rect["endRow"], rect["endCol"]
        area = (r2 - r1 + 1) * (c2 - c1 + 1)
        
                    
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if occupancy[r][c] is not None:
                    return False, f"Cell ({r},{c}) belongs to multiple rectangles"
                occupancy[r][c] = rect_idx
        
                                     
        clue_found = False
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if cells[r][c] > 0:
                    if clue_found:
                        return False, f"Rectangle has multiple clues"
                    if cells[r][c] != area:
                        return False, f"Clue {cells[r][c]} doesn't match rectangle area {area}"
                    clue_found = True
                    clue_mapping[(r, c, cells[r][c])] = rect_idx
        
        if not clue_found:
            return False, f"Rectangle has no clue"
    
                                 
    for r in range(n):
        for c in range(n):
            if cells[r][c] > 0:
                if (r, c, cells[r][c]) not in clue_mapping:
                    return False, f"Clue at ({r},{c}) not covered"
    
                                 
    for r in range(n):
        for c in range(n):
            if occupancy[r][c] is None:
                return False, f"Cell ({r},{c}) not covered"
    
    return True, "Valid"


def test_precompute_candidates():
                                        
    print("\n=== Test 1: Precompute Candidates ===") 
                              
    cells = [[0, 2, 0],
             [0, 0, 0],
             [0, 0, 0]]
    n = 3
    
    candidates = precompute_candidates(cells, n)                               
    key = (0, 1, 2)
    assert key in candidates
    expected_count = 3
    assert len(candidates[key]) == expected_count, f"Expected {expected_count}, got {len(candidates[key])}"
    print(f"✓ Candidates computed: {len(candidates[key])} for area 2")


def test_simple_puzzle():
                                           
    print("\n=== Test 2: Simple Puzzle (4×4) ===")
    
                                                       
                                                                                 
    board = {
        "rows": 4,
        "cols": 4,
        "cells": [
            [4, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 4, 0],
            [1, 0, 1, 0],
        ]
    }
                                         
                                              
    from generator import generate_board_with_solution as gen
    board, _ = gen(4, seed=999)
    
                             
    print("  Backtracking...", end="")
    start = time.time()
    sol_bt = solve_backtracking(board)
    time_bt = time.time() - start
    print(f" {time_bt*1000:.2f}ms")
    
                                       
    print("  Backtracking+CP...", end="")
    start = time.time()
    sol_cp = solve_backtracking_cp(board)
    time_cp = time.time() - start
    print(f" {time_cp*1000:.2f}ms")
    
                             
    for name, sol in [("BT", sol_bt), ("CP", sol_cp)]:
        if not sol:
            print(f"  ✗ {name}: No solution found")
            continue
        
        valid, msg = validate_solution(board, sol)
        if valid:
            print(f"  ✓ {name}: {len(sol)} rectangles")
        else:
            print(f"  ✗ {name}: {msg}")


def test_from_generator():
                                     
    print("\n=== Test 3: Generated Puzzle (6×6) ===")
    
    from generator import generate_board_with_solution as gen
    
                                               
    board, known_solution = gen(6, seed=42)
    
    print(f"  Testing with {len(known_solution)} clues...")
    
              
    print("  Backtracking...", end="")
    start = time.time()
    sol_bt = solve_backtracking(board)
    time_bt = time.time() - start
    print(f" {time_bt*1000:.2f}ms")
    
    print("  Backtracking+CP...", end="")
    start = time.time()
    sol_cp = solve_backtracking_cp(board)
    time_cp = time.time() - start
    print(f" {time_cp*1000:.2f}ms")
    
              
    for name, sol in [("BT", sol_bt), ("CP", sol_cp)]:
        if not sol:
            print(f"  ✗ {name}: No solution found")
            continue
        
        valid, msg = validate_solution(board, sol)
        if valid:
            print(f"  ✓ {name}: {len(sol)} rectangles")
        else:
            print(f"  ✗ {name}: {msg}")


def test_hardness():
                                                          
    print("\n=== Test 4: Solver Performance Comparison ===")
    
    from generator import generate_board_with_solution as gen
    
    for size in [5, 6, 7]:
        board, _ = gen(size, seed=999+size)
        
        print(f"\n  {size}×{size} puzzle:")
        
                      
        start = time.time()
        sol_bt = solve_backtracking(board)
        time_bt = time.time() - start
        
        valid_bt, _ = validate_solution(board, sol_bt) if sol_bt else (False, "No solution")
        status_bt = "✓" if valid_bt else "✗"
        print(f"    BT:   {status_bt} {time_bt*1000:.2f}ms" + (" (timeout)" if time_bt > 10 else ""))
        
                                
        start = time.time()
        sol_cp = solve_backtracking_cp(board)
        time_cp = time.time() - start
        
        valid_cp, _ = validate_solution(board, sol_cp) if sol_cp else (False, "No solution")
        status_cp = "✓" if valid_cp else "✗"
        print(f"    CP:   {status_cp} {time_cp*1000:.2f}ms" + (" (timeout)" if time_cp > 10 else ""))
        
                 
        if time_bt > 0:
            speedup = time_bt / time_cp
            print(f"    Speedup: {speedup:.1f}x")


def test_edge_cases():
                                            
    print("\n=== Test 5: Edge Cases ===")
    
                                                
    board_2x2 = {
        "rows": 2,
        "cols": 2,
        "cells": [
            [4, 0],
            [0, 0],
        ]
    }
    
    sol_bt = solve_backtracking(board_2x2)
    sol_cp = solve_backtracking_cp(board_2x2)
    
    for name, sol in [("BT", sol_bt), ("CP", sol_cp)]:
        if not sol:
            print(f"  ✗ 2×2 {name}: No solution")
            continue
        valid, msg = validate_solution(board_2x2, sol)
        if valid:
            print(f"  ✓ 2×2 {name}: Valid")
        else:
            print(f"  ✗ 2×2 {name}: {msg}")
    
                                              
    from generator import generate_board_with_solution as gen
    board_3x3, _ = gen(3, seed=111)
    
    sol_bt = solve_backtracking(board_3x3)
    sol_cp = solve_backtracking_cp(board_3x3)
    
    for name, sol in [("BT", sol_bt), ("CP", sol_cp)]:
        if not sol:
            print(f"  ✗ 3×3 {name}: No solution")
            continue
        valid, msg = validate_solution(board_3x3, sol)
        if valid:
            print(f"  ✓ 3×3 {name}: Valid")
        else:
            print(f"  ✗ 3×3 {name}: {msg}")


def test_reproducibility():
                                           
    print("\n=== Test 6: Reproducibility ===")
    
    from generator import generate_board_with_solution as gen
    
    board, _ = gen(5, seed=777)
    
                          
    solutions = [
        solve_backtracking(board),
        solve_backtracking(board),
        solve_backtracking_cp(board),
        solve_backtracking_cp(board),
    ]
    
                                           
    all_same = all(sol == solutions[0] for sol in solutions)
    if all_same:
        print("  ✓ Both solvers are deterministic")
    else:
        print("  ✗ Solutions differ (non-deterministic)")


if __name__ == "__main__":
    try:
        test_precompute_candidates()
        test_simple_puzzle()
        test_from_generator()
        test_hardness()
        test_edge_cases()
        test_reproducibility()
        
        print("\n" + "="*50)
        print("✓ All tests completed!")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
