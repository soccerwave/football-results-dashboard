from __future__ import annotations

I18N = {
    "en": {
        # Global
        "app_title": "Sports Results Support Kit",
        "phase_caption": "Phase 1: Dashboard • Phase 2: Data Quality • Phase 3: SQLite • Phase 4: Analytics • Phase 5: Report • Phase 6: Bilingual UI",
        "language_label": "Language",
        "tab_dashboard": "Dashboard",
        "tab_qa": "Data Quality",
        "tab_sql": "SQL",
        "tab_analytics": "Analytics",

        # Sidebar
        "filters": "Filters",
        "team": "Team",
        "opponent_optional": "Opponent (optional)",
        "year": "Year (one or more)",
        "reset_filters": "Reset Filters",

        # KPIs / dashboard
        "kpis": "KPIs",
        "games": "Games",
        "w_d_l": "W-D-L",
        "gf_ga": "GF-GA",
        "win_pct": "Win %",
        "goal_diff": "Goal Diff",
        "points_per_game": "Points/Game",

        "filtered_results": "Filtered Results",
        "download_csv": "Download CSV",
        "head_to_head": "Head-to-Head",
        "pick_opponent_info": "Pick an Opponent to see Head-to-Head summary and form chart.",
        "selected_teams": "Selected teams: **{team}** vs **{opponent}**",

        # QA tab
        "qa_intro": "Run automated data quality checks before analysis.",
        "qa_checks_run": "Checks run: required columns, null counts, invalid dates, inconsistent duplicate team names.",
        "use_demo": "Use demo issues (synthetic) without modifying your data",
        "qa_summary": "Summary",
        "qa_no_issues": "No issues found. Your dataset looks good.",
        "qa_issues_table_title": "Issues Table",
        "qa_download_btn": "Download Issues CSV",
        "qa_help_title": "What to fix first?",
        "qa_help_text": "- Fix all **Errors** first (missing required fields, invalid dates).\n- Then address **Warnings** (nulls in non-critical fields, inconsistent names).\n- Use the issues CSV to prioritize fixes.",
        "col_issue_type": "issue_type",
        "col_severity": "severity",
        "col_column": "column",
        "col_row": "row_index",
        "col_detail": "detail",

        # SQL tab
        "sql_title": "SQLite: ETL & Queries",
        "db_path_exists": "DB path: {path} — Exists: {exists}",
        "init_schema": "Initialize DB schema",
        "load_csv_db": "Load CSV into DB",
        "etl_loaded": "Loaded. Teams={teams}, Matches={matches}",
        "etl_error": "ETL error: {error}",
        "run_predef_query": "Run a predefined query",
        "query": "Query",
        "team_a": "Team A",
        "team_b": "Team B",
        "limit": "Limit",
        "db_not_found": "Database not found. Click 'Initialize DB schema' and then 'Load CSV into DB'.",
        "query_error": "Query error: {error}",

        # Analytics tab
        "an_title": "Analytics: Rolling Trends and Elo-lite",
        "team_analytics": "Team (analytics)",
        "rolling_form_title": "Rolling Form (points over last 5 games)",
        "no_data_form": "No data to compute rolling form.",
        "rolling_gd_title": "Rolling Goal Difference (last 5 games)",
        "no_data_gd": "No data to compute rolling goal difference.",
        "rolling_winpct_title": "Rolling Win% (last 10 games)",
        "no_data_winpct": "No data to compute rolling win percentage.",
        "elo_title": "Elo-lite Trend",
        "elo_assumptions": "Assumptions: base=1500, K=20, home advantage=50 Elo pts.",
        "no_data_elo": "No Elo data to display.",

        # Reports
        "export_h2h": "Export H2H Report (HTML)",
        "export_saved": "Report saved: {path}",
        "download_now": "Download now",
        "export_team": "Export Team Report (HTML)",
    },

    "es": {
        # Global
        "app_title": "Kit de Soporte de Resultados Deportivos",
        "phase_caption": "Fase 1: Panel • Fase 2: Calidad de Datos • Fase 3: SQLite • Fase 4: Analítica • Fase 5: Informe • Fase 6: Interfaz Bilingüe",
        "language_label": "Idioma",
        "tab_dashboard": "Panel",
        "tab_qa": "Calidad de Datos",
        "tab_sql": "SQL",
        "tab_analytics": "Analítica",

        # Sidebar
        "filters": "Filtros",
        "team": "Equipo",
        "opponent_optional": "Oponente (opcional)",
        "year": "Año (uno o más)",
        "reset_filters": "Restablecer filtros",

        # KPIs / dashboard
        "kpis": "KPIs",
        "games": "Partidos",
        "w_d_l": "G-E-P",
        "gf_ga": "GF-GC",
        "win_pct": "% Victorias",
        "goal_diff": "Dif. Goles",
        "points_per_game": "Puntos/Partido",

        "filtered_results": "Resultados Filtrados",
        "download_csv": "Descargar CSV",
        "head_to_head": "Cara a Cara",
        "pick_opponent_info": "Elige un Oponente para ver el resumen de Cara a Cara y la gráfica de forma.",
        "selected_teams": "Equipos seleccionados: **{team}** vs **{opponent}**",

        # QA tab
        "qa_intro": "Ejecuta verificaciones automáticas de calidad de datos antes del análisis.",
        "qa_checks_run": "Verificaciones: columnas requeridas, nulos, fechas inválidas, nombres de equipo duplicados/inconsistentes.",
        "use_demo": "Usar problemas de demostración (sintéticos) sin modificar tus datos",
        "qa_summary": "Resumen",
        "qa_no_issues": "No se encontraron problemas. Tu conjunto de datos parece correcto.",
        "qa_issues_table_title": "Tabla de Problemas",
        "qa_download_btn": "Descargar CSV de Problemas",
        "qa_help_title": "¿Qué corregir primero?",
        "qa_help_text": "- Corrige primero todos los **Errores** (campos requeridos faltantes, fechas inválidas).\n- Luego atiende las **Advertencias** (nulos no críticos, nombres inconsistentes).\n- Usa el CSV de problemas para priorizar correcciones.",
        "col_issue_type": "tipo_problema",
        "col_severity": "severidad",
        "col_column": "columna",
        "col_row": "fila",
        "col_detail": "detalle",

        # SQL tab
        "sql_title": "SQLite: ETL y Consultas",
        "db_path_exists": "Ruta BD: {path} — Existe: {exists}",
        "init_schema": "Inicializar esquema de BD",
        "load_csv_db": "Cargar CSV en BD",
        "etl_loaded": "Cargado. Equipos={teams}, Partidos={matches}",
        "etl_error": "Error ETL: {error}",
        "run_predef_query": "Ejecutar una consulta predefinida",
        "query": "Consulta",
        "team_a": "Equipo A",
        "team_b": "Equipo B",
        "limit": "Límite",
        "db_not_found": "Base de datos no encontrada. Pulsa 'Inicializar esquema de BD' y luego 'Cargar CSV en BD'.",
        "query_error": "Error de consulta: {error}",

        # Analytics tab
        "an_title": "Analítica: Tendencias y Elo-lite",
        "team_analytics": "Equipo (analítica)",
        "rolling_form_title": "Forma móvil (puntos en últimos 5 partidos)",
        "no_data_form": "No hay datos para calcular la forma móvil.",
        "rolling_gd_title": "Diferencia de goles móvil (últimos 5 partidos)",
        "no_data_gd": "No hay datos para calcular la diferencia de goles.",
        "rolling_winpct_title": "% Victorias móvil (últimos 10 partidos)",
        "no_data_winpct": "No hay datos para calcular el % de victorias.",
        "elo_title": "Tendencia Elo-lite",
        "elo_assumptions": "Suposiciones: base=1500, K=20, ventaja local=50 puntos Elo.",
        "no_data_elo": "No hay datos Elo para mostrar.",

        # Reports
        "export_h2h": "Exportar Informe H2H (HTML)",
        "export_saved": "Informe guardado: {path}",
        "download_now": "Descargar ahora",
        "export_team": "Exportar Informe de Equipo (HTML)",
    },
}

def tr(lang: str, key: str, **kwargs) -> str:
    """
    Simple translator helper. Falls back to English if key or language missing.
    """
    lang_dict = I18N.get(lang, I18N["en"])
    text = lang_dict.get(key, I18N["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
