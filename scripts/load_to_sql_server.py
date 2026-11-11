"""Load the generated CSV files into the SQL Server portfolio database.

Run the database and table creation scripts first. By default, this loader uses
Windows authentication and ODBC Driver 18 for SQL Server.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import pyodbc


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LOAD_ORDER = [
    ("Customers", "customers.csv"),
    ("Vehicles", "vehicles.csv"),
    ("Technicians", "technicians.csv"),
    ("ServiceTypes", "service_types.csv"),
    ("Parts", "parts.csv"),
    ("TechnicianShifts", "technician_shifts.csv"),
    ("Appointments", "appointments.csv"),
    ("RepairOrders", "repair_orders.csv"),
    ("RepairOrderServices", "repair_order_services.csv"),
    ("TechnicianTimeLogs", "technician_time_logs.csv"),
    ("PartUsage", "part_usage.csv"),
    ("PartsShortages", "parts_shortages.csv"),
]

DELETE_ORDER = [table for table, _ in reversed(LOAD_ORDER)]


def connection_string(args: argparse.Namespace) -> str:
    base = (
        f"DRIVER={{{args.driver}}};SERVER={args.server};DATABASE={args.database};"
        "TrustServerCertificate=yes;"
    )
    if args.sql_auth:
        user = os.environ.get("QUAZAR_SQL_USER")
        password = os.environ.get("QUAZAR_SQL_PASSWORD")
        if not user or not password:
            raise SystemExit("Set QUAZAR_SQL_USER and QUAZAR_SQL_PASSWORD before using --sql-auth.")
        return base + f"UID={user};PWD={password};"
    return base + "Trusted_Connection=yes;"


def read_csv(path: Path) -> tuple[list[str], list[tuple]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        rows = [tuple(None if row[column] == "" else row[column] for column in columns) for row in reader]
    return columns, rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default=r"localhost\SQLEXPRESS")
    parser.add_argument("--database", default="AutomotiveServiceOperations")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--sql-auth", action="store_true", help="Use credentials from QUAZAR_SQL_USER and QUAZAR_SQL_PASSWORD.")
    parser.add_argument("--keep-existing", action="store_true", help="Do not clear existing rows before loading.")
    args = parser.parse_args()

    connection = pyodbc.connect(connection_string(args), autocommit=False)
    cursor = connection.cursor()
    cursor.fast_executemany = True

    try:
        if not args.keep_existing:
            for table in DELETE_ORDER:
                cursor.execute(f"DELETE FROM dbo.[{table}];")

        for table, filename in LOAD_ORDER:
            columns, rows = read_csv(DATA / filename)
            column_sql = ", ".join(f"[{column}]" for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            insert_sql = f"INSERT INTO dbo.[{table}] ({column_sql}) VALUES ({placeholders});"
            cursor.executemany(insert_sql, rows)
            print(f"Loaded {len(rows):,} rows into dbo.{table}")

        connection.commit()
        print("Load completed successfully.")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
