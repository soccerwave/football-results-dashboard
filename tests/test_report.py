from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.data_io import load_results
from src.metrics import team_perspective, kpis, rolling_form, rolling_goal_diff
from src.report import build_h2h_report_html, build_team_report_html, save_report_html

def test_build_and_save_h2h_report(tmp_path: Path):
    df = load_results()
    # pick two teams from first row (not guaranteed to have H2H in small slice,
    tA = str(df.iloc[0]["home_team"])
    tB = str(df.iloc[0]["away_team"])
    dfA = team_perspective(df, tA)
    # filter vs B (best effort)
    dfA_vsB = dfA[dfA["opponent"] == tB].copy()
    k = kpis(dfA_vsB if not dfA_vsB.empty else dfA)
    # minimal tables
    h2h_summary = pd.DataFrame({"result": ["W","D","L"], "count": [0,0,0]})
    if not dfA_vsB.empty:
        h2h_summary = dfA_vsB.groupby("result").size().reindex(["W","D","L"], fill_value=0).reset_index(name="count")
    recent = (dfA_vsB if not dfA_vsB.empty else dfA).head(5)
    rf = rolling_form(dfA_vsB if not dfA_vsB.empty else dfA, window=5)
    values = rf["rolling_form"].tolist() if not rf.empty else []

    html_text = build_h2h_report_html(tA, tB, k, h2h_summary, recent, values)
    out = save_report_html(html_text, tmp_path, "h2h.html")
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert tA in txt and "H2H Report" in txt

def test_build_and_save_team_report(tmp_path: Path):
    df = load_results()
    team = str(df.iloc[0]["home_team"])
    dfT = team_perspective(df, team)
    k = kpis(dfT)
    rf = rolling_form(dfT, window=5)
    rgd = rolling_goal_diff(dfT, window=5)
    rf_tbl = rf.tail(10) if not rf.empty else pd.DataFrame()
    rgd_tbl = rgd.tail(10) if not rgd.empty else pd.DataFrame()
    form_vals = rf["rolling_form"].tolist() if not rf.empty else []
    gd_vals = rgd["rolling_gd"].tolist() if not rgd.empty else []

    html_text = build_team_report_html(team, k, rf_tbl, rgd_tbl, form_vals, gd_vals)
    out = save_report_html(html_text, tmp_path, "team.html")
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert team in txt and "Team Report" in txt
