#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Step 1: Generate raw data ==="
python3 scripts/generate_data.py

echo ""
echo "=== Step 2: ETL ==="
python3 scripts/etl.py

echo ""
echo "=== Step 3: Validate KPIs ==="
python3 scripts/validate_kpis.py

echo ""
echo "=== Step 4: SQLite demo ==="
python3 scripts/run_sql_demo.py

echo ""
echo "=== Pipeline complete ==="
