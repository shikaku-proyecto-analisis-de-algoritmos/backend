from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from statistics import median
from sqlalchemy import text
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Board, SessionStartRequest, SolveRequest, ValidateRequest, HintRequest
from boards import get_board
from auth import ensure_profile, get_current_player, get_db, get_optional_player, router as auth_router
from solver import solve_backtracking, solve_backtracking_cp
from hints import get_hint
from checker import check_solution
from database import engine, Base  
import models as db_models 
from db_model import GameRecord, GameSession, HintEvent, LoginEvent, Player, PlayerProfile, SolveEvent

app = FastAPI()

def _ensure_player_columns():
    with engine.begin() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(players)")).fetchall()
        }
        if "email" not in existing_columns:
            connection.execute(text("ALTER TABLE players ADD COLUMN email VARCHAR"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_players_email ON players(email)"))
        if "google_id" not in existing_columns:
            connection.execute(text("ALTER TABLE players ADD COLUMN google_id VARCHAR"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_players_google_id ON players(google_id)"))
        if "auth_provider" not in existing_columns:
            connection.execute(text("ALTER TABLE players ADD COLUMN auth_provider VARCHAR DEFAULT 'local'"))
            connection.execute(text("UPDATE players SET auth_provider = 'local' WHERE auth_provider IS NULL"))
        if "avatar_url" not in existing_columns:
            connection.execute(text("ALTER TABLE players ADD COLUMN avatar_url VARCHAR"))

@app.on_event("startup") 

def startup():
    Base.metadata.create_all(bind=engine)
    _ensure_player_columns()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    players = (
        db.query(Player)
        .order_by(Player.score.desc(), Player.username.asc())
        .limit(10)
        .all()
    )
    return [
        {
            "rank": index + 1,
            "username": player.username,
            "score": player.score or 0
        }
        for index, player in enumerate(players)
    ]

@app.get("/board")
def fetch_board(difficulty: str = "easy", seed: int = None):
    board = get_board(difficulty=difficulty, seed=seed)
    return {"board": board}

@app.get("/game/level/{id}")
def fetch_game_level(id: int):
    board = get_board(difficulty="medium", seed=id)
    return board

@app.post("/solve")
def solve(
    request: SolveRequest,
    player: Player = Depends(get_optional_player),
    db: Session = Depends(get_db)
):
    board_dict = request.board.dict()
    if request.solver_type == "bt":
        solution = solve_backtracking(board_dict)
    elif request.solver_type == "cp":
        solution = solve_backtracking_cp(board_dict)
    else:
        raise HTTPException(status_code=400, detail="solver_type must be 'bt' or 'cp'")

    if player:
        db.add(SolveEvent(
            player_id=player.id,
            difficulty=request.difficulty or "unknown",
            level=request.level or 1,
            solver_type=request.solver_type,
            elapsed_before_secs=request.elapsed_secs or 0
        ))
        db.commit()

    return {"solution": solution}


@app.post("/validate")
def validate(
    request: ValidateRequest,
    player: Player = Depends(get_optional_player),
    db: Session = Depends(get_db)
):
    result = check_solution(request.board, request.rectangles)

    if player and result.get("valid"):
        completed_at = datetime.utcnow()
        time_secs = request.time_secs or 0
        difficulty = (request.difficulty or "easy").lower()
        solve_used = bool(request.solve_used)
        hints_used = request.hints_used or 0

        db.add(GameSession(
            player_id=player.id,
            difficulty=difficulty,
            level=request.level or 1,
            completed_at=completed_at,
            completed=True,
            manual=not solve_used,
            time_secs=time_secs,
            hints_used=hints_used,
            solve_used=solve_used
        ))

        db.add(GameRecord(
            player_id=player.id,
            difficulty=difficulty,
            time_secs=time_secs,
            completed=completed_at
        ))

        # ==================================================
        # CÁLCULO DE PUNTAJE
        # ==================================================

        # Puntos base por dificultad
        difficulty_points = {
            "easy": 100,
            "medium": 250,
            "hard": 500
        }

        score_earned = difficulty_points.get(difficulty, 100)

        # --------------------------------------------------
        # BONUS POR RESOLUCIÓN MANUAL
        # --------------------------------------------------

        if not solve_used:
            score_earned = int(score_earned * 1.5)

        # --------------------------------------------------
        # BONUS POR VELOCIDAD
        # --------------------------------------------------

        # (tiempo objetivo en segundos, bonus máximo)
        time_targets = {
            "easy": (60, 150),
            "medium": (180, 300),
            "hard": (300, 500)
        }

        target_time, max_bonus = time_targets.get(
            difficulty,
            (60, 150)
        )

        if time_secs > 0:
            speed_bonus = int(
                max_bonus *
                (target_time / (target_time + time_secs))
            )

            score_earned += speed_bonus

        # --------------------------------------------------
        # PENALIZACIÓN POR PISTAS
        # --------------------------------------------------

        score_earned -= hints_used * 20

        # --------------------------------------------------
        # PUNTAJE MÍNIMO GARANTIZADO
        # --------------------------------------------------

        score_earned = max(score_earned, 50)

        player.score = (player.score or 0) + score_earned

        db.commit()

        result["score_earned"] = score_earned
        result["total_score"] = player.score

    return result


@app.post("/hint")
def hint(
    request: HintRequest,
    player: Player = Depends(get_optional_player),
    db: Session = Depends(get_db)
):
    
    result = get_hint(
        board=request.board.dict(),
        user_rectangles=[r.dict() for r in request.user_rectangles]
    )

    if player:
        db.add(HintEvent(
            player_id=player.id,
            difficulty=request.difficulty or "unknown",
            level=request.level or 1,
            elapsed_secs=request.elapsed_secs or 0
        ))
        db.commit()

    return result

@app.post("/analytics/session/start")
def start_session(
    request: SessionStartRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    db.add(GameSession(
        player_id=player.id,
        difficulty=request.difficulty,
        level=request.level,
        completed=False,
        manual=True,
        time_secs=0
    ))
    db.commit()
    return {"message": "session recorded"}

def _format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"

def _streaks(login_events):
    login_days = sorted({event.logged_at.date() for event in login_events}, reverse=True)
    if not login_days:
        return {"current": 0, "max": 0}

    today = date.today()
    current = 0
    cursor = today
    days = set(login_days)
    if today not in days and (today - timedelta(days=1)) in days:
        cursor = today - timedelta(days=1)
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)

    max_streak = 1
    running = 1
    asc = sorted(days)
    for idx in range(1, len(asc)):
        if asc[idx] == asc[idx - 1] + timedelta(days=1):
            running += 1
            max_streak = max(max_streak, running)
        else:
            running = 1

    return {"current": current, "max": max_streak}

@app.get("/profile")
def profile(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    profile_row = ensure_profile(player, db)
    logins = db.query(LoginEvent).filter(LoginEvent.player_id == player.id).order_by(LoginEvent.logged_at.desc()).all()
    completed = db.query(GameSession).filter(
        GameSession.player_id == player.id,
        GameSession.completed == True
    ).all()
    total_time = sum(session.time_secs or 0 for session in completed)

    return {
        "id": player.id,
        "username": player.username,
        "email": player.email,
        "authProvider": player.auth_provider or "local",
        "avatarUrl": player.avatar_url,
        "registeredAt": profile_row.created_at,
        "score": player.score or 0,
        "levelsCompleted": len(completed),
        "totalPlayedSecs": total_time,
        "totalPlayedLabel": _format_duration(total_time),
        "lastAccess": logins[0].logged_at if logins else None
    }

@app.get("/profile/stats")
def profile_stats(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    completed = db.query(GameSession).filter(
        GameSession.player_id == player.id,
        GameSession.completed == True
    ).all()
    solves = db.query(SolveEvent).filter(SolveEvent.player_id == player.id).all()
    hints = db.query(HintEvent).filter(HintEvent.player_id == player.id).all()
    logins = db.query(LoginEvent).filter(LoginEvent.player_id == player.id).all()

    levels_by_difficulty = Counter(session.difficulty for session in completed)
    algorithms = Counter(event.solver_type for event in solves)
    manual_sessions = [session for session in completed if session.manual]

    manual_times = {}
    for difficulty in ["easy", "medium", "hard"]:
        values = [session.time_secs or 0 for session in manual_sessions if session.difficulty == difficulty]
        manual_times[difficulty] = {
            "average": round(sum(values) / len(values), 2) if values else 0,
            "best": min(values) if values else 0,
            "worst": max(values) if values else 0
        }

    solve_waits = [event.elapsed_before_secs or 0 for event in solves]
    solve_wait_stats = {
        "average": round(sum(solve_waits) / len(solve_waits), 2) if solve_waits else 0,
        "median": median(solve_waits) if solve_waits else 0,
        "min": min(solve_waits) if solve_waits else 0,
        "max": max(solve_waits) if solve_waits else 0
    }

    hints_by_day = Counter(event.created_at.date().isoformat() for event in hints)
    logins_by_day = Counter(event.logged_at.date().isoformat() for event in logins)
    total_time = sum(session.time_secs or 0 for session in completed)
    hint_frequency = {
        "perGame": round(len(hints) / len(completed), 2) if completed else 0,
        "secondsPerHint": round(total_time / len(hints), 2) if hints and total_time else 0
    }
    streaks = _streaks(logins)

    return {
        "kpis": {
            "levelsCompleted": len(completed),
            "totalPlayedSecs": total_time,
            "totalPlayedLabel": _format_duration(total_time),
            "currentStreak": streaks["current"],
            "maxStreak": streaks["max"],
            "hintsUsed": len(hints),
            "loginCount": len(logins),
            "solveCount": len(solves)
        },
        "levelsByDifficulty": {
            "easy": levels_by_difficulty.get("easy", 0),
            "medium": levels_by_difficulty.get("medium", 0),
            "hard": levels_by_difficulty.get("hard", 0)
        },
        "algorithmUsage": {
            "bt": algorithms.get("bt", 0),
            "cp": algorithms.get("cp", 0)
        },
        "manualTimesByDifficulty": manual_times,
        "solveWaitStats": solve_wait_stats,
        "hintFrequency": hint_frequency,
        "hintsByDay": dict(sorted(hints_by_day.items())),
        "activityByDay": dict(sorted(logins_by_day.items()))
    }

@app.get("/profile/history")
def profile_history(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    completed = db.query(GameSession).filter(
        GameSession.player_id == player.id,
        GameSession.completed == True
    ).order_by(GameSession.completed_at.desc()).limit(25).all()

    return {
        "games": [
            {
                "difficulty": session.difficulty,
                "level": session.level,
                "timeSecs": session.time_secs,
                "manual": session.manual,
                "hintsUsed": session.hints_used,
                "solveUsed": session.solve_used,
                "completedAt": session.completed_at
            }
            for session in completed
        ]
    }
