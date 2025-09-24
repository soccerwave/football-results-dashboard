# app/streamlit_app.py
from __future__ import annotations
import sys, pathlib

# --- ensure project root is in sys.path ---
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from src.data_io import load_results
from src.metrics import (
    team_perspective,
    filter_team_opponent_years,
    kpis,
    rolling_form,
    rolling_goal_diff,
    rolling_win_pct,
    h2h_summary_table,
    compute_elo,
    team_elo_trend,
)
from src.qa import run_all_checks
from src.i18n import I18N, tr
from src.sql_io import init_db, load_csv_to_db, run_query, get_query_names, DEFAULT_DB_PATH
from src.report import build_h2h_report_html, build_team_report_html, save_report_html

st.set_page_config(page_title="Sports Results Support Kit", layout="wide")

@st.cache_data
def _load():
    return load_results()

@st.cache_data
def _elo_cache(df: pd.DataFrame):
    return compute_elo(df)

def _unique_sorted_teams(df: pd.DataFrame) -> list[str]:
    teams = pd.unique(pd.concat([df["home_team"], df["away_team"]], ignore_index=True))
    return sorted(teams.tolist())

def reset_filters():
    for key in ("team", "opponent", "years"):
        if key in st.session_state:
            del st.session_state[key]

# ---- LANGUAGE (global selector in sidebar) ----
with st.sidebar:
    lang = st.selectbox("Language / Idioma", ["en", "es"], index=0, key="lang")

# ---- HEADER ----
st.title(tr(lang, "app_title"))
st.caption(tr(lang, "phase_caption"))

# ---- LOAD DATA ----
df = _load()

# ---- TABS ----
tab_main, tab_qa, tab_sql, tab_an = st.tabs([
    tr(lang, "tab_dashboard"),
    tr(lang, "tab_qa"),
    tr(lang, "tab_sql"),
    tr(lang, "tab_analytics"),
])

with tab_main:
    # Sidebar filters (under global language selector)
    with st.sidebar:
        st.subheader(tr(lang, "filters"))
        team = st.selectbox(tr(lang, "team"), _unique_sorted_teams(df), key="team")
        opp_list = [o for o in _unique_sorted_teams(df) if o != team]
        opponent = st.selectbox(tr(lang, "opponent_optional"), [""] + opp_list, key="opponent")
        opponent = opponent if opponent != "" else None
        all_years = sorted(df["year"].unique().tolist())
        years = st.multiselect(tr(lang, "year"), all_years, key="years")
        if st.button(tr(lang, "reset_filters")):
            reset_filters()
            st.rerun()

    df_team = team_perspective(df, team)
    df_filt = filter_team_opponent_years(df_team, opponent, years)

    st.markdown("### " + tr(lang, "kpis"))
    k = kpis(df_filt)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(tr(lang, "games"), f"{k['games']}")
    col2.metric(tr(lang, "w_d_l"), f"{k['w']}-{k['d']}-{k['l']}")
    col3.metric(tr(lang, "gf_ga"), f"{k['gf']}-{k['ga']}")
    col4.metric(tr(lang, "win_pct"), f"{k['win_pct']}%")
    gd = k['gf'] - k['ga']
    col5.metric(tr(lang, "goal_diff"), f"{gd}")
    ppg = round((k['w']*1 + k['d']*0.5) / k['games'], 2) if k['games'] else 0.0
    col6.metric(tr(lang, "points_per_game"), f"{ppg}")

    st.divider()

    st.markdown("### " + tr(lang, "filtered_results"))
    show_cols = ["date","is_home","opponent","gf","ga","result",
                 "home_team","away_team","home_score","away_score","year"]
    st.dataframe(df_filt[show_cols], use_container_width=True)
    csv_bytes = df_filt[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(tr(lang, "download_csv"), data=csv_bytes,
                       file_name="filtered_results.csv", mime="text/csv")

    st.divider()

    st.markdown("### " + tr(lang, "head_to_head"))
    if opponent:
        st.write(tr(lang, "selected_teams", team=team, opponent=opponent))
        h2h_sum = (
            df_filt.groupby("result")
            .size()
            .reindex(["W","D","L"], fill_value=0)
            .reset_index(name="count")
        )
        st.dataframe(h2h_sum, use_container_width=True)

        form_df = rolling_form(df_filt, window=5)

        # Export H2H report
        if st.button(tr(lang, "export_h2h")):
            k_cur = kpis(df_filt)
            recent_cols = ["date","is_home","opponent","gf","ga","result"]
            recent_tbl = df_filt[recent_cols].sort_values("date", ascending=False).head(20)
            form_vals = form_df["rolling_form"].tolist() if not form_df.empty else []
            html_text = build_h2h_report_html(team, opponent, k_cur, h2h_sum, recent_tbl, form_vals)
            out_path = save_report_html(
                html_text, out_dir="outputs",
                file_name=f"report_h2h_{team.replace(' ','_')}_vs_{opponent.replace(' ','_')}.html"
            )
            st.success(tr(lang, "export_saved", path=str(out_path)))
            st.download_button(tr(lang, "download_now"), data=html_text.encode("utf-8"),
                               file_name=out_path.name, mime="text/html")

        if not form_df.empty:
            line = (
                alt.Chart(form_df)
                .mark_line(point=True)
                .encode(
                    x="date:T",
                    y=alt.Y("rolling_form:Q", title="Rolling Form (0–1)"),
                    tooltip=["date:T","rolling_form:Q"]
                )
                .properties(height=300)
            )
            st.altair_chart(line, use_container_width=True)
    else:
        st.info(tr(lang, "pick_opponent_info"))

with tab_qa:
    st.subheader(tr(lang, "tab_qa"))
    st.write(tr(lang, "qa_intro"))
    st.caption(tr(lang, "qa_checks_run"))

    use_demo = st.checkbox(tr(lang, "use_demo"), value=False)

    df_qc = df.copy()
    if use_demo and not df_qc.empty:
        df_qc.loc[df_qc.index[0], "date"] = pd.Timestamp("2200-01-01")
        if "year" in df_qc.columns:
            df_qc.loc[df_qc.index[0], "year"] = 2200
        df_qc.loc[df_qc.index[1], "away_team"] = None
        df_qc.loc[df_qc.index[2], "home_team"] = str(df_qc.loc[df_qc.index[2], "home_team"]) + "  "

    from src.qa import run_all_checks
    issues_df = run_all_checks(df_qc)

    st.markdown("### " + tr(lang, "qa_summary"))
    if issues_df.empty:
        st.success(tr(lang, "qa_no_issues"))
    else:
        errors = int((issues_df["severity"] == "ERROR").sum())
        warns = int((issues_df["severity"] == "WARN").sum())
        st.warning(f"Errors: {errors} | Warnings: {warns}" if lang == "en"
                   else f"Errores: {errors} | Advertencias: {warns}")

        rename_map = {
            "issue_type": tr(lang, "col_issue_type"),
            "severity": tr(lang, "col_severity"),
            "column": tr(lang, "col_column"),
            "row_index": tr(lang, "col_row"),
            "detail": tr(lang, "col_detail"),
        }
        st.markdown("### " + tr(lang, "qa_issues_table_title"))
        st.dataframe(issues_df.rename(columns=rename_map), use_container_width=True)

        csv_bytes = issues_df.to_csv(index=False).encode("utf-8")
        st.download_button(tr(lang, "qa_download_btn"), data=csv_bytes,
                           file_name="data_quality_issues.csv", mime="text/csv")

    st.markdown("#### " + tr(lang, "qa_help_title"))
    st.write(tr(lang, "qa_help_text"))

with tab_sql:
    st.subheader(tr(lang, "sql_title"))
    db_path = DEFAULT_DB_PATH
    exists = Path(db_path).exists()
    st.caption(tr(lang, "db_path_exists", path=str(db_path), exists=str(exists)))

    colA, colB = st.columns([1,2])
    with colA:
        if st.button(tr(lang, "init_schema")):
            init_db(db_path)
            st.success("Schema initialized.")

        if st.button(tr(lang, "load_csv_db")):
            try:
                teams_count, matches_count = load_csv_to_db(db_path, Path("data/results.csv"))
                st.success(tr(lang, "etl_loaded", teams=teams_count, matches=matches_count))
            except Exception as e:
                st.error(tr(lang, "etl_error", error=str(e)))

    with colB:
        st.markdown("**" + tr(lang, "run_predef_query") + "**")
        query_names = get_query_names()
        qname = st.selectbox(tr(lang, "query"), query_names, index=0, key="sql_qname")

        teams = _unique_sorted_teams(df)
        params = {}
        if qname in ("last_5_matches_h2h", "h2h_summary"):
            team_a = st.selectbox(tr(lang, "team_a"), teams, key="q_team_a")
            team_b = st.selectbox(tr(lang, "team_b"), [t for t in teams if t != team_a], key="q_team_b")
            params["team_a"] = team_a
            params["team_b"] = team_b
            if qname == "last_5_matches_h2h":
                limit = st.number_input(tr(lang, "limit"), min_value=1, max_value=100, value=5, step=1, key="q_limit_h2h")
                params["limit"] = int(limit)
        elif qname in ("recent_form_10", "team_top_opponents", "team_recent_goal_diff"):
            team_name = st.selectbox(tr(lang, "team"), teams, key="q_team_single")
            params["team_name"] = team_name
            default_limit = 10 if qname != "team_recent_goal_diff" else 20
            limit = st.number_input(tr(lang, "limit"), min_value=1, max_value=200, value=default_limit, step=1, key="q_limit_single")
            params["limit"] = int(limit)

        if st.button("Run Query" if lang == "en" else "Ejecutar consulta"):
            if not Path(db_path).exists():
                st.error(tr(lang, "db_not_found"))
            else:
                try:
                    out = run_query(qname, params, db_path=db_path)
                    st.dataframe(out, use_container_width=True)
                    if qname == "team_recent_goal_diff" and not out.empty:
                        chart = (
                            alt.Chart(out)
                            .mark_line(point=True)
                            .encode(x="date:T", y="gd:Q", tooltip=["date:T", "gd:Q"])
                            .properties(height=300)
                        )
                        st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.error(tr(lang, "query_error", error=str(e)))

with tab_an:
    st.subheader(tr(lang, "an_title"))
    teams = _unique_sorted_teams(df)
    team_an = st.selectbox(tr(lang, "team_analytics"), teams, key="an_team")

    df_t = team_perspective(df, team_an)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**" + tr(lang, "rolling_form_title") + "**")
        rf = rolling_form(df_t, window=5)
        if not rf.empty:
            ch = (
                alt.Chart(rf).mark_line(point=True)
                .encode(x="date:T", y=alt.Y("rolling_form:Q", title="Rolling Form (0–1)"),
                        tooltip=["date:T","rolling_form:Q"])
                .properties(height=280)
            )
            st.altair_chart(ch, use_container_width=True)
        else:
            st.info(tr(lang, "no_data_form"))

    with c2:
        st.markdown("**" + tr(lang, "rolling_gd_title") + "**")
        rgd = rolling_goal_diff(df_t, window=5)
        if not rgd.empty:
            ch2 = (
                alt.Chart(rgd).mark_line(point=True)
                .encode(x="date:T", y=alt.Y("rolling_gd:Q", title="Rolling GD"),
                        tooltip=["date:T","rolling_gd:Q"])
                .properties(height=280)
            )
            st.altair_chart(ch2, use_container_width=True)
        else:
            st.info(tr(lang, "no_data_gd"))

    st.divider()

    st.markdown("**" + tr(lang, "rolling_winpct_title") + "**")
    rwp = rolling_win_pct(df_t, window=10)
    if not rwp.empty:
        ch3 = (
            alt.Chart(rwp).mark_line(point=True)
            .encode(x="date:T", y=alt.Y("rolling_win_pct:Q", title="Rolling Win %"),
                    tooltip=["date:T","rolling_win_pct:Q"])
            .properties(height=300)
        )
        st.altair_chart(ch3, use_container_width=True)
    else:
        st.info(tr(lang, "no_data_winpct"))

    st.divider()

    st.markdown("**" + tr(lang, "elo_title") + "**")
    with st.spinner("Computing Elo ratings..." if lang == "en" else "Calculando calificaciones Elo..."):
        ratings_history, final_ratings = _elo_cache(df)
    trend = team_elo_trend(ratings_history, team_an)
    if not trend.empty:
        elo_chart = (
            alt.Chart(trend).mark_line(point=True)
            .encode(x="date:T", y=alt.Y("rating:Q", title="Elo-lite Rating"),
                    tooltip=["date:T","rating:Q"])
            .properties(height=320)
        )
        st.altair_chart(elo_chart, use_container_width=True)
        st.caption(tr(lang, "elo_assumptions"))
    else:
        st.info(tr(lang, "no_data_elo"))

    st.divider()
    # Export team report button
    if st.button(tr(lang, "export_team"), key="export_team_report"):
        k_full = kpis(df_t)
        rf_tbl = rf.tail(20) if not rf.empty else pd.DataFrame()
        rgd_tbl = rgd.tail(20) if not rgd.empty else pd.DataFrame()
        form_vals = rf["rolling_form"].tolist() if not rf.empty else []
        gd_vals = rgd["rolling_gd"].tolist() if not rgd.empty else []
        html_text = build_team_report_html(team_an, k_full, rf_tbl, rgd_tbl, form_vals, gd_vals)
        out_path = save_report_html(html_text, out_dir="outputs",
                                    file_name=f"report_team_{team_an.replace(' ','_')}.html")
        st.success(tr(lang, "export_saved", path=str(out_path)))
        st.download_button(tr(lang, "download_now"), data=html_text.encode("utf-8"),
                           file_name=out_path.name, mime="text/html")
