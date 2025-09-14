
#!/usr/bin/env python3
import re, os, pandas as pd, sys, gzip
from datetime import timedelta

def parse_log_file(log_path):
    ts_re = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)')
    entries = []
    with open(log_path, 'r', errors='replace') as f:
        current = []
        current_ts = None
        for line in f:
            m = ts_re.match(line)
            if m:
                if current:
                    entries.append(("".join(current_ts), "".join(current)))
                current_ts = m.groups()
                current = [line[len(m.group(0)):]]
            else:
                current.append(line)
        if current:
            entries.append(("".join(current_ts) if current_ts else "", "".join(current)))
    records = []
    for ts, text in entries:
        if "Start syncing the balance" in text:
            m = re.search(r"transaction:\s*{([^}]*)}", text, re.S)
            block = m.group(1) if m else text
            def r(key):
                mm = re.search(rf"{key}:\s*'([^']*)'", block)
                if mm:
                    return mm.group(1)
                mm2 = re.search(rf"{key}:\s*([0-9\.\-eE]+)", block)
                if mm2:
                    return mm2.group(1)
                mm3 = re.search(rf"{key}:\s*(true|false)", block, re.I)
                if mm3:
                    return mm3.group(1).lower()=='true'
                return None
            rec = {}
            rec['log_ts'] = ts
            rec['transaction_id'] = r('id')
            rec['type'] = r('type')
            rec['source'] = r('source')
            rec['action'] = r('action')
            rec['user_id'] = r('userId')
            rec['paymentBalance'] = r('paymentBalance')
            rec['updatePaymentBalance'] = r('updatePaymentBalance')
            rec['currency'] = r('currency')
            rec['amount'] = r('amount')
            rec['vat'] = r('vat')
            rec['oldBalance'] = r('oldBalance')
            records.append(rec)
    df = pd.DataFrame(records)
    for col in ['paymentBalance','amount','vat','oldBalance']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['log_ts'] = pd.to_datetime(df['log_ts'], errors='coerce')
    df = df.sort_values(['user_id','log_ts'])
    def compute_expected(row):
        if pd.notna(row['oldBalance']) and pd.notna(row['amount']) and pd.notna(row['type']):
            if str(row['type']).upper()=='DEBIT':
                return row['oldBalance'] - row['amount']
            elif str(row['type']).upper()=='CREDIT':
                return row['oldBalance'] + row['amount']
        return None
    df['expected_paymentBalance'] = df.apply(compute_expected, axis=1)
    df['balance_mismatch'] = (df['expected_paymentBalance'] - df['paymentBalance']).abs() > 0.01
    df['overdraft'] = df['paymentBalance'] < 0
    dup_tx = df['transaction_id'][df['transaction_id'].duplicated(keep=False)].unique().tolist()
    # simple outputs
    outdir = os.path.join(os.path.dirname(log_path), 'report_output')
    os.makedirs(outdir, exist_ok=True)
    df['log_ts'] = df['log_ts'].dt.tz_convert(None)
    df.to_csv(os.path.join(outdir,'transactions.csv'), index=False)
    summary = df.groupby('user_id').agg(transactions=('transaction_id','count'),
                                        total_debit=('amount', lambda x: x[df.loc[x.index,'type'].str.upper()=='DEBIT'].sum()),
                                        total_credit=('amount', lambda x: x[df.loc[x.index,'type'].str.upper()=='CREDIT'].sum()),
                                        min_balance=('paymentBalance','min'),
                                        max_balance=('paymentBalance','max'),
                                        last_balance=('paymentBalance', 'last')).reset_index()
    summary.to_csv(os.path.join(outdir,'user_summary.csv'), index=False)
    df[df['balance_mismatch']==True].to_csv(os.path.join(outdir,'mismatches.csv'), index=False)
    df[df['overdraft']==True].to_csv(os.path.join(outdir,'overdrafts.csv'), index=False)
    return outdir

if __name__=='__main__':
    if len(sys.argv)<2:
        print("Usage: parse_logs.py <path-to-log-file>")
        sys.exit(1)
    out = parse_log_file(sys.argv[1])
    print("Reports saved to", out)
