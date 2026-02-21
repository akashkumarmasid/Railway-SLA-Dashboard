import sqlite3
import csv
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DB_PATH = os.path.join(BASE_DIR, "data", "railway_sla.db")


def load_csv_into_table(conn, table_name, csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return
    cols = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(cols))
    conn.executemany(
        f"INSERT OR REPLACE INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})",
        [tuple(r[c] for c in cols) for r in rows],
    )
    conn.commit()
    print(f"  Loaded {len(rows)} rows into {table_name}")


def create_schema(conn):
    schema_path = os.path.join(SQL_DIR, "schema.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())


def run_kpi_queries(conn):
    queries_path = os.path.join(SQL_DIR, "kpi_queries.sql")
    with open(queries_path) as f:
        sql_text = f.read()

    queries = [q.strip() for q in sql_text.split(";") if q.strip()]

    for query in queries:
        lines = query.strip().split("\n")
        title = lines[0] if lines[0].startswith("--") else "Query"
        title = title.lstrip("- ").strip()

        sql = "\n".join(l for l in lines if not l.strip().startswith("--"))
        if not sql.strip():
            continue

        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

        cursor = conn.execute(sql)
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        widths = [len(c) for c in col_names]
        for row in rows[:20]:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))

        header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(col_names))
        print(header)
        print("-+-".join("-" * w for w in widths))

        for row in rows[:20]:
            print(" | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))

        if len(rows) > 20:
            print(f"  ... ({len(rows)} total rows, showing first 20)")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    print("Creating schema...")
    create_schema(conn)

    print("Loading CSVs...")
    load_csv_into_table(conn, "trains", os.path.join(RAW_DIR, "trains.csv"))
    load_csv_into_table(conn, "trips", os.path.join(RAW_DIR, "trips.csv"))
    load_csv_into_table(conn, "complaints", os.path.join(RAW_DIR, "complaints.csv"))

    print("\nRunning KPI queries...")
    run_kpi_queries(conn)

    conn.close()
    print(f"\nSQLite DB saved to {DB_PATH}")


if __name__ == "__main__":
    main()
