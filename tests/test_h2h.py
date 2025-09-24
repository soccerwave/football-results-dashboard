from __future__ import annotations
from src.data_io import load_results
from src.metrics import team_perspective, kpis, h2h_summary_table

def test_h2h_summary_consistency():
    df = load_results()
    team = str(df.iloc[0]["home_team"])
    df_t = team_perspective(df, team)
    k = kpis(df_t)
    tbl = h2h_summary_table(df_t)

    assert "Games" in tbl.columns
    # Games should equal W+D+L in KPIs
    assert k["games"] == k["w"] + k["d"] + k["l"]
    # And table must reflect Games == KPIs games
    assert int(tbl.iloc[0]["Games"]) == k["games"]
