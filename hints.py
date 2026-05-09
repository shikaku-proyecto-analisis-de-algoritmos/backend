from solver import precompute_candidates


def _rect_cells(rect: dict) -> set[tuple[int, int]]:
    cells = set()
    for r in range(rect["startRow"], rect["endRow"] + 1):
        for c in range(rect["startCol"], rect["endCol"] + 1):
            cells.add((r, c))
    return cells


def _build_occupancy(rows: int, cols: int, user_rectangles: list[dict]) -> list[list[bool]]:
    occupancy = [[False for _ in range(cols)] for _ in range(rows)]
    for rect in user_rectangles:
        for r in range(rect["startRow"], rect["endRow"] + 1):
            for c in range(rect["startCol"], rect["endCol"] + 1):
                if 0 <= r < rows and 0 <= c < cols:
                    occupancy[r][c] = True
    return occupancy


def _contains_clue(rect: dict, clue_row: int, clue_col: int) -> bool:
    return (
        rect["startRow"] <= clue_row <= rect["endRow"]
        and rect["startCol"] <= clue_col <= rect["endCol"]
    )


def _rect_area(rect: dict) -> int:
    return (rect["endRow"] - rect["startRow"] + 1) * (rect["endCol"] - rect["startCol"] + 1)


def _bbox_from_cells(cells: set[tuple[int, int]]) -> dict:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return {
        "startRow": min(rows),
        "startCol": min(cols),
        "endRow": max(rows),
        "endCol": max(cols),
    }


def _candidate_overlaps_occupancy(candidate: dict, occupancy: list[list[bool]]) -> bool:
    for r in range(candidate["startRow"], candidate["endRow"] + 1):
        for c in range(candidate["startCol"], candidate["endCol"] + 1):
            if occupancy[r][c]:
                return True
    return False


def get_hint(board: dict, user_rectangles: list[dict]) -> dict:
    rows = board["rows"]
    cols = board["cols"]
    cells = board["cells"]
    user_rectangles = user_rectangles or []

    occupancy = _build_occupancy(rows, cols, user_rectangles)

    solved_clues = set()
    pending_clues = []
    for r in range(rows):
        for c in range(cols):
            v = cells[r][c]
            if v <= 0:
                continue

            solved = False
            for rect in user_rectangles:
                if _contains_clue(rect, r, c) and _rect_area(rect) == v:
                    solved = True
                    break

            if solved:
                solved_clues.add((r, c))
            else:
                pending_clues.append((r, c, v))

    if not pending_clues:
        return {"hintRect": None, "message": "El puzzle está completo o no hay pistas."}

    all_candidates = precompute_candidates(cells, rows)
    clue_candidates = []

    for clue in pending_clues:
        r, c, v = clue
        raw = all_candidates.get((r, c, v), [])
        candidates = [
            {"startRow": r1, "startCol": c1, "endRow": r2, "endCol": c2}
            for r1, c1, r2, c2 in raw
        ]
        valid = [cand for cand in candidates if not _candidate_overlaps_occupancy(cand, occupancy)]

        if not valid:
            return {
                "hintRect": None,
                "clueRow": r,
                "clueCol": c,
                "clueValue": v,
                "message": (
                    f"Inconsistencia detectada: el clue de área {v} en ({r},{c}) "
                    "ya no tiene candidatos válidos."
                ),
            }

        clue_candidates.append((clue, valid))

    clue_candidates.sort(key=lambda item: len(item[1]))
    (clue_row, clue_col, clue_value), valid_candidates = clue_candidates[0]

    if len(valid_candidates) == 1:
        rect = valid_candidates[0]
        return {
            "hintRect": rect,
            "clueRow": clue_row,
            "clueCol": clue_col,
            "clueValue": clue_value,
            "message": (
                f"El rectángulo de área {clue_value} que empieza en "
                f"({clue_row},{clue_col}) solo puede ir aquí."
            ),
            "forced": True,
        }

    common_cells = _rect_cells(valid_candidates[0])
    for rect in valid_candidates[1:]:
        common_cells &= _rect_cells(rect)
        if not common_cells:
            break

    if common_cells:
        return {
            "hintRect": _bbox_from_cells(common_cells),
            "clueRow": clue_row,
            "clueCol": clue_col,
            "clueValue": clue_value,
            "message": (
                f"Estas celdas definitivamente pertenecen al rectángulo de área "
                f"{clue_value}."
            ),
            "forced": False,
        }

    suggested = min(valid_candidates, key=_rect_area)
    return {
        "hintRect": suggested,
        "clueRow": clue_row,
        "clueCol": clue_col,
        "clueValue": clue_value,
        "message": f"Prueba colocar el rectángulo de área {clue_value} aquí.",
        "forced": False,
    }
