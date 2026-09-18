import argparse
import os
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
APP_VERSION = "1.2.0"


def check_local_release():
    failures = []
    required_files = (
        PROJECT_DIR / "app.py",
        PROJECT_DIR / "database.py",
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

    admin_pin = os.environ.get("ADEM_AYEM_ADMIN_PIN", "").strip()
    if admin_pin and len(admin_pin) < 6:
        failures.append("ADEM_AYEM_ADMIN_PIN harus minimal 6 karakter.")
    return failures


def missing_public_services():
    requirements = {
        "ADEM_AYEM_API_URL": "backend HTTPS pusat",
        "ADEM_AYEM_PAYMENT_PROVIDER": "payment gateway resmi",
        "ADEM_AYEM_PRIVACY_URL": "URL kebijakan privasi publik",
    }
    return [description for key, description in requirements.items() if not os.environ.get(key)]


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
