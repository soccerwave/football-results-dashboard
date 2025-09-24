# src/data_io.py
from __future__ import annotations
import os
import pandas as pd

REQUIRED_COLS = [
    "date", "home_team", "away_team", "home_score", "away_score"
]

def load_results() -> pd.DataFrame:
    """
    Load results.csv from ./data/results.csv (preferred) or ./results.csv (fallback).
    Parse dates, derive 'year', and ensure required columns exist.
    """
    preferred_path = os.path.join("data", "results.csv")
    fallback_path = "results.csv"

    csv_path = preferred_path if os.path.exists(preferred_path) else fallback_path
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            "results.csv not found. Place it in ./data/results.csv (recommended) "
            "or in project root as ./results.csv."
        )

    df = pd.read_csv(csv_path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["year"] = df["date"].dt.year.astype(int)

    df["home_team"] = df["home_team"].astype(str).str.strip()
    df["away_team"] = df["away_team"].astype(str).str.strip()

    df = df.sort_values("date").reset_index(drop=True)
    return df
