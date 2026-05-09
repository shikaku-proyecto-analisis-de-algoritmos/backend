from typing import Dict, List, Tuple, Optional


def precompute_candidates(cells: List[List[int]], n: int) -> Dict:       
    candidates = {}
    
    for r in range(n):
        for c in range(n):
            v = cells[r][c]
            if v > 0:
                candidates[(r, c, v)] = []
                
                                                                     
                for h in range(1, v + 1):
                    if v % h == 0:
                        w = v // h
                        
                                                                                        
                        r1_min = max(0, r - h + 1)
                        r1_max = min(r, n - h)
                        
                                                                                       
                        c1_min = max(0, c - w + 1)
                        c1_max = min(c, n - w)
                        
                                                       
                        for r1 in range(r1_min, r1_max + 1):
                            for c1 in range(c1_min, c1_max + 1):
                                r2 = r1 + h - 1
                                c2 = c1 + w - 1
                                candidates[(r, c, v)].append((r1, c1, r2, c2))
    return candidates


def solve_backtracking(board: Dict) -> List[Dict]:     
    n = board["rows"]
    cells = board["cells"]
    
                                          
    clues = []
    for r in range(n):
        for c in range(n):
            if cells[r][c] > 0:
                clues.append((r, c, cells[r][c]))
    
    if not clues:
        return []
    
                                         
    candidates_dict = precompute_candidates(cells, n)
    
                                             
    candidates_list = [candidates_dict[(r, c, v)] for r, c, v in clues]
    
                                                                   
                                                                            
    clue_order = sorted(range(len(clues)), key=lambda i: len(candidates_list[i]))
    
                                                                   
    occupancy = [[False] * n for _ in range(n)]
    
                                                                            
    solution = [None] * len(clues)
    
    def backtrack(clue_idx: int) -> bool:                                      
        if clue_idx == len(clue_order):
            return True
        
                                                     
        original_clue_idx = clue_order[clue_idx]
        r, c, v = clues[original_clue_idx]
        candidates = candidates_dict[(r, c, v)]
        
                                                    
        for r1, c1, r2, c2 in candidates:
                                                                     
            valid = True
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    if occupancy[rr][cc]:
                        valid = False
                        break
                if not valid:
                    break
            
            if not valid:
                continue                      
            
                                    
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    occupancy[rr][cc] = True
            
            solution[original_clue_idx] = (r1, c1, r2, c2)
            
                                  
            if backtrack(clue_idx + 1):
                return True
            
                                     
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    occupancy[rr][cc] = False
            
            solution[original_clue_idx] = None
        
        return False                                          
    
                      
    if backtrack(0):
        return [
            {"startRow": r1, "startCol": c1, "endRow": r2, "endCol": c2}
            for r1, c1, r2, c2 in solution
        ]
    
    return []


def solve_backtracking_cp(board: Dict) -> List[Dict]:   
    n = board["rows"]
    cells = board["cells"]
    
                       
    clues = []
    for r in range(n):
        for c in range(n):
            if cells[r][c] > 0:
                clues.append((r, c, cells[r][c]))
    
    if not clues:
        return []
    
                           
    candidates_dict = precompute_candidates(cells, n)
    
                                                                            
    remaining_candidates = {}
    for i, (r, c, v) in enumerate(clues):
        remaining_candidates[i] = candidates_dict[(r, c, v)][:]
    
                        
    occupancy = [[False] * n for _ in range(n)]
    
                                          
    assigned = [False] * len(clues)
    
                                                        
    solution = [None] * len(clues)
    
    def is_feasible() -> bool:
                                                                      
        for i in range(len(clues)):
            if not assigned[i] and len(remaining_candidates[i]) == 0:
                return False
        return True
    
    def apply_forward_checking():      
        for i in range(len(clues)):
            if assigned[i]:
                continue
            
                                                  
            viable = []
            for r1, c1, r2, c2 in remaining_candidates[i]:
                overlaps = False
                for rr in range(r1, r2 + 1):
                    for cc in range(c1, c2 + 1):
                        if occupancy[rr][cc]:
                            overlaps = True
                            break
                    if overlaps:
                        break
                
                if not overlaps:
                    viable.append((r1, c1, r2, c2))
            
            remaining_candidates[i] = viable
    
    def place_rectangle(clue_idx: int, r1: int, c1: int, r2: int, c2: int):
                                                                        
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                occupancy[rr][cc] = True
        assigned[clue_idx] = True
        solution[clue_idx] = (r1, c1, r2, c2)
    
    def backtrack() -> bool:                                                            
        while True:
                                                      
            if not is_feasible():
                return False
            
                                                            
            units = [i for i in range(len(clues)) 
                    if not assigned[i] and len(remaining_candidates[i]) == 1]
            
            if not units:
                break                                      
            
                                         
            for u in units:
                r1, c1, r2, c2 = remaining_candidates[u][0]
                place_rectangle(u, r1, c1, r2, c2)
                
                                                              
                apply_forward_checking()
        
                                         
        if all(assigned):
            return True
        
                                                                          
        next_idx = min((i for i in range(len(clues)) if not assigned[i]),
                      key=lambda i: len(remaining_candidates[i]),
                      default=None)
        
        if next_idx is None:
            return True                
        
                                         
        for r1, c1, r2, c2 in remaining_candidates[next_idx][:]:             
                                
            saved_remaining = {i: remaining_candidates[i][:] for i in range(len(clues))}
            saved_occupancy = [row[:] for row in occupancy]
            saved_assigned = assigned[:]
            saved_solution = solution[:]
            
                             
            place_rectangle(next_idx, r1, c1, r2, c2)
            
                                             
            apply_forward_checking()
            
            if is_feasible() and backtrack():
                return True
            
                                      
            for i in range(len(clues)):
                remaining_candidates[i] = saved_remaining[i]
            for rr in range(n):
                for cc in range(n):
                    occupancy[rr][cc] = saved_occupancy[rr][cc]
            assigned[:] = saved_assigned
            solution[:] = saved_solution
        
        return False                             
    
                                                  
    if backtrack():
        return [
            {"startRow": r1, "startCol": c1, "endRow": r2, "endCol": c2}
            for r1, c1, r2, c2 in solution if r1 is not None
        ]
    
    return []
