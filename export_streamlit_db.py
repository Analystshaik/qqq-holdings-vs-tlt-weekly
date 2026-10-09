import sqlite3
from pathlib import Path

SOURCE_DB = r"C:\Keystone\ibkr_production_data_engine_v2\data\ibkr_market_data.sqlite"
TARGET_DB = Path("data") / "streamlit_data.sqlite"

TABLES = [
    "qqq_holdings_tlt_relationship_week",
    "qqq_holdings_tlt_relationship_snapshot",
]

def copy_table(src, dst, table):
    row = src.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table,)
    ).fetchone()

    if not row or not row[0]:
        print(f"SKIP: {table} not found")
        return

    dst.execute(f'DROP TABLE IF EXISTS "{table}"')
    dst.execute(row[0])

    rows = src.execute(f'SELECT * FROM "{table}"').fetchall()
    if rows:
        placeholders = ",".join("?" for _ in rows[0])
        dst.executemany(f'INSERT INTO "{table}" VALUES ({placeholders})', rows)

    print(f"COPIED: {table} ({len(rows):,} rows)")

def main():
    target = TARGET_DB.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        target.unlink()

    src = sqlite3.connect(SOURCE_DB)
    dst = sqlite3.connect(str(target))

    try:
        for table in TABLES:
            copy_table(src, dst, table)
        dst.commit()
        dst.execute("VACUUM")
        dst.commit()
    finally:
        src.close()
        dst.close()

    print(f"Created: {target}")
    print(f"Size: {target.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
