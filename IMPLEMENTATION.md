
# Implementation Details

- Language: Python 3.11 with pandas for data processing.
- Approach: The logs are semi-structured. The parser looks for "Start syncing the balance" blocks and extracts key fields using regular expressions.
- Reports: transactions.csv, user_summary.csv, mismatches.csv, overdrafts.csv, and an Excel file and HTML summary are included in balance_sync_report/.
- Dockerization: simple Dockerfile is included that runs parse_logs.py with `/data/logs.txt` mounted into the container.
- Future improvements:
  * Use a proper log parser or JSON-structured logs to avoid fragile regex parsing.
  * Persist results to a database and build an interactive dashboard (Streamlit or Dash).
  * Add unit tests and CI to build the Docker image and run checks.
