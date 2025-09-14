
import streamlit as st
import pandas as pd, os, datetime
st.set_page_config(page_title="Balance Sync Dashboard", layout="wide")

st.title("Balance Sync Logs — Dashboard")

base = os.path.join(os.path.dirname(__file__), "balance_sync_report")
# prefer CSVs in report_output if present
csv_dir = os.path.join(os.path.dirname(__file__), "balance_sync_report")
transactions_csv = None
# try known locations
candidates = [
    os.path.join(csv_dir, "report_output", "transactions.csv"),
    os.path.join(csv_dir, "transactions.csv"),
    os.path.join(csv_dir, "balance_reports.csv"),
]
for c in candidates:
    if os.path.exists(c):
        transactions_csv = c
        break

# Fallback: try reading Excel
excel_path = os.path.join(csv_dir, "balance_reports.xlsx")
if transactions_csv is None and os.path.exists(excel_path):
    try:
        tx = pd.read_excel(excel_path, sheet_name="transactions")
    except Exception as e:
        tx = pd.DataFrame()
else:
    tx = pd.read_csv(transactions_csv) if transactions_csv and os.path.exists(transactions_csv) else pd.DataFrame()

st.sidebar.header("Filters")
if tx.empty:
    st.warning("No transactions data found. Make sure reports were generated and balance_sync_report/ exists.")
    st.stop()

# parse timestamps if present
if 'log_ts' in tx.columns:
    try:
        tx['log_ts'] = pd.to_datetime(tx['log_ts'])
    except:
        pass

min_date = tx['log_ts'].min() if 'log_ts' in tx.columns else None
max_date = tx['log_ts'].max() if 'log_ts' in tx.columns else None
start = st.sidebar.date_input("Start date", value=min_date.date() if min_date is not None else None)
end = st.sidebar.date_input("End date", value=max_date.date() if max_date is not None else None)

df = tx.copy()
if 'log_ts' in df.columns and start and end:
    start_dt = datetime.datetime.combine(start, datetime.time.min)
    end_dt = datetime.datetime.combine(end, datetime.time.max)
    df = df[(df['log_ts'] >= start_dt) & (df['log_ts'] <= end_dt)]

user_filter = st.sidebar.text_input("Filter by user_id (contains)")
if user_filter:
    df = df[df['user_id'].str.contains(user_filter, na=False)]

st.metric("Total transactions shown", len(df))
col1, col2 = st.columns(2)
with col1:
    st.write("Top users by transactions")
    top_users = df.groupby('user_id').size().reset_index(name='count').sort_values('count', ascending=False).head(20)
    st.dataframe(top_users)

with col2:
    st.write("Anomalies (balance_mismatch / overdraft)")
    if 'balance_mismatch' in df.columns or 'overdraft' in df.columns:
        anomalies = df[(df.get('balance_mismatch', False)) | (df.get('overdraft', False))]
        st.dataframe(anomalies[['log_ts','transaction_id','user_id','type','amount','oldBalance','paymentBalance','expected_paymentBalance','balance_mismatch','overdraft']].head(200))
    else:
        st.write("No anomaly flags available in data.")

st.write("Transactions (first 500 rows)")
st.dataframe(df.head(500))

st.download_button("Download filtered transactions as CSV", df.to_csv(index=False).encode('utf-8'), file_name="transactions_filtered.csv")
