import os
import sys


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault("KIVY_HOME", os.path.join(PROJECT_DIR, ".kivy"))

from kivy.clock import Clock

from app import FishingMVPApp


class ScreenPreviewApp(FishingMVPApp):
    preview_target = sys.argv[1] if len(sys.argv) > 1 else "home"

    def on_start(self):
        self.manager.transition.duration = 0
        if self.preview_target in (
            "booking",
            "booking_data",
            "payment",
            "edit_profile",
            "profile_member",
            "account_security",
            "gallery_submit",
        ):
            self.current_user = {
                "id": 999,
                "username": "budi_santoso",
                "full_name": "Budi Santoso",
                "phone": "081234567890",
                "avatar_path": None,
            }
        if self.preview_target == "event_detail":
            self.open_event_detail("NILA-GP")
        elif self.preview_target == "booking":
            self.start_booking("NILA-GP")
        elif self.preview_target in ("booking_data", "payment"):
            self.start_booking("NILA-GP")
            available_spot = next(
                number for number in range(1, 83) if number not in self.occupied_spots
            )
            self.select_spot(available_spot)
            self.continue_to_booking_data()
            self.customer_name.text = "Budi Santoso"
            self.customer_phone.text = "081234567890"
            self.customer_notes.text = "Datang 30 menit sebelum acara"
            if self.preview_target == "payment":
                self.bait_checkbox.active = True
                self.continue_to_payment()
        elif self.preview_target == "ticket":
            self.ticket_event.text = "Grand Mix Babaon"
            self.ticket_code.text = "AA-DEMO82"
            self.ticket_qr.set_code("AA-DEMO82")
            self.ticket_detail.text = "Minggu, 6 September 2026\nLapak 82 | Rp 102.500\nQRIS / GoPay / OVO"
            self.ticket_status.text = "PEMBAYARAN BERHASIL"
            self.go("ticket")
        elif self.preview_target == "news_detail":
            self.open_news_detail(__import__("app").NEWS_ITEMS[2])
        elif self.preview_target == "edit_profile":
            self.open_account_settings()
        elif self.preview_target == "profile_member":
            self.refresh_profile()
            self.go("profile")
        elif self.preview_target == "account_security":
            self.open_account_security()
        elif self.preview_target == "admin_users":
            self.admin_authenticated = True
            self.open_admin_users()
        elif self.preview_target == "admin_events":
            self.admin_authenticated = True
            self.open_admin_events()
        elif self.preview_target == "admin_gallery":
            self.admin_authenticated = True
            self.open_admin_gallery()
        elif self.preview_target == "admin_news":
            self.admin_authenticated = True
            self.open_admin_news()
        elif self.preview_target == "admin_leaderboard":
            self.admin_authenticated = True
            self.open_admin_leaderboard()
        elif self.preview_target == "gallery_submit":
            self.refresh_user_gallery_submissions()
            self.go("gallery_submit")
        elif self.preview_target != "home":
            self.go(self.preview_target)
        Clock.schedule_once(self.capture, 4.0)

    def capture(self, *_args):
        output = os.path.join(
            PROJECT_DIR,
            "wireframes",
            f"implementation-{self.preview_target}.png",
        )
        self.root.export_to_png(output)
        print("PREVIEW_SAVED", output)
        self.stop()


if __name__ == "__main__":
    ScreenPreviewApp().run()
