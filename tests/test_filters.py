from __future__ import annotations
from src.data_io import load_results
from src.metrics import team_perspective, filter_team_opponent_years

def test_filter_by_opponent_and_year():
    df = load_results()
    team = str(df.iloc[0]["home_team"])
    df_t = team_perspective(df, team)

    opp = str(df_t.iloc[0]["opponent"])
    year = int(df_t.iloc[0]["year"])
    out = filter_team_opponent_years(df_t, opponent=opp, years=[year])

    assert ((out["opponent"] == opp) & (out["year"] == year)).all() or out.empty
