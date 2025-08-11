#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

MASTER = Path('phivolcs_earthquakes_master.csv')

if not MASTER.exists():
    print('Master CSV not found:', MASTER)
    raise SystemExit(1)

# Read
# Allow mixed formats; pandas handles strings like '11 August 2025 - 12:07 PM'
df = pd.read_csv(MASTER)
# Find date column
date_col = None
for c in df.columns:
    if str(c).lower().startswith('date'):
        date_col = c
        break
if date_col is None:
    print('No date-like column found. Columns:', df.columns.tolist())
    raise SystemExit(1)

# Parse datetimes
dt = pd.to_datetime(df[date_col], errors='coerce', infer_datetime_format=True)
# Drop rows that failed to parse
parsed = df.loc[dt.notna()].copy()
parsed['__dt'] = dt[dt.notna()]

# Filter to 2025
parsed_2025 = parsed[parsed['__dt'].dt.year == 2025].copy()
if parsed_2025.empty:
    print('No 2025 rows found in master; nothing to write.')
    raise SystemExit(0)

# Ensure deterministic ordering by time ascending
parsed_2025 = parsed_2025.sort_values('__dt')

# Columns to write: keep first six that match scraper output
wanted_cols = [
    'Date-Time', 'Latitude', 'Longitude', 'Depth', 'Magnitude', 'Location'
]
cols_present = [c for c in wanted_cols if c in parsed_2025.columns]

# Group by month and write
written = []
for (year, month), g in parsed_2025.groupby([parsed_2025['__dt'].dt.year, parsed_2025['__dt'].dt.month]):
    out_name = f'phivolcs_earthquakes_{year}_{month:02d}.csv'
    out = Path(out_name)
    g_to_write = g[cols_present]
    g_to_write.to_csv(out, index=False)
    written.append(out_name)

print('Wrote monthly files:', ', '.join(written))
