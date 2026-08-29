import gc
import os
import sqlite3
import sys
import tempfile


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import app as module


def run_smoke_test():
    handle, test_db = tempfile.mkstemp(prefix="nila-kediri-", suffix=".db")
    os.close(handle)
    os.unlink(test_db)
    module.DB_PATH = test_db

    application = module.FishingMVPApp()
    application.build()
    assert len(module.EVENTS) == 4
    assert len(application.spot_buttons) == 82
    assert module.EVENTS["NILA-GP"]["price"] == 100_000
    assert module.EVENTS["NILA-GP"]["release"] == "Pelepasan nila 225 kg"
    assert module.EVENTS["NILA-200"]["price"] == 85_000
    assert module.EVENTS["NILA-150"]["price"] == 70_000
    assert module.EVENTS["NILA-100"]["price"] == 50_000
    assert all(event["quota"] == 82 for event in module.EVENTS.values())
    assert module.GOOGLE_MAPS_URL == "https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7"

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

    application.start_booking("NILA-GP")
    application.select_spot(82)
    application.continue_to_booking_data()
    application.customer_name.text = "Budi Uji"
    application.customer_phone.text = "081234567890"
    application.bait_checkbox.active = True
    application.continue_to_payment()
    assert application.manager.current == "payment"

    application.submit_booking()
    assert application.manager.current == "ticket"
    with sqlite3.connect(test_db) as connection:
        booking = connection.execute(
            "SELECT spot_number, ticket_count FROM bookings"
        ).fetchone()
    connection.close()
    assert booking == (82, 1)
    assert application.ticket_code.text.startswith("PN-")

    ticket_code = application.ticket_code.text
    application.on_stop()
    del application
    gc.collect()
    os.unlink(test_db)
    print("BOOKING_FLOW_OK", ticket_code, booking)


if __name__ == "__main__":
    run_smoke_test()
