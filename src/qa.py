from __future__ import annotations
import re
import unicodedata
import pandas as pd
from typing import List, Dict, Any

REQUIRED_COLS = ["date", "home_team", "away_team", "home_score", "away_score"]

def run_all_checks(df: pd.DataFrame) -> pd.DataFrame:
    issues = []
    issues += check_required_columns(df)
    issues += check_nulls(df)
    issues += check_invalid_dates(df)
    issues += check_unclean_team_names(df, ["home_team", "away_team"])

    if not issues:
        return pd.DataFrame(columns=["issue_type", "severity", "column", "row_index", "detail"])
    return pd.DataFrame(issues)

def check_required_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues = []
    for col in REQUIRED_COLS:
        if col not in df.columns:
            issues.append(_issue("MISSING_COLUMN", "ERROR", col, None, f"Required column '{col}' is missing"))
    return issues

def check_nulls(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            severity = "ERROR" if col in REQUIRED_COLS else "WARN"
            issues.append(_issue("NULL_VALUES", severity, col, None, f"Null count: {null_count}"))
    return issues

def check_invalid_dates(df: pd.DataFrame, min_year: int = 1870, max_year: int = 2100) -> List[Dict[str, Any]]:
    issues = []
    if "date" not in df.columns:
        issues.append(_issue("MISSING_COLUMN", "ERROR", "date", None, "No 'date' column"))
        return issues

    # Null dates
    date_null = df["date"].isna()
    for idx in df[date_null].index.tolist():
        issues.append(_issue("INVALID_DATE", "ERROR", "date", int(idx), "NaT (invalid date)"))

    # Plausibility range
    if "year" in df.columns:
        years = df.loc[~df["date"].isna(), "year"]
    else:
        years = df.loc[~df["date"].isna(), "date"].dt.year

    bad_idx = df.index[(years < min_year) | (years > max_year)].tolist()
    for idx in bad_idx:
        y = int(years.loc[idx])
        issues.append(_issue("OUT_OF_RANGE_DATE", "ERROR", "date", int(idx), f"Year {y} outside [{min_year}, {max_year}]"))
    return issues

def check_unclean_team_names(df: pd.DataFrame, team_cols: List[str]) -> List[Dict[str, Any]]:
    issues = []
    # Build canonical map
    canon_to_originals = {}
    for col in team_cols:
        for val in df[col].astype(str).tolist():
            c = canonicalize_name(val)
            canon_to_originals.setdefault(c, set()).add(val)

    for canon, originals in canon_to_originals.items():
        if len(originals) > 1:
            detail = f"Canonical='{canon}' has variants: {sorted(originals)}"
            issues.append(_issue("UNCLEAN_TEAM_NAME", "WARN", ",".join(team_cols), None, detail))
    return issues

def canonicalize_name(s: str) -> str:
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace(".", "")  # remove dots like "U.S.A." -> "usa"
    return s

def _issue(issue_type: str, severity: str, column: str | None, row_index: int | None, detail: str) -> Dict[str, Any]:
    return {
        "issue_type": issue_type,
        "severity": severity,
        "column": column,
        "row_index": row_index,
        "detail": detail,
    }
