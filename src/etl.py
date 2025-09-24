from __future__ import annotations
from pathlib import Path
from src.sql_io import init_db, load_csv_to_db, DEFAULT_DB_PATH

def main():
    print("[ETL] Initializing database schema...")
    init_db(DEFAULT_DB_PATH)
    print(f"[ETL] DB ready at: {DEFAULT_DB_PATH}")

    print("[ETL] Loading CSV into DB (teams, matches, h2h_summary)...")
    teams_count, matches_count = load_csv_to_db(DEFAULT_DB_PATH, Path("data/results.csv"))
    print(f"[ETL] Done. Teams: {teams_count}, Matches: {matches_count}")

if __name__ == "__main__":
    main()
