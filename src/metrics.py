
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def team_perspective(df: pd.DataFrame, team: str) -> pd.DataFrame:
    df = df.copy()
    is_home = df["home_team"] == team
    is_away = df["away_team"] == team
    df_team = df[is_home | is_away].copy()

    df_team["is_home"] = is_home[is_home | is_away]
    df_team["opponent"] = df_team.apply(
        lambda r: r["away_team"] if r["is_home"] else r["home_team"], axis=1
    )
    df_team["gf"] = df_team.apply(
        lambda r: r["home_score"] if r["is_home"] else r["away_score"], axis=1
    )
    df_team["ga"] = df_team.apply(
        lambda r: r["away_score"] if r["is_home"] else r["home_score"], axis=1
    )
    df_team["result"] = df_team.apply(_row_result, axis=1)

    # keep essential columns + originals for reference
    keep = ["date","year","is_home","opponent","gf","ga","result",
            "home_team","away_team","home_score","away_score"]
    df_team = df_team.sort_values("date").reset_index(drop=True)
    return df_team[keep]

def _row_result(r) -> str:
    if r["gf"] > r["ga"]:
        return "W"
    if r["gf"] < r["ga"]:
        return "L"
    return "D"

def filter_team_opponent_years(df_team: pd.DataFrame, opponent: str | None, years: list[int] | None) -> pd.DataFrame:
    out = df_team.copy()
    if opponent:
        out = out[out["opponent"] == opponent]
    if years:
        out = out[out["year"].isin(years)]
    return out

def kpis(df_team_filtered: pd.DataFrame) -> dict:
    n = len(df_team_filtered)
    w = (df_team_filtered["result"] == "W").sum()
    d = (df_team_filtered["result"] == "D").sum()
    l = (df_team_filtered["result"] == "L").sum()
    gf = int(df_team_filtered["gf"].sum()) if n else 0
    ga = int(df_team_filtered["ga"].sum()) if n else 0
    win_pct = round((w / n) * 100, 1) if n else 0.0
    return {"games": n, "w": int(w), "d": int(d), "l": int(l), "gf": gf, "ga": ga, "win_pct": win_pct}


def rolling_form(df_team_filtered: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    form_df = df_team_filtered[["date", "result"]].copy()
    if form_df.empty:
        form_df["points"] = []
        form_df["rolling_form"] = []
        return form_df

    points_map = {"W": 1.0, "D": 0.5, "L": 0.0}
    form_df["points"] = form_df["result"].map(points_map).astype(float)
    form_df["rolling_form"] = form_df["points"].rolling(window=window, min_periods=1).mean()
    return form_df

def rolling_goal_diff(df_team_filtered: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    gd_df = df_team_filtered[["date", "gf", "ga"]].copy()
    if gd_df.empty:
        gd_df["gd"] = []
        gd_df["rolling_gd"] = []
        return gd_df
    gd_df["gd"] = (gd_df["gf"] - gd_df["ga"]).astype(float)
    gd_df["rolling_gd"] = gd_df["gd"].rolling(window=window, min_periods=1).mean()
    return gd_df[["date","gd","rolling_gd"]]

def rolling_win_pct(df_team_filtered: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    w_df = df_team_filtered[["date", "result"]].copy()
    if w_df.empty:
        w_df["win"] = []
        w_df["rolling_win_pct"] = []
        return w_df
    w_df["win"] = (w_df["result"] == "W").astype(int)
    w_df["rolling_win_pct"] = w_df["win"].rolling(window=window, min_periods=1).mean() * 100.0
    return w_df

# H2H summary
def h2h_summary_table(df_team_filtered: pd.DataFrame) -> pd.DataFrame:
    k = kpis(df_team_filtered)
    out = pd.DataFrame([{
        "Games": k["games"], "W": k["w"], "D": k["d"], "L": k["l"], "GF": k["gf"], "GA": k["ga"]
    }])
    return out

# Elo model
def compute_elo(df: pd.DataFrame,
                base_rating: float = 1500.0,
                k_factor: float = 20.0,
                home_advantage: float = 50.0) -> Tuple[pd.DataFrame, pd.DataFrame]:


    df = df.sort_values("date").reset_index(drop=True).copy()
    teams = pd.unique(pd.concat([df["home_team"], df["away_team"]], ignore_index=True)).tolist()

    rating: Dict[str, float] = {t: float(base_rating) for t in teams}
    hist_rows = []

    for _, r in df.iterrows():
        ht = str(r["home_team"]); at = str(r["away_team"])
        hs = int(r["home_score"]); as_ = int(r["away_score"])

        rh = rating[ht]; ra = rating[at]

        e_home = 1.0 / (1.0 + 10.0 ** ((ra - (rh + home_advantage)) / 400.0))
        e_away = 1.0 - e_home

        # Actual scores
        if hs > as_:
            s_home, s_away = 1.0, 0.0
        elif hs < as_:
            s_home, s_away = 0.0, 1.0
        else:
            s_home, s_away = 0.5, 0.5

        # Update ratings
        rh_new = rh + k_factor * (s_home - e_home)
        ra_new = ra + k_factor * (s_away - e_away)
        rating[ht], rating[at] = rh_new, ra_new

        # Record history (post-match ratings)
        hist_rows.append({"date": r["date"], "team": ht, "rating": rh_new})
        hist_rows.append({"date": r["date"], "team": at, "rating": ra_new})

    ratings_history = pd.DataFrame(hist_rows)
    final_ratings = ratings_history.sort_values("date").groupby("team").tail(1)[["team","rating"]].reset_index(drop=True)
    final_ratings = final_ratings.sort_values("rating", ascending=False).reset_index(drop=True)
    return ratings_history, final_ratings

def team_elo_trend(ratings_history: pd.DataFrame, team: str) -> pd.DataFrame:
    if ratings_history.empty:
        return ratings_history.copy()
    out = ratings_history[ratings_history["team"] == team][["date","rating"]].sort_values("date").reset_index(drop=True)
    return out
