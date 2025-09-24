from __future__ import annotations
import sys, pathlib

# --- ensure project root is in sys.path ---
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------

from pathlib import Path
import pandas as pd
from src.sql_io import init_db, load_csv_to_db, run_query

def test_sql_etl_and_queries():
    # 1) check CSV exists and not empty
    csv_path = Path("data/results.csv")
    assert csv_path.exists(), "data/results.csv must exist"
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV must not be empty"

    # 2) pick two teams from first row
    team_a = str(df.iloc[0]["home_team"])
    team_b = str(df.iloc[0]["away_team"])
    assert team_a and team_b

    # 3) init fresh DB
    db_path = Path("data/test_app.db")
    if db_path.exists():
        db_path.unlink()  # remove old test DB
    init_db(db_path)

    # 4) load CSV into DB
    teams_count, matches_count = load_csv_to_db(db_path, csv_path)
    assert teams_count > 0
    assert matches_count > 0

    # 5) run h2h_summary querry
    h2h = run_query("h2h_summary", {"team_a": team_a, "team_b": team_b}, db_path)
    assert isinstance(h2h, pd.DataFrame)

    # 6) run recent_form_10 query
    rf = run_query("recent_form_10", {"team_name": team_a, "limit": 10}, db_path)
    assert isinstance(rf, pd.DataFrame)
    assert len(rf) <= 10
