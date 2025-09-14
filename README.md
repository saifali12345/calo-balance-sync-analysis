# calo-balance-sync-analysis
Data engineering solution to analyze balance sync logs, detect overdrafts/anomalies, and generate reports for reconciliation.

# Balance Sync Logs Analysis

Run `parse_logs.py` against the provided `logs.txt`. The script will generate CSV reports under `report_output/`.
A Dockerfile is provided to run the parser in a container. Build and run with:

```
docker build -t balance-logs-analysis .
docker run --rm -v $(pwd)/data:/data balance-logs-analysis
```

The provided deliverables in this package include:
- parse_logs.py : main parsing script
- requirements.txt : python deps
- Dockerfile : to run without extra config
- balance_sync_report/ : sample output generated from the uploaded logs


## Streamlit Dashboard

A Streamlit dashboard (`app_streamlit.py`) is included to make it easy for non-technical users to explore transactions and anomalies.

Run locally:
```
pip install -r requirements.txt
streamlit run app_streamlit.py
```

Run with Docker (recommended):
```
docker build -t balance-logs-dashboard .
docker run --rm -p 8501:8501 -v $(pwd)/data:/data balance-logs-dashboard
```
Make sure `data/logs.txt` was processed and `balance_sync_report/` is present in the project (or mount a directory containing the report files). The app reads the generated CSV/XLSX from `balance_sync_report/`.

