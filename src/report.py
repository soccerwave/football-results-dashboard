# src/report.py
# Build a one-page HTML report with KPIs, tables, and a minimal sparkline SVG.

from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import html
import pandas as pd

def _kpi_cards_html(k: Dict[str, float | int]) -> str:
    cards = [
        ("Games", str(k["games"])),
        ("W-D-L", f'{k["w"]}-{k["d"]}-{k["l"]}'),
        ("GF-GA", f'{k["gf"]}-{k["ga"]}'),
        ("Win %", f'{k["win_pct"]}%'),
        ("Goal Diff", str(k["gf"] - k["ga"])),
        ("Points/Game", f'{round((k["w"]*1 + k["d"]*0.5)/k["games"], 2) if k["games"] else 0.0}')
    ]
    items = []
    for title, val in cards:
        items.append(f"""
        <div class="card">
          <div class="card-title">{html.escape(title)}</div>
          <div class="card-value">{html.escape(str(val))}</div>
        </div>
        """)
    return '<div class="kpi-grid">' + "\n".join(items) + "</div>"

def _df_to_table_html(df: pd.DataFrame, title: str) -> str:
    if df is None or df.empty:
        return f"<h3>{html.escape(title)}</h3><div class='muted'>No data</div>"
    df_show = df.copy()
    max_rows = 50
    truncated = False
    if len(df_show) > max_rows:
        df_show = df_show.head(max_rows)
        truncated = True
    thead = "<tr>" + "".join([f"<th>{html.escape(str(c))}</th>" for c in df_show.columns]) + "</tr>"
    rows = []
    for _, r in df_show.iterrows():
        tds = "".join([f"<td>{html.escape(str(v))}</td>" for v in r.tolist()])
        rows.append(f"<tr>{tds}</tr>")
    extra = "<div class='muted'>Showing first 50 rows…</div>" if truncated else ""
    return f"""
    <h3>{html.escape(title)}</h3>
    <div class="table-wrap">
      <table>
        <thead>{thead}</thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
    {extra}
    """

def _sparkline_svg(values: List[float], width: int = 600, height: int = 100, padding: int = 10) -> str:
    if not values:
        return "<div class='muted'>No chart</div>"
    n = len(values)
    if n == 1:
        values = values * 2
        n = 2
    vmin, vmax = min(values), max(values)
    if vmax - vmin < 1e-9:
        vmax = vmin + 1.0
    def scale_x(i: int) -> float:
        if n == 1:
            return padding
        return padding + (i / (n - 1)) * (width - 2 * padding)
    def scale_y(v: float) -> float:
        return padding + (1 - (v - vmin) / (vmax - vmin)) * (height - 2 * padding)
    pts = " ".join([f"{scale_x(i)},{scale_y(v)}" for i, v in enumerate(values)])
    baseline_min = scale_y(vmin)
    baseline_max = scale_y(vmax)
    return f"""
    <svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="sparkline">
      <polyline fill="none" stroke="#3b82f6" stroke-width="2" points="{pts}" />
      <line x1="{padding}" y1="{baseline_min}" x2="{width-padding}" y2="{baseline_min}" stroke="#d1d5db" stroke-dasharray="4,4" />
      <line x1="{padding}" y1="{baseline_max}" x2="{width-padding}" y2="{baseline_max}" stroke="#d1d5db" stroke-dasharray="4,4" />
    </svg>
    """

def _html_shell(body: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #111827; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  h2 {{ font-size: 20px; margin: 18px 0 8px; color: #374151; }}
  h3 {{ font-size: 16px; margin: 16px 0 8px; color: #4b5563; }}
  .muted {{ color: #6b7280; font-size: 13px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 12px 0 4px; }}
  .card {{ background: #f9fafb; padding: 12px; border: 1px solid #e5e7eb; border-radius: 10px; }}
  .card-title {{ font-size: 12px; color: #6b7280; }}
  .card-value {{ font-size: 20px; font-weight: 700; }}
  .table-wrap {{ overflow-x: auto; border: 1px solid #e5e7eb; border-radius: 10px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th, td {{ border-bottom: 1px solid #e5e7eb; text-align: left; padding: 8px; }}
  th {{ background: #f3f4f6; font-weight: 600; }}
  .sparkline {{ display: block; margin-top: 6px; }}
  .row {{ display: grid; grid-template-columns: 1fr; gap: 14px; }}
  @media(min-width: 920px) {{ .row {{ grid-template-columns: 1fr 1fr; }} }}
  .footer {{ margin-top: 24px; font-size: 12px; color: #6b7280; }}
</style>
</head>
<body>
{body}
<div class="footer">Generated on {html.escape(datetime.now().strftime("%Y-%m-%d %H:%M"))}</div>
</body>
</html>"""

def build_h2h_report_html(team: str, opponent: str, kpi: Dict[str, float | int],
                          h2h_table: pd.DataFrame, recent_matches: pd.DataFrame,
                          rolling_form_values: List[float]) -> str:
    title = f"H2H Report — {team} vs {opponent}"
    kpi_html = _kpi_cards_html(kpi)
    h2h_html = _df_to_table_html(h2h_table, f"Head-to-Head Summary: {team} vs {opponent}")
    recent_html = _df_to_table_html(recent_matches, "Recent Matches (Filtered)")
    spark = _sparkline_svg(rolling_form_values, width=720, height=120, padding=12)
    body = f"""
<h1>{html.escape(title)}</h1>
<h2>KPIs</h2>
{kpi_html}
<h2>Rolling Form (sparkline)</h2>
<div class="muted">Rolling average of points (W=1, D=0.5, L=0). Window=5.</div>
{spark}
<div class="row">
  <div>{h2h_html}</div>
  <div>{recent_html}</div>
</div>
"""
    return _html_shell(body, title)

def build_team_report_html(team: str, kpi: Dict[str, float | int],
                           form_table: pd.DataFrame, gd_table: pd.DataFrame,
                           rolling_form_values: List[float], rolling_gd_values: List[float]) -> str:
    title = f"Team Report — {team}"
    kpi_html = _kpi_cards_html(kpi)
    form_html = _df_to_table_html(form_table, "Rolling Form Table")
    gd_html = _df_to_table_html(gd_table, "Rolling Goal Diff Table")
    spark_form = _sparkline_svg(rolling_form_values, width=720, height=120, padding=12)
    spark_gd = _sparkline_svg(rolling_gd_values, width=720, height=120, padding=12)
    body = f"""
<h1>{html.escape(title)}</h1>
<h2>KPIs</h2>
{kpi_html}
<h2>Rolling Form (sparkline)</h2>
<div class="muted">Rolling average of points (W=1, D=0.5, L=0). Window=5.</div>
{spark_form}
<h2>Rolling Goal Difference (sparkline)</h2>
{spark_gd}
<div class="row">
  <div>{form_html}</div>
  <div>{gd_html}</div>
</div>
"""
    return _html_shell(body, title)

def save_report_html(html_text: str, out_dir: Path | str = Path("outputs"),
                     file_name: Optional[str] = None) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not file_name:
        file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    out_path = out_dir / file_name
    out_path.write_text(html_text, encoding="utf-8")
    return out_path
