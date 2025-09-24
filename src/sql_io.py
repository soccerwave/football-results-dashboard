from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
from typing import Dict, Tuple

DEFAULT_DB_PATH = Path("data/app.db")
SCHEMA_PATH = Path("sql/schema.sql")
QUERIES_PATH = Path("sql/queries.sql")

def _connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path | str = DEFAULT_DB_PATH, schema_path: Path | str = SCHEMA_PATH) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn, open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
        conn.executescript(sql)

def load_csv_to_db(db_path: Path | str = DEFAULT_DB_PATH, csv_path: Path | str = Path("data/results.csv")) -> Tuple[int, int]:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # basic sanity
    required = ["date", "home_team", "away_team", "home_score", "away_score"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required CSV columns: {missing}")

    # dates & year
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    if "year" not in df.columns:
        df["year"] = df["date"].dt.year.astype(int)
    else:
        df["year"] = df["year"].astype(int)

    # trim names
    df["home_team"] = df["home_team"].astype(str).str.strip()
    df["away_team"] = df["away_team"].astype(str).str.strip()

    with _connect(db_path) as conn:
        cur = conn.cursor()

        # Insert teams
        teams = pd.unique(pd.concat([df["home_team"], df["away_team"]], ignore_index=True)).tolist()
        for name in teams:
            cur.execute("INSERT OR IGNORE INTO teams(name) VALUES (?)", (name,))
        conn.commit()

        # Map team name -> id
        team_id = {row["name"]: row["id"] for row in cur.execute("SELECT id, name FROM teams")}

        # Insert matches
        rows = []
        for _, r in df.iterrows():
            rows.append((
                r["date"].date().isoformat(),
                int(r["year"]),
                int(team_id[r["home_team"]]),
                int(team_id[r["away_team"]]),
                int(r["home_score"]),
                int(r["away_score"]),
            ))
        cur.executemany(
            """INSERT INTO matches(date, year, home_team_id, away_team_id, home_score, away_score)
               VALUES (?, ?, ?, ?, ?, ?)""",
            rows
        )
        conn.commit()

        # Build h2h_summary
        cur.execute("DELETE FROM h2h_summary;")
        conn.commit()

        cur.executescript("""
        WITH team_matches AS (
          SELECT date, home_team_id AS team_id, away_team_id AS opponent_id,
                 home_score AS gf, away_score AS ga
          FROM matches
          UNION ALL
          SELECT date, away_team_id, home_team_id,
                 away_score, home_score
          FROM matches
        ),
        team_results AS (
          SELECT team_id, opponent_id, date, gf, ga,
                 CASE WHEN gf > ga THEN 1
                      WHEN gf = ga THEN 0
                      ELSE -1 END AS outcome
          FROM team_matches
        )
        INSERT INTO h2h_summary(team_id, opponent_id, games, w, d, l, gf, ga, last_meeting_date)
        SELECT team_id,
               opponent_id,
               COUNT(*) AS games,
               SUM(CASE WHEN outcome = 1 THEN 1 ELSE 0 END) AS w,
               SUM(CASE WHEN outcome = 0 THEN 1 ELSE 0 END) AS d,
               SUM(CASE WHEN outcome = -1 THEN 1 ELSE 0 END) AS l,
               SUM(gf) AS gf,
               SUM(ga) AS ga,
               MAX(date) AS last_meeting_date
        FROM team_results
        GROUP BY team_id, opponent_id;
        """)
        conn.commit()

        # return counts
        teams_count = cur.execute("SELECT COUNT(*) FROM teams;").fetchone()[0]
        matches_count = cur.execute("SELECT COUNT(*) FROM matches;").fetchone()[0]
        return teams_count, matches_count

def _load_query_templates(path: Path | str = QUERIES_PATH) -> Dict[str, str]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    blocks = text.split("-- name:")
    queries: Dict[str, str] = {}
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        key = lines[0].strip()
        sql = "\n".join(lines[1:]).strip()
        queries[key] = sql
    return queries

_QUERIES_CACHE: Dict[str, str] | None = None

def get_query_names() -> list[str]:
    global _QUERIES_CACHE
    if _QUERIES_CACHE is None:
        _QUERIES_CACHE = _load_query_templates()
    return sorted(_QUERIES_CACHE.keys())

def get_query_sql(name: str) -> str:
    global _QUERIES_CACHE
    if _QUERIES_CACHE is None:
        _QUERIES_CACHE = _load_query_templates()
    if name not in _QUERIES_CACHE:
        raise KeyError(f"Unknown query name: {name}")
    return _QUERIES_CACHE[name]

def run_query(name: str, params: dict, db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    sql = get_query_sql(name)
    with _connect(db_path) as conn:
        df = pd.read_sql_query(sql, conn, params=params)
    return df
