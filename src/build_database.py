"""Author: Anveshaa Kesharwaani

Create the SQLite database from the CSV files, using sql/schema.sql, sql/views.sql and sql/advanced_views.sql.
Run from the project root folder.
"""
import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "placement.db"
SQL_DIR = Path("sql")
TABLES = [("students", "students.csv"), ("companies", "companies.csv"), ("offers", "offers.csv")]


def build(db_path=DB_PATH, data_dir=DATA_DIR, sql_dir=SQL_DIR):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript((Path(sql_dir) / "schema.sql").read_text())
        for table, filename in TABLES:
            df = pd.read_csv(Path(data_dir) / filename)
            df.to_sql(table, conn, if_exists="append", index=False)
        conn.executescript((Path(sql_dir) / "views.sql").read_text())
        conn.executescript((Path(sql_dir) / "advanced_views.sql").read_text())
        conn.commit()
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table, _ in TABLES
        }
    finally:
        conn.close()
    return counts


if __name__ == "__main__":
    print("Database built:", build())
