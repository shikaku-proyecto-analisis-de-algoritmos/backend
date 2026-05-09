from boards import get_board
import json


def test_board_easy():
                                     
    board = get_board(difficulty="easy")
    assert board["rows"] == 5
    assert board["cols"] == 5
    assert len(board["cells"]) == 5
    assert all(len(row) == 5 for row in board["cells"])
    print("✓ Easy board generation works")


def test_board_medium():
                                       
    board = get_board(difficulty="medium")
    assert board["rows"] == 8
    assert board["cols"] == 8
    assert len(board["cells"]) == 8
    assert all(len(row) == 8 for row in board["cells"])
    print("✓ Medium board generation works")


def test_board_hard():
                                     
    board = get_board(difficulty="hard")
    assert board["rows"] == 10
    assert board["cols"] == 10
    assert len(board["cells"]) == 10
    assert all(len(row) == 10 for row in board["cells"])
    print("✓ Hard board generation works")


def test_board_with_seed():
                                         
    board1 = get_board(difficulty="easy", seed=42)
    board2 = get_board(difficulty="easy", seed=42)
    
    assert board1["cells"] == board2["cells"]
    print("✓ Reproducibility with seed works")


def test_board_cells_valid():
                                                  
    board = get_board(difficulty="easy", seed=99)
    
                                                  
    for row in board["cells"]:
        for cell in row:
            assert cell >= 0
            assert isinstance(cell, int)
    
                                   
    clue_count = sum(1 for row in board["cells"] for cell in row if cell > 0)
    assert clue_count > 0
    print("✓ Board cells are valid")


def test_serializable_to_json():
                                                    
    board = get_board(difficulty="medium", seed=777)
    try:
        json_str = json.dumps(board)
        board_restored = json.loads(json_str)
        assert board_restored == board
        print("✓ Board is JSON serializable")
    except Exception as e:
        raise AssertionError(f"Board not JSON serializable: {e}")


def test_board_difficulty_variations():
                                                                         
    boards_by_difficulty = {
        "easy": get_board("easy", seed=111),
        "medium": get_board("medium", seed=111),
        "hard": get_board("hard", seed=111),
    }
    
    sizes = [boards_by_difficulty[d]["rows"] for d in ["easy", "medium", "hard"]]
    assert sizes == [5, 8, 10], f"Expected [5, 8, 10], got {sizes}"
    print("✓ Different difficulties produce expected sizes")


if __name__ == "__main__":
    try:
        test_board_easy()
        test_board_medium()
        test_board_hard()
        test_board_with_seed()
        test_board_cells_valid()
        test_serializable_to_json()
        test_board_difficulty_variations()
        print("\n✓ All integration tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
