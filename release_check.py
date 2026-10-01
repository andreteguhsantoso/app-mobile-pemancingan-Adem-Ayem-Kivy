import argparse
import os
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
APP_VERSION = "1.3.0"


def check_local_release():
    failures = []
    required_files = (
        PROJECT_DIR / "app.py",
        PROJECT_DIR / "database.py",
        PROJECT_DIR / "media_picker.py",
        PROJECT_DIR / "supabase_client.py",
        PROJECT_DIR / "backend_sync.py",
        PROJECT_DIR / "mvp.db",
        PROJECT_DIR / "assets" / "generated" / "brand-adem-ayem-icon.png",
        PROJECT_DIR / "buildozer.spec",
        PROJECT_DIR / "adem_ayem.spec",
    )
    for path in required_files:
        if not path.exists():
            failures.append(f"File wajib tidak ditemukan: {path}")

    database_path = PROJECT_DIR / "mvp.db"
    if database_path.exists():
        connection = sqlite3.connect(database_path)
        try:
            quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
            foreign_key_issues = connection.execute("PRAGMA foreign_key_check").fetchall()
            if quick_check != "ok":
                failures.append(f"SQLite quick_check: {quick_check}")
            if foreign_key_issues:
                failures.append(
                    f"SQLite memiliki {len(foreign_key_issues)} masalah foreign key."
                )
        finally:
            connection.close()

    build_config = PROJECT_DIR / "buildozer.spec"
    if build_config.exists() and f"version = {APP_VERSION}" not in build_config.read_text(
        encoding="utf-8"
    ):
        failures.append("Versi buildozer tidak sama dengan versi aplikasi.")

    return failures


def missing_public_services():
    missing = []
    backend_config = PROJECT_DIR / "backend_config.json"
    if not (
        backend_config.exists()
        or (
            os.environ.get("ADEM_AYEM_SUPABASE_URL")
            and os.environ.get("ADEM_AYEM_SUPABASE_PUBLISHABLE_KEY")
        )
    ):
        missing.append("proyek dan Publishable key Supabase khusus Kivy")
    for key, description in {
        "ADEM_AYEM_PAYMENT_PROVIDER": "payment gateway resmi",
        "ADEM_AYEM_PRIVACY_URL": "URL kebijakan privasi publik",
    }.items():
        if not os.environ.get(key):
            missing.append(description)
    return missing


def main():
    parser = argparse.ArgumentParser(description="Audit kesiapan rilis Adem Ayem.")
    parser.add_argument(
        "--strict-public",
        action="store_true",
        help="Gagal jika layanan produksi eksternal belum dikonfigurasi.",
    )
    arguments = parser.parse_args()

    failures = check_local_release()
    if failures:
        print("LOCAL_RELEASE_NOT_READY")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(f"LOCAL_BETA_READY | versi {APP_VERSION}")
    missing = missing_public_services()
    if missing:
        print("PUBLIC_MULTI_DEVICE_BLOCKED")
        for requirement in missing:
            print(f"- Belum tersedia: {requirement}")
        if arguments.strict_public:
            raise SystemExit(2)
    else:
        print("PUBLIC_SERVICE_CONFIGURATION_PRESENT")


if __name__ == "__main__":
    main()
