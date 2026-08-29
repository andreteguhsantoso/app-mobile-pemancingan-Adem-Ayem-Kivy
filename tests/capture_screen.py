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
        if self.preview_target == "event_detail":
            self.open_event_detail("NILA-GP")
        elif self.preview_target == "booking":
            self.start_booking("NILA-GP")
        elif self.preview_target == "ticket":
            self.ticket_event.text = "Grand Mix Babaon 225 KG"
            self.ticket_code.text = "PN-DEMO82"
            self.ticket_qr.set_code("PN-DEMO82")
            self.ticket_detail.text = "Minggu, 6 September 2026\nLapak 82 | Rp 102.500\nQRIS / GoPay / OVO"
            self.ticket_status.text = "MENUNGGU PEMBAYARAN"
            self.go("ticket")
        elif self.preview_target != "home":
            self.go(self.preview_target)
        Clock.schedule_once(self.capture, 1.5)

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
