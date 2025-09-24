# tests/test_metrics.py
# Basic sanity tests for rolling metrics and Elo-lite.

from __future__ import annotations
import pandas as pd
from src.data_io import load_results
from src.metrics import (
    team_perspective, filter_team_opponent_years, kpis,
    rolling_form, rolling_goal_diff, rolling_win_pct,
    compute_elo, team_elo_trend
)

def test_rolling_metrics_and_kpis():
    df = load_results()
    # Pick a team that exists in first row (ensures non-empty subset)
    t = str(df.iloc[0]["home_team"])
    df_t = team_perspective(df, t)
    assert set(["date","year","is_home","opponent","gf","ga","result"]).issubset(df_t.columns)

    # KPIs should be non-negative and consistent
    k = kpis(df_t)
    assert k["games"] >= 0
    assert k["w"] >= 0 and k["d"] >= 0 and k["l"] >= 0
    assert k["games"] == k["w"] + k["d"] + k["l"]

    # Rolling form in [0,1]
    rf = rolling_form(df_t, window=5)
    if not rf.empty:
        assert (rf["rolling_form"] >= 0.0).all()
        assert (rf["rolling_form"] <= 1.0).all()

    # Rolling GD finite
    rgd = rolling_goal_diff(df_t, window=5)
    if not rgd.empty:
        assert rgd["rolling_gd"].isna().sum() == 0

    # Rolling Win% in [0,100]
    rwp = rolling_win_pct(df_t, window=10)
    if not rwp.empty:
        assert (rwp["rolling_win_pct"] >= 0.0).all()
        assert (rwp["rolling_win_pct"] <= 100.0).all()

def test_elo_lite_outputs():
    df = load_results()
    ratings_history, final_ratings = compute_elo(df, base_rating=1500.0, k_factor=20.0, home_advantage=50.0)
    # final ratings must exist for at least 2 teams
    assert isinstance(final_ratings, pd.DataFrame)
    assert len(final_ratings) >= 2
    assert "team" in final_ratings.columns and "rating" in final_ratings.columns

    # pick a team and ensure trend is non-empty if present in history
    team = str(final_ratings.iloc[0]["team"])
    trend = team_elo_trend(ratings_history, team)
    assert isinstance(trend, pd.DataFrame)
    if not trend.empty:
        assert "rating" in trend.columns
