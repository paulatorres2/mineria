#!/usr/bin/env python
"""Seed the MotherDuck star schema (run once from the project root).

Usage:
    python scripts/init_motherduck.py           # skips if tables already exist
    python scripts/init_motherduck.py --force   # drops and rebuilds all tables
"""
import os
import sys

token = os.environ.get("MOTHERDUCK_TOKEN", "")
if not token:
    print("\nError: MOTHERDUCK_TOKEN is not set.\n\n")
    sys.exit(1)

sys.path.insert(0, ".")

from app.nivel_2.db import _fetch_data, _build_schema, _md_conn, _tables_exist

conn = _md_conn()

if _tables_exist(conn):
    if "--force" not in sys.argv:
        print("Tables already exist in MotherDuck. Run with --force to rebuild.")
        conn.close()
        sys.exit(0)
    for tbl in ("fact_homicidios", "dim_tiempo", "dim_ubicacion", "dim_arma", "dim_modalidad"):
        conn.execute(f"DROP TABLE IF EXISTS {tbl}")
    print("Existing tables dropped.")

print("Fetching data from API...")
df = _fetch_data()
print(f"Fetched {len(df)} rows. Building star schema in MotherDuck...")
_build_schema(conn, df)
print("Done — star schema is live in MotherDuck.")
conn.close()
