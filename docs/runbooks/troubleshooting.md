**# Troubleshooting (Client-Friendly)**



**## Streamlit won't start**

**- Try `streamlit run app/streamlit\_app.py --server.port 8502`.**

**- Ensure your virtualenv is activated and deps installed: `pip install -r requirements.txt`.**



**## CSV not found**

**- Place your `results.csv` under `data/results.csv`.**



**## Invalid imports in tests**

**- Make sure `tests/conftest.py` exists to add the project root to `sys.path`.**



**## SQLite errors (no such table)**

**- In the \*\*SQL\*\* tab, click \*\*Initialize DB schema\*\* then \*\*Load CSV into DB\*\*, or run `python -m src.etl`.**



**## Empty charts**

**- Select a team with more matches or remove restrictive filters.**



