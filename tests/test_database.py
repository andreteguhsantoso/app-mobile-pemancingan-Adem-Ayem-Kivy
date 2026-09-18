import os
import sys
import tempfile
from datetime import datetime


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from database import BookingConflictError, BookingDatabase, BookingStateError


EVENTS = {
    "TEST-01": {
        "title": "Event Uji",
        "date": "1 Januari 2027",
        "time": "08.00 WIB",
        "price": 50_000,
        "quota": 4,
        "release": "Pelepasan nila 100 kg",
        "image": "event.png",
    }
}


def booking(code, spot, status="paid", user_id=None):
    return {
        "booking_code": code,
        "event_id": "TEST-01",
        "customer_name": "Pemancing Uji",
        "customer_phone": "081234567890",
        "customer_notes": "Datang lebih awal",
        "ticket_count": 1,
        "payment_method": "QRIS / GoPay / OVO",
        "total_amount": 52_500,
        "payment_status": status,
        "spot_number": spot,
        "bait_rule_accepted": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "payment_reference": f"SIM-{code}",
        "user_id": user_id,
    }


def run_database_test():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "booking.db")
        database = BookingDatabase(path)
        database.initialize(EVENTS, {"TEST-01": {1}})
        health = database.health_check()
        assert health["healthy"] is True
        assert health["counts"]["events"] == 1

        created_event = {
            "event_id": "TEST-ADMIN",
            "title": "Event Buatan Admin",
            "date": "2 Januari 2027",
            "time": "09.00 WIB",
            "price": 75_000,
            "quota": 82,
            "release": "Pelepasan nila 175 kg",
            "image": "C:/content/event.jpg",
        }
        database.create_event(created_event, initial_available=80)
        admin_event = next(
            row for row in database.list_events() if row["event_id"] == "TEST-ADMIN"
        )
        assert admin_event["available"] == 80
        created_event["title"] = "Event Admin Diperbarui"
        created_event["available"] = 79
        database.update_event("TEST-ADMIN", created_event)
        updated_admin_event = next(
            row for row in database.list_events() if row["event_id"] == "TEST-ADMIN"
        )
        assert updated_admin_event["title"] == "Event Admin Diperbarui"
        assert updated_admin_event["available"] == 79
        database.set_event_active("TEST-ADMIN", False)
        assert "TEST-ADMIN" not in {row["event_id"] for row in database.list_events()}
        assert "TEST-ADMIN" in {
            row["event_id"] for row in database.list_events(active_only=False)
        }

        gallery_id = database.create_gallery_item(
            "Foto Event Admin", "Event", "C:/content/gallery.jpg"
        )
        assert database.list_gallery_items()[0]["id"] == gallery_id
        database.set_gallery_active(gallery_id, False)
        assert database.list_gallery_items() == []

        leaderboard_id = database.create_leaderboard_entry(
            {
                "name": "Juara Uji",
                "event": "Event Uji",
                "biggest": 3.5,
                "total": 8.2,
                "count": 3,
                "spot": "Lapak 03",
                "image": "C:/content/champion.jpg",
                "periods": ("Per Event", "Bulanan"),
            }
        )
        assert database.list_leaderboard_entries()[0]["id"] == leaderboard_id
        leaderboard_update = database.list_leaderboard_entries()[0]
        leaderboard_update["biggest"] = 3.75
        database.update_leaderboard_entry(leaderboard_id, leaderboard_update)
        assert database.list_leaderboard_entries()[0]["biggest"] == 3.75
        database.set_leaderboard_active(leaderboard_id, False)
        assert database.list_leaderboard_entries() == []

        news_id = database.create_news_item(
            {
                "category": "Pengumuman",
                "title": "Berita dari Admin",
                "summary": "Ringkasan berita.",
                "date": "1 Januari 2027",
                "badge": "TERBARU",
                "image": "C:/content/news.jpg",
                "event_id": "TEST-01",
                "body": "Paragraf pertama.\n\nParagraf kedua.",
                "facts": "NILA | 82 LAPAK",
            }
        )
        assert database.list_news_items()[0]["id"] == news_id
        assert len(database.list_news_items()[0]["body"]) == 2
        database.set_news_active(news_id, False)
        assert database.list_news_items() == []

        user = database.create_user(
            "pemancing_uji", "password-kuat", "Pemancing Uji", "081234567890"
        )
        submission_id = database.create_gallery_item(
            "Kiriman Pengguna",
            "Tangkapan",
            "C:/content/user-gallery.jpg",
            actor="user:pemancing_uji",
            user_id=user["id"],
            submitted_by=user["full_name"],
            approved=False,
        )
        assert database.list_gallery_items() == []
        user_submissions = database.list_gallery_items(
            active_only=False, user_id=user["id"]
        )
        assert user_submissions[0]["moderation_status"] == "pending"
        database.moderate_gallery_item(submission_id, "approved")
        assert database.list_gallery_items()[0]["id"] == submission_id
        assert database.authenticate_user("PEMANCING_UJI", "password-kuat")["id"] == user["id"]
        assert database.authenticate_user("pemancing_uji", "password-salah") is None
        history = database.login_history(user["id"])
        assert len(history) == 2
        assert {row["success"] for row in history} == {0, 1}
        user = database.update_user(
            user["id"], "pemancing_baru", "Pemancing Baru", "089999999999"
        )
        assert user["username"] == "pemancing_baru"
        avatar_path = os.path.join(directory, "avatar-pemancing.jpg")
        user = database.update_user(
            user["id"], user["username"], user["full_name"], user["phone"], avatar_path
        )
        assert database.get_user(user["id"])["avatar_path"] == avatar_path
        user = database.update_user(
            user["id"], user["username"], user["full_name"], user["phone"], None
        )
        assert database.get_user(user["id"])["avatar_path"] is None
        database.change_password(user["id"], "password-kuat", "password-baru")
        assert database.authenticate_user("pemancing_baru", "password-kuat") is None
        assert database.authenticate_user("pemancing_baru", "password-baru") is not None
        database.set_user_status(user["id"], "inactive")
        assert database.authenticate_user("pemancing_baru", "password-baru") is None
        database.set_user_status(user["id"], "active")
        database.reset_user_password(user["id"], "password-admin")
        assert database.authenticate_user("pemancing_baru", "password-admin") is not None
        listed_user = database.list_users()[0]
        assert listed_user["last_login"] is not None
        assert listed_user["status"] == "active"

        assert database.occupied_spots("TEST-01") == {1}
        assert database.remaining_spots("TEST-01") == 3

        database.create_booking(booking("AA-TEST01", 2, user_id=user["id"]))
        assert database.occupied_spots("TEST-01") == {1, 2}
        assert database.remaining_spots("TEST-01") == 2

        saved = database.list_bookings()
        assert len(saved) == 1
        assert saved[0]["customer_notes"] == "Datang lebih awal"
        assert saved[0]["bait_rule_accepted"] is True
        assert database.list_bookings(user_id=user["id"])[0]["user_id"] == user["id"]

        second_connection = BookingDatabase(path)
        second_connection.initialize(EVENTS, {"TEST-01": {1}})
        assert second_connection.list_bookings()[0]["booking_code"] == "AA-TEST01"

        try:
            database.create_booking(booking("AA-TEST02", 2))
        except BookingConflictError:
            pass
        else:
            raise AssertionError("Lapak yang sama seharusnya ditolak")

        database.create_booking(booking("AA-TEST03", 3, "pay_at_venue", user["id"]))
        assert database.remaining_spots("TEST-01") == 1
        database.cancel_booking("AA-TEST03")
        assert database.remaining_spots("TEST-01") == 2
        assert database.list_bookings()[-1]["payment_status"] == "cancelled"

        try:
            database.cancel_booking("AA-TEST01")
        except BookingStateError:
            pass
        else:
            raise AssertionError("Tiket paid tidak boleh dibatalkan pelanggan")

        database.set_settings(
            {
                "venue_status": "Tutup sementara",
                "fish_mood": "Biasa",
                "daily_release_kg": "100",
                "operator_note": "Perawatan air.",
            }
        )
        status = database.operational_status()
        assert status["venue_status"] == "Tutup sementara"
        assert status["daily_release_kg"] == "100"

        backup_path = database.backup(os.path.join(directory, "backups"))
        assert os.path.exists(backup_path)

    print("DATABASE_OK")


if __name__ == "__main__":
    run_database_test()
