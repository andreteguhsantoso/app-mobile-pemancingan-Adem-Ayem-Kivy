import os
import sys


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault("KIVY_HOME", os.path.join(PROJECT_DIR, ".kivy"))

from kivy.clock import Clock

from app import FishingMVPApp


class SpotPreviewApp(FishingMVPApp):
    def on_start(self):
        self.manager.transition.duration = 0
        self.start_booking("NILA-GP")
        Clock.schedule_once(self.capture, 1.5)

    def capture(self, *_args):
        output = os.path.join(PROJECT_DIR, "wireframes", "implementation-lapak-82.png")
        self.root.export_to_png(output)
        print("PREVIEW_SAVED", output)
        self.stop()


if __name__ == "__main__":
    SpotPreviewApp().run()
