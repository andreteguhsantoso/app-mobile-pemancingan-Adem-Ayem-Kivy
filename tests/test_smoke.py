import gc
import os
import sys
import tempfile


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import app as module


def run_smoke_test():
    temporary_directory = tempfile.TemporaryDirectory()
    application = module.FishingMVPApp()
    application.database_path = os.path.join(temporary_directory.name, "smoke.db")
    application.build()

    assert application.title == "Pemancingan Adem Ayem Dlopo"
    assert len(module.EVENTS) == 4
    assert len(application.nav_buttons) == 5
    assert len(application.spot_buttons) == 82
    assert module.EVENTS["NILA-GP"]["price"] == 100_000
    assert module.EVENTS["NILA-GP"]["available"] == 14
    assert module.EVENTS["NILA-200"]["price"] == 85_000
    assert module.EVENTS["NILA-150"]["price"] == 70_000
    assert module.EVENTS["NILA-100"]["price"] == 50_000
    assert all(event["quota"] == 82 for event in module.EVENTS.values())
    assert module.GOOGLE_MAPS_URL == "https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7"
    assert module.DB_PATH.endswith("mvp.db")
    assert application.operational_status["venue_status"] == "Buka"
    assert application.manager.has_screen("admin_events")
    assert application.manager.has_screen("admin_gallery")
    assert application.manager.has_screen("admin_news")

    opened_urls = []
    original_open = module.webbrowser.open
    module.webbrowser.open = lambda url: opened_urls.append(url)
    application.open_map()
    module.webbrowser.open = original_open
    assert opened_urls == [module.GOOGLE_MAPS_URL]

    application.filter_events("200 KG")
    assert len(application.event_list.children) == 1
    application.filter_events("Semua")
    assert len(application.event_list.children) == 4

    application.filter_gallery("Tangkapan")
    assert len(application.gallery_grid.children) == 2
    application.filter_gallery("Semua")
    assert len(application.gallery_grid.children) == 6

    application.filter_news("Aturan")
    assert len(application.news_list.children) == 1
    application.filter_news("Semua")
    assert len(application.news_list.children) == 4

    application.database.create_event(
        {
            "event_id": "ADMIN-SMOKE",
            "title": "Event Dinamis Admin",
            "date": "1 Oktober 2026",
            "time": "08.00 - 12.00 WIB",
            "price": 60_000,
            "quota": 82,
            "release": "Pelepasan nila 125 kg",
            "image": "hero-nila.png",
        },
        initial_available=82,
    )
    application.database.create_gallery_item(
        "Galeri Dinamis", "Event", "gallery-nila.png"
    )
    application.database.create_news_item(
        {
            "category": "Pengumuman",
            "title": "Berita Dinamis",
            "summary": "Dibuat dari data admin.",
            "date": "17 September 2026",
            "badge": "TERBARU",
            "image": "gallery-release.png",
            "event_id": "ADMIN-SMOKE",
            "body": "Konten berita tersimpan di database.",
            "facts": "125 KG | 82 LAPAK",
        }
    )
    application.reload_content_data(refresh_widgets=True)
    assert "ADMIN-SMOKE" in module.EVENTS
    assert len(application.event_cards) == 5
    assert any(title == "Galeri Dinamis" for _, title, _ in module.GALLERY_ITEMS)
    assert module.NEWS_ITEMS[0]["title"] == "Berita Dinamis"

    application.filter_leaderboard("Hari Ini")
    assert len(application.leaderboard_list.children) == 3
    application.filter_leaderboard("Per Event")
    assert len(application.leaderboard_list.children) == 5

    application.start_booking("NILA-GP")
    assert application.manager.current == "auth"
    assert application.pending_booking_event_id == "NILA-GP"
    user = application.database.create_user(
        "budi_uji", "password-kuat", "Budi Uji", "081234567890"
    )
    application.complete_login(user)
    assert application.current_user["username"] == "budi_uji"
    assert application.manager.current == "booking"
    available_spot = next(
        number for number in range(1, 83) if number not in application.occupied_spots
    )
    application.select_spot(available_spot)
    application.continue_to_booking_data()
    application.customer_name.text = ""
    application.customer_name.focus = True
    module.Clock.tick()
    application.customer_name.insert_text("Budi Uji")
    assert application.customer_name.text == "Budi Uji"
    application.customer_phone.text = "081234567890"
    application.customer_notes.text = "Datang bersama keluarga"
    application.bait_checkbox.active = True
    application.continue_to_payment()
    assert application.manager.current == "payment"
    assert application.navigation.height == 0

    application.submit_booking()
    assert application.manager.current == "ticket"
    assert len(application.session_bookings) == 1
    booking = application.session_bookings[0]
    assert booking["spot_number"] == available_spot
    assert booking["ticket_count"] == 1
    assert booking["booking_code"].startswith("AA-")
    assert booking["user_id"] == user["id"]
    assert booking["customer_notes"] == "Datang bersama keluarga"
    assert application.remaining_spots("NILA-GP") == 13
    assert application.home_availability_label.text == "13 dari 82 lapak tersisa"

    application.start_booking("NILA-GP")
    assert available_spot in application.occupied_spots
    assert application.spot_buttons[available_spot].status == "occupied"
    application.open_saved_ticket(booking)
    assert application.current_ticket_booking == booking
    assert application.ticket_code.text == booking["booking_code"]

    application.database.set_settings(
        {
            "venue_status": "Tutup sementara",
            "fish_mood": "Biasa",
            "daily_release_kg": "100",
            "operator_note": "Perawatan air kolam.",
        }
    )
    application.operational_status = application.database.operational_status()
    application.refresh_operational_labels()
    assert application.home_status_label.text == "TUTUP SEMENTARA"
    assert application.home_release_label.text == "100 kg"

    application.go("profile")
    assert application.navigation.height > 0
    assert application.profile_active_count.value_label.text == "1"
    assert application.profile_ticket_title.text == module.EVENTS["NILA-GP"]["title"]

    ticket_code = booking["booking_code"]
    persisted = application.database.list_bookings(user_id=user["id"])
    assert len(persisted) == 1
    assert persisted[0]["booking_code"] == ticket_code
    application.on_stop()
    del application
    gc.collect()
    temporary_directory.cleanup()
    print("KIVY_PARITY_OK", ticket_code, available_spot)


if __name__ == "__main__":
    run_smoke_test()
