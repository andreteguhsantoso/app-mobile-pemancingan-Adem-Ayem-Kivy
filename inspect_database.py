import argparse
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = PROJECT_DIR / "mvp.db"
HIDDEN_COLUMNS = {"password_hash", "password_salt"}


def print_table(connection, table_name, limit):
    columns = connection.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    visible_columns = [row[1] for row in columns if row[1] not in HIDDEN_COLUMNS]
    if not visible_columns:
        print(f"\n[{table_name}] tidak memiliki kolom yang dapat ditampilkan.")
        return

    selected = ", ".join(f'"{column}"' for column in visible_columns)
    rows = connection.execute(
        f'SELECT {selected} FROM "{table_name}" LIMIT ?', (limit,)
    ).fetchall()

    print(f"\n=== {table_name} ({len(rows)} baris ditampilkan) ===")
    if not rows:
        print("Belum ada data.")
        return

    widths = {
        column: max(
            len(column),
            *(len(str(row[column] if row[column] is not None else "NULL")) for row in rows),
        )
        for column in visible_columns
    }
    header = " | ".join(column.ljust(widths[column]) for column in visible_columns)
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            " | ".join(
                str(row[column] if row[column] is not None else "NULL").ljust(
                    widths[column]
                )
                for column in visible_columns
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description="Lihat isi database Pemancingan Adem Ayem tanpa membuka file biner."
    )
    parser.add_argument(
        "table",
        nargs="?",
        help="Nama tabel. Kosongkan untuk melihat daftar tabel.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maksimal baris.")
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help="Lokasi file SQLite.",
    )
    arguments = parser.parse_args()

    if not arguments.database.exists():
        raise SystemExit(f"Database tidak ditemukan: {arguments.database}")
    if arguments.limit < 1 or arguments.limit > 500:
        raise SystemExit("Limit harus berada di antara 1 dan 500.")

    connection = sqlite3.connect(arguments.database)
    connection.row_factory = sqlite3.Row
    try:
        tables = [
            row[0]
            for row in connection.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        ]
        if not arguments.table:
            print("Tabel tersedia:")
            for table in tables:
                count = connection.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
                print(f"- {table}: {count} baris")
            print("\nContoh: .\\.venv\\Scripts\\python.exe inspect_database.py bookings")
            return

        if arguments.table not in tables:
            raise SystemExit(
                f"Tabel '{arguments.table}' tidak ditemukan. Pilihan: {', '.join(tables)}"
            )
        print_table(connection, arguments.table, arguments.limit)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
