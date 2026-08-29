import hashlib
import os
import sqlite3
import webbrowser
from datetime import datetime
from uuid import uuid4

os.environ.setdefault("KIVY_HOME", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".kivy"))

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import platform as kivy_platform


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets", "generated")
DB_PATH = os.path.join(BASE_DIR, "mvp.db")
GOOGLE_MAPS_URL = "https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7"
WINDOWS_FONT_DIR = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")


def system_font(filename, fallback="Roboto"):
    path = os.path.join(WINDOWS_FONT_DIR, filename)
    return path if os.path.exists(path) else fallback


FONT_DISPLAY = system_font("bahnschrift.ttf")
FONT_BODY = system_font("trebuc.ttf")


COLORS = {
    "cream": (0.965, 0.953, 0.91, 1),
    "forest": (0.025, 0.245, 0.27, 1),
    "deep_forest": (0.018, 0.16, 0.18, 1),
    "terracotta": (0.82, 0.31, 0.18, 1),
    "ink": (0.075, 0.11, 0.105, 1),
    "muted": (0.34, 0.39, 0.37, 1),
    "mint": (0.80, 0.90, 0.84, 1),
    "sage": (0.36, 0.63, 0.52, 1),
    "sand": (0.95, 0.76, 0.34, 1),
    "sky": (0.38, 0.71, 0.86, 1),
    "coral": (0.91, 0.43, 0.35, 1),
    "white": (1, 1, 1, 1),
}


HERO_SLIDES = (
    {
        "image": "carousel-event-nila.png",
        "kicker": "EVENT PILIHAN PEKAN INI",
        "title": "Grand Mix Babaon 225 KG",
        "meta": "Minggu, 6 Sep | Rp 100.000",
        "event_id": "NILA-GP",
    },
    {
        "image": "gallery-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Pelepasan Nila 200 KG",
        "meta": "Sabtu, 12 Sep | Rp 85.000",
        "event_id": "NILA-200",
    },
    {
        "image": "carousel-night-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Pelepasan Nila 150 KG",
        "meta": "Jumat, 18 Sep | Rp 70.000",
        "event_id": "NILA-150",
    },
    {
        "image": "hero-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Pelepasan Nila 100 KG",
        "meta": "Sabtu, 26 Sep | Rp 50.000",
        "event_id": "NILA-100",
    },
)


EVENTS = {
    "NILA-GP": {
        "title": "Grand Mix Babaon 225 KG",
        "date": "Minggu, 6 September 2026",
        "time": "08.00 - 13.00 WIB",
        "price": 100_000,
        "quota": 82,
        "available": 82,
        "release": "Pelepasan nila 225 kg",
        "image": "carousel-event-nila.png",
    },
    "NILA-200": {
        "title": "Event Nila 200 KG",
        "date": "Sabtu, 12 September 2026",
        "time": "15.00 - 20.00 WIB",
        "price": 85_000,
        "quota": 82,
        "available": 82,
        "release": "Pelepasan nila 200 kg",
        "image": "gallery-nila.png",
    },
    "NILA-150": {
        "title": "Event Nila 150 KG",
        "date": "Jumat, 18 September 2026",
        "time": "19.00 - 23.30 WIB",
        "price": 70_000,
        "quota": 82,
        "available": 82,
        "release": "Pelepasan nila 150 kg",
        "image": "carousel-night-nila.png",
    },
    "NILA-100": {
        "title": "Event Nila 100 KG",
        "date": "Sabtu, 26 September 2026",
        "time": "08.00 - 13.00 WIB",
        "price": 50_000,
        "quota": 82,
        "available": 82,
        "release": "Pelepasan nila 100 kg",
        "image": "hero-nila.png",
    },
}


BAIT_RULE_SHORT = "Umpan wajib alami. Essen/pemanis boleh hanya sebagai campuran umpan alami."
BAIT_RULE_FULL = (
    "Umpan hanya boleh berasal dari bahan alami, misalnya cacing, lumut, jagung, "
    "singkong, kroto, atau racikan bahan pangan alami. Media, bahan, atau umpan lain "
    "yang tidak berasal dari alam dilarang. Essen dan pemanis diperbolehkan hanya "
    "sebagai campuran pada umpan alami, bukan digunakan sebagai umpan utama."
)


def asset(filename):
    return os.path.join(ASSET_DIR, filename)


def rupiah(value):
    return "Rp {:,.0f}".format(value).replace(",", ".")


def label(text, height=dp(30), size=14, color=None, bold=False, halign="left"):
    widget = Label(
        text=text,
        size_hint_y=None,
        height=height,
        font_size=f"{size}sp",
        font_name=FONT_DISPLAY if bold else FONT_BODY,
        color=color or COLORS["ink"],
        bold=bold,
        halign=halign,
        valign="middle",
    )
    widget.bind(size=lambda instance, value: setattr(instance, "text_size", value))
    return widget


class Card(BoxLayout):
    def __init__(self, background=None, radius=18, **kwargs):
        super().__init__(**kwargs)
        self.background = background or COLORS["white"]
        self.radius = dp(radius)
        with self.canvas.before:
            self.shadow_color = Color(0.01, 0.10, 0.11, 0.10)
            self.shadow_rect = RoundedRectangle(
                pos=(self.x, self.y - dp(3)), size=self.size, radius=[self.radius]
            )
            self.card_color = Color(*self.background)
            self.card_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
        with self.canvas.after:
            self.border_color = Color(0.02, 0.18, 0.19, 0.10)
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=0.8,
            )
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_args):
        self.shadow_rect.pos = (self.x, self.y - dp(3))
        self.shadow_rect.size = self.size
        self.card_rect.pos = self.pos
        self.card_rect.size = self.size
        self.border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self.radius,
        )


class AccentMark(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_x", None)
        kwargs.setdefault("width", dp(5))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*COLORS["terracotta"])
            self.mark_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(3)])
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_args):
        self.mark_rect.pos = self.pos
        self.mark_rect.size = self.size


def section_heading(title, subtitle=None):
    height = dp(50 if subtitle else 34)
    row = BoxLayout(size_hint_y=None, height=height, spacing=dp(9))
    row.add_widget(AccentMark())
    copy = BoxLayout(orientation="vertical", spacing=dp(0))
    copy.add_widget(label(title, dp(28), 18, COLORS["forest"], True))
    if subtitle:
        copy.add_widget(label(subtitle, dp(20), 10, COLORS["muted"]))
    row.add_widget(copy)
    return row


def booking_progress(active_step):
    row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(6))
    for step, title in enumerate(("LAPAK", "DATA", "BAYAR", "TIKET"), start=1):
        active = step == active_step
        complete = step < active_step
        background = COLORS["forest"] if active else COLORS["mint"] if complete else COLORS["white"]
        text_color = COLORS["white"] if active else COLORS["forest"]
        item = Card(orientation="vertical", padding=dp(4), background=background, radius=11)
        item.add_widget(label(f"0{step}", 22, 10, COLORS["sand"] if active else COLORS["terracotta"], True, "center"))
        item.add_widget(label(title, 22, 9, text_color, True, "center"))
        row.add_widget(item)
    return row


class PrimaryButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", COLORS["white"])
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_name", FONT_DISPLAY)
        super().__init__(**kwargs)
        self.resting_color = COLORS["terracotta"]
        self.pressed_color = (0.68, 0.22, 0.12, 1)
        with self.canvas.before:
            self.button_color = Color(*self.resting_color)
            self.button_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._sync_canvas, size=self._sync_canvas, state=self._sync_state)

    def _sync_canvas(self, *_args):
        self.button_rect.pos = self.pos
        self.button_rect.size = self.size

    def _sync_state(self, *_args):
        self.button_color.rgba = self.pressed_color if self.state == "down" else self.resting_color


class GhostButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(44))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", COLORS["forest"])
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_name", FONT_DISPLAY)
        super().__init__(**kwargs)
        self.resting_color = COLORS["mint"]
        self.pressed_color = (0.66, 0.82, 0.72, 1)
        with self.canvas.before:
            self.button_color = Color(*self.resting_color)
            self.button_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._sync_canvas, size=self._sync_canvas, state=self._sync_state)

    def _sync_canvas(self, *_args):
        self.button_rect.pos = self.pos
        self.button_rect.size = self.size

    def _sync_state(self, *_args):
        self.button_color.rgba = self.pressed_color if self.state == "down" else self.resting_color


class NavButton(Button):
    def __init__(self, active=False, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", "10sp")
        kwargs.setdefault("font_name", FONT_DISPLAY)
        kwargs.setdefault("halign", "center")
        super().__init__(**kwargs)
        self.active = active
        with self.canvas.before:
            self.nav_color = Color(*(COLORS["mint"] if active else (0, 0, 0, 0)))
            self.nav_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        with self.canvas.after:
            self.indicator_color = Color(*(COLORS["terracotta"] if active else (0, 0, 0, 0)))
            self.indicator_rect = RoundedRectangle(
                pos=(self.x + dp(13), self.top - dp(4)),
                size=(max(0, self.width - dp(26)), dp(3)),
                radius=[dp(2)],
            )
        self.set_active(active)
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_args):
        self.nav_rect.pos = self.pos
        self.nav_rect.size = self.size
        self.indicator_rect.pos = (self.x + dp(13), self.top - dp(4))
        self.indicator_rect.size = (max(0, self.width - dp(26)), dp(3))

    def set_active(self, active):
        self.active = active
        self.nav_color.rgba = COLORS["mint"] if active else (0, 0, 0, 0)
        self.indicator_color.rgba = COLORS["terracotta"] if active else (0, 0, 0, 0)
        self.color = COLORS["forest"] if active else COLORS["muted"]


class SpotButton(Button):
    STATUS_COLORS = {
        "available": COLORS["mint"],
        "occupied": COLORS["coral"],
        "selected": COLORS["sky"],
    }

    def __init__(self, number, **kwargs):
        kwargs.setdefault("text", f"{number:02d}")
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", COLORS["forest"])
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", "10sp")
        kwargs.setdefault("font_name", FONT_DISPLAY)
        super().__init__(**kwargs)
        self.number = number
        self.status = "available"
        with self.canvas.before:
            self.spot_color = Color(*COLORS["mint"])
            self.spot_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(7)])
        with self.canvas.after:
            self.spot_border_color = Color(0.02, 0.18, 0.19, 0.22)
            self.spot_border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(7)),
                width=0.7,
            )
        self.bind(pos=self._sync_canvas, size=self._sync_canvas, state=self._sync_state)

    def _sync_canvas(self, *_args):
        self.spot_rect.pos = self.pos
        self.spot_rect.size = self.size
        self.spot_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(7),
        )

    def _sync_state(self, *_args):
        base = self.STATUS_COLORS[self.status]
        self.spot_color.rgba = tuple(value * 0.88 for value in base[:3]) + (1,) if self.state == "down" else base

    def set_status(self, status):
        self.status = status
        self.disabled = status == "occupied"
        self.spot_color.rgba = self.STATUS_COLORS[status]
        self.color = COLORS["white"] if status == "occupied" else COLORS["forest"]


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("padding", (dp(13), dp(14)))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("foreground_color", COLORS["ink"])
        kwargs.setdefault("cursor_color", COLORS["terracotta"])
        kwargs.setdefault("font_name", FONT_BODY)
        super().__init__(**kwargs)
        with self.canvas.before:
            self.field_color = Color(*COLORS["white"])
            self.field_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        with self.canvas.after:
            self.field_border_color = Color(0.02, 0.18, 0.19, 0.18)
            self.field_border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=0.9,
            )
        self.bind(pos=self._sync_canvas, size=self._sync_canvas, focus=self._sync_focus)

    def _sync_canvas(self, *_args):
        self.field_rect.pos = self.pos
        self.field_rect.size = self.size
        self.field_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(12),
        )

    def _sync_focus(self, *_args):
        self.field_border_color.rgba = COLORS["terracotta"] if self.focus else (0.02, 0.18, 0.19, 0.18)


class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", COLORS["forest"])
        kwargs.setdefault("font_name", FONT_DISPLAY)
        super().__init__(**kwargs)
        with self.canvas.before:
            self.spinner_color = Color(*COLORS["mint"])
            self.spinner_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_args):
        self.spinner_rect.pos = self.pos
        self.spinner_rect.size = self.size


class TicketMatrix(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = "NILA-KEDIRI"
        self.bind(pos=self._draw, size=self._draw)

    def set_code(self, code):
        self.code = code
        self._draw()

    def _draw(self, *_args):
        if self.width <= 0 or self.height <= 0:
            return
        grid_size = 15
        side = min(self.width, self.height)
        cell = side / grid_size
        origin_x = self.x + (self.width - side) / 2
        origin_y = self.y + (self.height - side) / 2
        digest = hashlib.sha256(self.code.encode("utf-8")).digest()
        self.canvas.clear()
        with self.canvas:
            Color(*COLORS["white"])
            RoundedRectangle(pos=(origin_x, origin_y), size=(side, side), radius=[dp(8)])
            Color(*COLORS["ink"])
            for row in range(grid_size):
                for col in range(grid_size):
                    finder = (
                        (row < 5 and col < 5)
                        or (row < 5 and col >= grid_size - 5)
                        or (row >= grid_size - 5 and col < 5)
                    )
                    border = row in (0, 4) or col in (0, 4)
                    center = 1 <= row % 10 <= 3 and 1 <= col % 10 <= 3
                    digest_bit = (digest[(row * grid_size + col) % len(digest)] >> (col % 8)) & 1
                    if (finder and (border or center)) or (not finder and digest_bit):
                        Rectangle(
                            pos=(origin_x + col * cell, origin_y + (grid_size - row - 1) * cell),
                            size=(cell * 0.88, cell * 0.88),
                        )


def page_content(padding=(18, 18, 18, 30), spacing=14):
    content = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        padding=[dp(value) for value in padding],
        spacing=dp(spacing),
    )
    content.bind(minimum_height=content.setter("height"))
    scroll = ScrollView(do_scroll_x=False)
    scroll.add_widget(content)
    return scroll, content


class FishingMVPApp(App):
    title = "Pemancingan Nila Kediri"

    def build(self):
        Window.clearcolor = COLORS["cream"]
        # Desktop/Linux uses a 1:2 phone preview that still fits a 720 px screen.
        # Android and iOS use the device viewport supplied by the operating system.
        if kivy_platform not in ("android", "ios"):
            Window.size = (340, 680)
        self.prepare_database()
        self.current_event_id = None
        self.hero_index = 0

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*COLORS["cream"])
            root.background_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(root.background_rect, "pos", root.pos))
        root.bind(size=lambda *_: setattr(root.background_rect, "size", root.size))
        self.manager = ScreenManager(transition=NoTransition())
        self.manager.add_widget(self.build_home())
        self.manager.add_widget(self.build_events())
        self.manager.add_widget(self.build_event_detail())
        self.manager.add_widget(self.build_booking())
        self.manager.add_widget(self.build_booking_data())
        self.manager.add_widget(self.build_payment())
        self.manager.add_widget(self.build_ticket())
        self.manager.add_widget(self.build_gallery())
        self.manager.add_widget(self.build_leaderboard())
        self.manager.add_widget(self.build_news())
        self.manager.add_widget(self.build_daily_status())
        self.manager.add_widget(self.build_orders())
        self.manager.add_widget(self.build_admin())
        self.manager.add_widget(self.build_operations())
        self.manager.add_widget(self.build_info())
        root.add_widget(self.manager)
        root.add_widget(self.build_navigation())
        self.hero_clock = Clock.schedule_interval(self.next_hero_slide, 5)
        return root

    def prepare_database(self):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_code TEXT UNIQUE NOT NULL,
                    event_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    ticket_count INTEGER NOT NULL,
                    payment_method TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    payment_status TEXT NOT NULL,
                    spot_number INTEGER,
                    bait_rule_accepted INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(bookings)")
            }
            if "bait_rule_accepted" not in columns:
                connection.execute(
                    "ALTER TABLE bookings ADD COLUMN bait_rule_accepted INTEGER NOT NULL DEFAULT 1"
                )
            if "spot_number" not in columns:
                connection.execute("ALTER TABLE bookings ADD COLUMN spot_number INTEGER")

    def build_navigation(self):
        nav = BoxLayout(
            size_hint_y=None,
            height=dp(68),
            padding=(dp(7), dp(7)),
            spacing=dp(4),
        )
        with nav.canvas.before:
            Color(*COLORS["white"])
            nav.bg = RoundedRectangle(pos=nav.pos, size=nav.size, radius=[dp(12)])
        nav.bind(pos=lambda *_: setattr(nav.bg, "pos", nav.pos))
        nav.bind(size=lambda *_: setattr(nav.bg, "size", nav.size))
        self.nav_buttons = {}
        for title, screen_name in (
            ("HOME\nBeranda", "home"),
            ("AGENDA\nEvent", "events"),
            ("TIKET\nBooking", "booking"),
            ("MOMEN\nGaleri", "gallery"),
            ("LOKASI\nInfo", "info"),
        ):
            button = NavButton(
                text=title,
                active=screen_name == "home",
            )
            if screen_name == "booking":
                button.bind(on_release=lambda *_: self.open_booking_nav())
            else:
                button.bind(on_release=lambda _button, name=screen_name: self.go(name))
            self.nav_buttons[screen_name] = button
            nav.add_widget(button)
        return nav

    def build_home(self):
        screen = Screen(name="home")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=12)

        app_bar = Card(
            size_hint_y=None,
            height=dp(72),
            padding=(dp(16), dp(10)),
            background=COLORS["forest"],
            spacing=dp(8),
        )
        brand = BoxLayout(orientation="vertical")
        brand.add_widget(label("NILA KEDIRI", 30, 18, COLORS["white"], True))
        brand.add_widget(label("Kolam khusus ikan nila", 22, 10, COLORS["mint"]))
        app_bar.add_widget(brand)
        status = BoxLayout(orientation="vertical", size_hint_x=0.34)
        status.add_widget(label("BUKA HARI INI", 25, 9, COLORS["sand"], True, "right"))
        status.add_widget(label("06.00 - 22.00", 25, 11, COLORS["white"], True, "right"))
        app_bar.add_widget(status)
        content.add_widget(app_bar)

        announcement = Card(
            size_hint_y=None,
            height=dp(42),
            padding=(dp(12), dp(6)),
            background=COLORS["sand"],
        )
        announcement.add_widget(label("4 PAKET EVENT", 28, 10, COLORS["forest"], True))
        announcement.add_widget(label("82 LAPAK", 28, 10, COLORS["forest"], True, "center"))
        announcement.add_widget(label("MULAI 50RB", 28, 10, COLORS["terracotta"], True, "right"))
        content.add_widget(announcement)

        hero = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(326),
            padding=dp(0),
            spacing=dp(0),
            background=COLORS["deep_forest"],
        )
        self.hero_image = Image(
            source=asset(HERO_SLIDES[0]["image"]),
            size_hint_y=None,
            height=dp(190),
            fit_mode="cover",
        )
        hero.add_widget(self.hero_image)
        hero_info = BoxLayout(
            orientation="vertical",
            padding=(dp(15), dp(8), dp(12), dp(10)),
            spacing=dp(2),
        )
        top_line = BoxLayout(size_hint_y=None, height=dp(20))
        self.hero_kicker = label(HERO_SLIDES[0]["kicker"], 20, 9, COLORS["sand"], True)
        self.hero_counter = label(f"1 / {len(HERO_SLIDES)}", 20, 9, COLORS["mint"], True, "right")
        top_line.add_widget(self.hero_kicker)
        top_line.add_widget(self.hero_counter)
        hero_info.add_widget(top_line)
        self.hero_title = label(HERO_SLIDES[0]["title"], 31, 19, COLORS["white"], True)
        hero_info.add_widget(self.hero_title)
        hero_actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(7))
        previous_button = GhostButton(text="<", width=dp(38), size_hint_x=None, height=dp(40))
        previous_button.bind(on_release=lambda *_: self.previous_hero_slide())
        self.hero_meta = label(HERO_SLIDES[0]["meta"], 40, 10, COLORS["mint"])
        order_button = PrimaryButton(text="Pesan", size_hint_x=None, width=dp(78), height=dp(40))
        order_button.bind(on_release=lambda *_: self.open_current_hero())
        next_button = GhostButton(text=">", width=dp(38), size_hint_x=None, height=dp(40))
        next_button.bind(on_release=lambda *_: self.next_hero_slide())
        hero_actions.add_widget(previous_button)
        hero_actions.add_widget(self.hero_meta)
        hero_actions.add_widget(order_button)
        hero_actions.add_widget(next_button)
        hero_info.add_widget(hero_actions)
        hero.add_widget(hero_info)
        content.add_widget(hero)

        content.add_widget(section_heading("Akses cepat", "Pilih kebutuhan Anda"))
        shortcuts = BoxLayout(size_hint_y=None, height=dp(102), spacing=dp(8))
        shortcuts.add_widget(self.quick_action("01", "BOOKING\nLAPAK", COLORS["sky"], lambda: self.start_booking("NILA-GP")))
        shortcuts.add_widget(self.quick_action("02", "JADWAL\nEVENT", COLORS["sage"], lambda: self.go("events")))
        shortcuts.add_widget(self.quick_action("03", "JUARA\nNILA", COLORS["sand"], lambda: self.go("leaderboard")))
        shortcuts.add_widget(self.quick_action("04", "GALERI\nMOMEN", COLORS["coral"], lambda: self.go("gallery")))
        content.add_widget(shortcuts)

        content.add_widget(section_heading("Jadwal terdekat", "Amankan lapak sebelum penuh"))
        next_event = Card(
            size_hint_y=None,
            height=dp(126),
            padding=dp(12),
            spacing=dp(11),
            background=COLORS["white"],
        )
        event_date = Card(
            orientation="vertical",
            size_hint_x=None,
            width=dp(64),
            padding=dp(6),
            background=COLORS["sand"],
        )
        event_date.add_widget(label("06", 42, 24, COLORS["forest"], True, "center"))
        event_date.add_widget(label("SEP", 24, 10, COLORS["forest"], True, "center"))
        next_event.add_widget(event_date)
        event_copy = BoxLayout(orientation="vertical", spacing=dp(1))
        event_copy.add_widget(label("Grand Mix Babaon 225 KG", 28, 16, COLORS["forest"], True))
        event_copy.add_widget(label("08.00 - 13.00 | Tiket Rp 100.000", 23, 11, COLORS["muted"]))
        event_copy.add_widget(label("82 lapak tersedia", 22, 10, COLORS["terracotta"], True))
        event_button = PrimaryButton(text="Daftar sekarang", height=dp(34), size_hint_x=0.7)
        event_button.bind(on_release=lambda *_: self.start_booking("NILA-GP"))
        event_copy.add_widget(event_button)
        next_event.add_widget(event_copy)
        content.add_widget(next_event)

        content.add_widget(section_heading("Kondisi kolam hari ini", "Informasi terbaru dari petugas"))
        stats = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        for value, caption, background in (
            ("225 kg", "Nila dilepas", COLORS["mint"]),
            ("AKTIF", "Mood makan", COLORS["sand"]),
            ("27 C", "Berawan", COLORS["sky"]),
        ):
            stat = Card(orientation="vertical", padding=dp(10), background=background)
            stat.add_widget(label(value, 36, 18, COLORS["forest"], True, "center"))
            stat.add_widget(label(caption, 25, 10, COLORS["muted"], False, "center"))
            stats.add_widget(stat)
        content.add_widget(stats)

        bait_card = Card(size_hint_y=None, height=dp(92), padding=dp(12), spacing=dp(10), background=COLORS["forest"])
        bait_copy = BoxLayout(orientation="vertical")
        bait_copy.add_widget(label("UMPAN ALAMI SAJA", 28, 13, COLORS["sand"], True))
        bait_copy.add_widget(label("Essen/pemanis boleh sebagai campuran.", 30, 10, COLORS["mint"]))
        bait_card.add_widget(bait_copy)
        rule_button = GhostButton(text="Aturan", size_hint_x=None, width=dp(82), height=dp(40))
        rule_button.bind(on_release=lambda *_: self.go("info"))
        bait_card.add_widget(rule_button)
        content.add_widget(bait_card)

        content.add_widget(section_heading("Temukan lokasi", "Gunakan titik resmi pemancingan"))
        location_card = Card(
            size_hint_y=None,
            height=dp(148),
            padding=dp(10),
            spacing=dp(11),
            background=COLORS["white"],
        )
        location_card.add_widget(
            Image(
                source=asset("venue-nila.png"),
                size_hint_x=0.36,
                fit_mode="cover",
            )
        )
        location_copy = BoxLayout(orientation="vertical", spacing=dp(2))
        location_copy.add_widget(label("TITIK RESMI GOOGLE MAPS", 22, 9, COLORS["terracotta"], True))
        location_copy.add_widget(label("Pemancingan Nila Kediri", 30, 15, COLORS["forest"], True))
        location_copy.add_widget(label("Buka rute langsung dari lokasi Anda.", 26, 10, COLORS["muted"]))
        home_map_button = PrimaryButton(text="Buka Maps", height=dp(36), size_hint_x=0.68)
        home_map_button.bind(on_release=lambda *_: self.open_map())
        location_copy.add_widget(home_map_button)
        location_card.add_widget(location_copy)
        content.add_widget(location_card)
        screen.add_widget(scroll)
        return screen

    def quick_action(self, number, title, background, callback):
        card = Card(orientation="vertical", padding=dp(6), spacing=dp(2), background=background)
        action = Button(
            text=f"{number}\n{title}",
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=COLORS["forest"],
            bold=True,
            font_size="11sp",
            font_name=FONT_DISPLAY,
            halign="center",
        )
        action.bind(on_release=lambda *_: callback())
        card.add_widget(action)
        return card

    def show_hero_slide(self, index):
        self.hero_index = index % len(HERO_SLIDES)
        slide = HERO_SLIDES[self.hero_index]
        self.hero_image.opacity = 0
        self.hero_image.source = asset(slide["image"])
        self.hero_kicker.text = slide["kicker"]
        self.hero_title.text = slide["title"]
        self.hero_meta.text = slide["meta"]
        self.hero_counter.text = f"{self.hero_index + 1} / {len(HERO_SLIDES)}"
        Animation(opacity=1, duration=0.28).start(self.hero_image)

    def next_hero_slide(self, *_args):
        self.show_hero_slide(self.hero_index + 1)

    def previous_hero_slide(self):
        self.show_hero_slide(self.hero_index - 1)

    def open_current_hero(self):
        self.start_booking(HERO_SLIDES[self.hero_index]["event_id"])

    def open_booking_nav(self):
        self.start_booking(self.current_event_id or "NILA-GP")

    def build_events(self):
        screen = Screen(name="events")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        header = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            padding=(dp(16), dp(14)),
            background=COLORS["forest"],
        )
        header.add_widget(label("AGENDA PEMANCINGAN", 20, 9, COLORS["sand"], True))
        header.add_widget(label("Pilih Paket Event", 42, 25, COLORS["white"], True))
        header.add_widget(label("Semua event khusus ikan nila dan memiliki 82 lapak.", 25, 10, COLORS["mint"]))
        content.add_widget(header)

        content.add_widget(section_heading("Filter pelepasan ikan", "Temukan paket sesuai anggaran Anda"))
        filters = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(7))
        self.event_filter_buttons = {}
        for filter_name in ("Semua", "225 KG", "200 KG", "150 KG", "100 KG"):
            chip = GhostButton(text=filter_name, height=dp(36), font_size="10sp")
            chip.bind(on_release=lambda _button, name=filter_name: self.filter_events(name))
            self.event_filter_buttons[filter_name] = chip
            filters.add_widget(chip)
        content.add_widget(filters)

        content.add_widget(section_heading("Event tersedia", "Harga tiket berlaku untuk satu lapak"))
        self.event_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(11))
        self.event_list.bind(minimum_height=self.event_list.setter("height"))
        self.event_cards = {}
        for index, (event_id, event) in enumerate(EVENTS.items()):
            card = self.build_event_card(event_id, event, index)
            self.event_cards[event_id] = card
            self.event_list.add_widget(card)
        content.add_widget(self.event_list)
        self.filter_events("Semua")
        screen.add_widget(scroll)
        return screen

    def build_event_card(self, event_id, event, index):
        accents = (COLORS["sand"], COLORS["sage"], COLORS["sky"], COLORS["coral"])
        card = Card(size_hint_y=None, height=dp(202), padding=dp(10), spacing=dp(11))
        media = BoxLayout(orientation="vertical", size_hint_x=0.36, spacing=dp(5))
        media.add_widget(Image(source=asset(event["image"]), fit_mode="cover"))
        badge = Card(size_hint_y=None, height=dp(27), padding=dp(3), background=accents[index % len(accents)])
        badge.add_widget(label(event["release"].replace("Pelepasan nila ", ""), 21, 10, COLORS["forest"], True, "center"))
        media.add_widget(badge)
        card.add_widget(media)

        details = BoxLayout(orientation="vertical", spacing=dp(1))
        details.add_widget(label("PAKET EVENT NILA", 18, 9, COLORS["terracotta"], True))
        details.add_widget(label(event["title"], 36, 17, COLORS["forest"], True))
        details.add_widget(label(event["date"], 23, 10, COLORS["muted"]))
        details.add_widget(label(event["time"], 22, 10, COLORS["muted"]))
        details.add_widget(label(f'Total {event["quota"]} lapak | 1 tiket per lapak', 24, 10, COLORS["forest"], True))
        price_row = BoxLayout(size_hint_y=None, height=dp(39), spacing=dp(7))
        price_row.add_widget(label(rupiah(event["price"]), 39, 16, COLORS["terracotta"], True))
        choose = PrimaryButton(text="Lihat Detail", height=dp(36), size_hint_x=0.54)
        choose.bind(on_release=lambda _button, eid=event_id: self.open_event_detail(eid))
        price_row.add_widget(choose)
        details.add_widget(price_row)
        card.add_widget(details)
        return card

    def filter_events(self, filter_name):
        if not hasattr(self, "event_list"):
            return
        for name, button in self.event_filter_buttons.items():
            active = name == filter_name
            button.resting_color = COLORS["forest"] if active else COLORS["mint"]
            button.button_color.rgba = button.resting_color
            button.color = COLORS["white"] if active else COLORS["forest"]
        self.event_list.clear_widgets()
        for event_id, event in EVENTS.items():
            release_amount = event["release"].replace("Pelepasan nila ", "").upper()
            if filter_name == "Semua" or release_amount == filter_name:
                self.event_list.add_widget(self.event_cards[event_id])

    def build_event_detail(self):
        screen = Screen(name="event_detail")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        back = GhostButton(text="< Kembali ke jadwal", size_hint_x=0.55, height=dp(38))
        back.bind(on_release=lambda *_: self.go("events"))
        content.add_widget(back)

        detail_media = Card(size_hint_y=None, height=dp(232), padding=dp(6), background=COLORS["deep_forest"])
        self.detail_image = Image(fit_mode="cover")
        detail_media.add_widget(self.detail_image)
        content.add_widget(detail_media)
        content.add_widget(label("PAKET EVENT KHUSUS NILA", 22, 9, COLORS["terracotta"], True))
        self.detail_title = label("Detail event", 42, 23, COLORS["forest"], True)
        self.detail_schedule = label("-", 52, 12, COLORS["muted"])
        content.add_widget(self.detail_title)
        content.add_widget(self.detail_schedule)

        content.add_widget(section_heading("Ringkasan paket", "Informasi utama sebelum memilih lapak"))
        facts = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        self.detail_release = self.fact_card("PELEPASAN", "-", COLORS["mint"])
        self.detail_quota = self.fact_card("TOTAL LAPAK", "-", COLORS["sand"])
        self.detail_price = self.fact_card("HARGA", "-", COLORS["sky"])
        facts.add_widget(self.detail_release)
        facts.add_widget(self.detail_quota)
        facts.add_widget(self.detail_price)
        content.add_widget(facts)

        content.add_widget(section_heading("Termasuk dalam tiket", "Satu tiket berlaku untuk satu pemancing"))
        benefits = BoxLayout(size_hint_y=None, height=dp(92), spacing=dp(8))
        for value, caption, background in (
            ("1", "Lapak pilihan", COLORS["mint"]),
            ("1", "Tiket digital", COLORS["sky"]),
            ("60 mnt", "Check-in awal", COLORS["sand"]),
        ):
            benefit = Card(orientation="vertical", padding=dp(8), background=background)
            benefit.add_widget(label(value, 34, 17, COLORS["forest"], True, "center"))
            benefit.add_widget(label(caption, 25, 9, COLORS["muted"], False, "center"))
            benefits.add_widget(benefit)
        content.add_widget(benefits)

        content.add_widget(section_heading("Sebelum mendaftar", "Baca ketentuan event dengan teliti"))
        content.add_widget(self.info_card(
            "Tentang event",
            "Kompetisi memancing khusus ikan nila dengan pencatatan hasil tangkapan terberat. Check-in dibuka 60 menit sebelum acara dimulai.",
            145,
        ))
        content.add_widget(self.info_card("Aturan umpan", BAIT_RULE_SHORT, 120, COLORS["sand"]))
        detail_action = PrimaryButton(text="Pilih dari 82 Lapak")
        detail_action.bind(on_release=lambda *_: self.start_booking(self.detail_event_id))
        content.add_widget(detail_action)
        screen.add_widget(scroll)
        return screen

    def fact_card(self, heading, value, background):
        card = Card(orientation="vertical", padding=dp(8), background=background)
        card.add_widget(label(heading, 25, 9, COLORS["muted"], True, "center"))
        card.value_label = label(value, 40, 13, COLORS["forest"], True, "center")
        card.add_widget(card.value_label)
        return card

    def open_event_detail(self, event_id):
        event = EVENTS[event_id]
        self.detail_event_id = event_id
        self.detail_image.source = asset(event["image"])
        self.detail_title.text = event["title"]
        self.detail_schedule.text = f'{event["date"]}\n{event["time"]}'
        self.detail_release.value_label.text = event["release"].replace("Pelepasan nila ", "")
        self.detail_quota.value_label.text = str(event["quota"])
        self.detail_price.value_label.text = rupiah(event["price"]).replace("Rp ", "")
        self.go("event_detail")

    def build_booking(self):
        screen = Screen(name="booking")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        back = GhostButton(text="< Kembali ke detail event", size_hint_x=0.63, height=dp(38))
        back.bind(on_release=lambda *_: self.open_event_detail(self.current_event_id or "NILA-GP"))
        content.add_widget(back)
        content.add_widget(booking_progress(1))

        header = Card(orientation="vertical", size_hint_y=None, height=dp(94), padding=dp(14), background=COLORS["forest"])
        self.spot_event_title = label("Pilih Lapak", 36, 20, COLORS["white"], True)
        self.spot_event_meta = label("-", 28, 10, COLORS["mint"])
        header.add_widget(self.spot_event_title)
        header.add_widget(self.spot_event_meta)
        content.add_widget(header)

        content.add_widget(section_heading("Status lapak", "Pilih tombol hijau yang masih tersedia"))
        legend = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(7))
        for text_value, color in (
            ("Tersedia", COLORS["mint"]),
            ("Terisi", COLORS["coral"]),
            ("Dipilih", COLORS["sky"]),
        ):
            item = Card(background=color, padding=dp(4))
            item.add_widget(label(text_value, 28, 9, COLORS["forest"], True, "center"))
            legend.add_widget(item)
        content.add_widget(legend)

        content.add_widget(section_heading("Denah kolam", "Nomor lapak 01 sampai 82"))
        pond = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(555),
            padding=dp(13),
            spacing=dp(9),
            background=COLORS["deep_forest"],
        )
        pond.add_widget(label("DENAH KOLAM UTAMA - 82 LAPAK", 26, 11, COLORS["sand"], True, "center"))
        water = Card(size_hint_y=None, height=dp(82), padding=dp(10), background=(0.19, 0.53, 0.59, 1))
        water.add_widget(label("KOLAM NILA\nArea pelepasan ikan", 64, 15, COLORS["white"], True, "center"))
        pond.add_widget(water)
        self.spot_grid = GridLayout(cols=10, spacing=dp(5), size_hint_y=None, height=dp(360))
        self.spot_buttons = {}
        self.occupied_spots = set()
        for spot_number in range(1, 83):
            occupied = spot_number in self.occupied_spots
            button = SpotButton(spot_number)
            button.set_status("occupied" if occupied else "available")
            button.bind(on_release=lambda _button, number=spot_number: self.select_spot(number))
            self.spot_buttons[spot_number] = button
            self.spot_grid.add_widget(button)
        pond.add_widget(self.spot_grid)
        content.add_widget(pond)

        content.add_widget(section_heading("Pilihan Anda", "Periksa nomor lapak sebelum lanjut"))
        summary = Card(size_hint_y=None, height=dp(74), padding=dp(12), spacing=dp(8), background=COLORS["white"])
        self.selected_spot_label = label("Belum memilih lapak", 45, 13, COLORS["muted"], True)
        self.spot_price_label = label("Rp 0", 45, 16, COLORS["terracotta"], True, "right")
        summary.add_widget(self.selected_spot_label)
        summary.add_widget(self.spot_price_label)
        content.add_widget(summary)
        continue_button = PrimaryButton(text="Lanjut Isi Data Pemesan")
        continue_button.bind(on_release=lambda *_: self.continue_to_booking_data())
        content.add_widget(continue_button)
        screen.add_widget(scroll)
        return screen

    def build_booking_data(self):
        screen = Screen(name="booking_data")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        back = GhostButton(text="< Kembali pilih lapak", size_hint_x=0.62)
        back.bind(on_release=lambda *_: self.go("booking"))
        content.add_widget(back)
        content.add_widget(booking_progress(2))
        booking_media = Card(size_hint_y=None, height=dp(205), padding=dp(6), background=COLORS["deep_forest"])
        self.booking_image = Image(fit_mode="cover")
        booking_media.add_widget(self.booking_image)
        content.add_widget(booking_media)
        self.booking_title = label("Pilih event", 40, 22, COLORS["forest"], True)
        self.booking_schedule = label("-", 48, 13, COLORS["muted"])
        self.booking_release = label("-", 30, 13, COLORS["terracotta"], True)
        content.add_widget(self.booking_title)
        content.add_widget(self.booking_schedule)
        content.add_widget(self.booking_release)

        content.add_widget(section_heading("Data pemesan", "Tiket akan dicatat menggunakan informasi ini"))
        content.add_widget(label("Nama pemesan", 24, 13, COLORS["ink"], True))
        self.customer_name = StyledTextInput(
            hint_text="Contoh: Budi Santoso",
            multiline=False,
        )
        content.add_widget(self.customer_name)
        content.add_widget(label("Nomor WhatsApp", 24, 13, COLORS["ink"], True))
        self.customer_phone = StyledTextInput(
            hint_text="08xxxxxxxxxx",
            multiline=False,
            input_filter="int",
        )
        content.add_widget(self.customer_phone)

        selected_card = Card(size_hint_y=None, height=dp(72), padding=dp(12), background=COLORS["mint"])
        self.data_spot_label = label("Lapak -", 45, 14, COLORS["forest"], True)
        selected_card.add_widget(self.data_spot_label)
        selected_card.add_widget(label("1 tiket", 45, 12, COLORS["muted"], False, "right"))
        content.add_widget(selected_card)

        content.add_widget(section_heading("Persetujuan aturan", "Wajib disetujui sebelum pembayaran"))
        rule_card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(158),
            padding=dp(14),
            spacing=dp(6),
            background=COLORS["sand"],
        )
        rule_card.add_widget(label("Persetujuan aturan umpan", 28, 15, COLORS["forest"], True))
        rule_card.add_widget(label(BAIT_RULE_SHORT, 58, 12, COLORS["muted"]))
        accept_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
        self.bait_checkbox = CheckBox(
            size_hint_x=None, width=dp(38), color=COLORS["terracotta"]
        )
        accept_row.add_widget(self.bait_checkbox)
        accept_row.add_widget(label("Saya memahami dan menyetujui aturan.", 38, 12, COLORS["ink"], True))
        rule_card.add_widget(accept_row)
        content.add_widget(rule_card)

        submit = PrimaryButton(text="Lanjut ke Pembayaran")
        submit.bind(on_release=lambda *_: self.continue_to_payment())
        content.add_widget(submit)
        screen.add_widget(scroll)
        return screen

    def build_payment(self):
        screen = Screen(name="payment")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        back = GhostButton(text="< Kembali isi data", size_hint_x=0.55, height=dp(38))
        back.bind(on_release=lambda *_: self.go("booking_data"))
        content.add_widget(back)
        content.add_widget(booking_progress(3))
        header = Card(orientation="vertical", size_hint_y=None, height=dp(92), padding=dp(14), background=COLORS["forest"])
        header.add_widget(label("Ringkasan Pembayaran", 38, 21, COLORS["white"], True))
        header.add_widget(label("Periksa pesanan sebelum menerbitkan tiket", 26, 10, COLORS["mint"]))
        content.add_widget(header)

        content.add_widget(section_heading("Pesanan Anda", "Pastikan event dan lapak sudah benar"))
        order = Card(orientation="vertical", size_hint_y=None, height=dp(180), padding=dp(14), spacing=dp(4))
        self.payment_event_label = label("-", 36, 17, COLORS["forest"], True)
        self.payment_spot_label = label("Lapak -", 28, 12, COLORS["terracotta"], True)
        self.payment_customer_label = label("-", 28, 11, COLORS["muted"])
        self.payment_schedule_label = label("-", 42, 11, COLORS["muted"])
        order.add_widget(self.payment_event_label)
        order.add_widget(self.payment_spot_label)
        order.add_widget(self.payment_customer_label)
        order.add_widget(self.payment_schedule_label)
        content.add_widget(order)

        content.add_widget(section_heading("Metode pembayaran", "Pilih cara pembayaran yang paling nyaman"))
        self.payment_method = StyledSpinner(
            text="QRIS / GoPay / OVO",
            values=("QRIS / GoPay / OVO", "Transfer Bank BCA", "Transfer Bank Mandiri", "Bayar di lokasi"),
        )
        self.payment_method.bind(text=lambda *_: self.update_payment_total())
        content.add_widget(self.payment_method)

        payment_note = Card(size_hint_y=None, height=dp(68), padding=dp(11), background=COLORS["mint"])
        payment_note.add_widget(label("QRIS & E-WALLET", 42, 10, COLORS["forest"], True))
        payment_note.add_widget(label("BANK TRANSFER", 42, 10, COLORS["forest"], True, "center"))
        payment_note.add_widget(label("BAYAR DI LOKASI", 42, 10, COLORS["forest"], True, "right"))
        content.add_widget(payment_note)

        content.add_widget(section_heading("Rincian biaya", "Transparan tanpa biaya tersembunyi"))
        breakdown = Card(orientation="vertical", size_hint_y=None, height=dp(156), padding=dp(14), spacing=dp(3), background=COLORS["white"])
        self.payment_ticket_price = label("Tiket: Rp 0", 30, 12, COLORS["muted"])
        self.payment_fee = label("Biaya layanan: Rp 2.500", 30, 12, COLORS["muted"])
        self.payment_total_label = label("Total: Rp 0", 45, 21, COLORS["forest"], True)
        breakdown.add_widget(self.payment_ticket_price)
        breakdown.add_widget(self.payment_fee)
        breakdown.add_widget(self.payment_total_label)
        content.add_widget(breakdown)
        content.add_widget(label("Pembayaran pada MVP disimulasikan. Integrasi payment gateway dilakukan pada fase produksi.", 54, 10, COLORS["muted"], False, "center"))
        pay_button = PrimaryButton(text="Bayar & Terbitkan Tiket")
        pay_button.bind(on_release=lambda *_: self.submit_booking())
        content.add_widget(pay_button)
        screen.add_widget(scroll)
        return screen

    def build_ticket(self):
        screen = Screen(name="ticket")
        layout = BoxLayout(
            orientation="vertical", padding=(dp(16), dp(12)), spacing=dp(10)
        )
        layout.add_widget(booking_progress(4))
        layout.add_widget(label("TIKET BERHASIL DIBUAT", 26, 11, COLORS["terracotta"], True, "center"))
        ticket_card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(438),
            padding=dp(16),
            spacing=dp(5),
            background=COLORS["deep_forest"],
        )
        ticket_brand = BoxLayout(size_hint_y=None, height=dp(24))
        ticket_brand.add_widget(label("NILA KEDIRI", 24, 11, COLORS["sand"], True))
        ticket_brand.add_widget(label("E-TICKET", 24, 9, COLORS["mint"], True, "right"))
        ticket_card.add_widget(ticket_brand)
        self.ticket_event = label("-", 42, 19, COLORS["white"], True, "center")
        self.ticket_code = label("-", 36, 22, COLORS["white"], True, "center")
        self.ticket_qr = TicketMatrix(size_hint_y=None, height=dp(138))
        self.ticket_detail = label("-", 68, 11, (0.9, 0.94, 0.88, 1), False, "center")
        self.ticket_status = label("MENUNGGU PEMBAYARAN", 34, 11, COLORS["sand"], True, "center")
        ticket_card.add_widget(self.ticket_event)
        ticket_card.add_widget(self.ticket_qr)
        ticket_card.add_widget(label("KODE BOOKING", 20, 9, COLORS["sand"], True, "center"))
        ticket_card.add_widget(self.ticket_code)
        ticket_card.add_widget(self.ticket_detail)
        ticket_card.add_widget(self.ticket_status)
        layout.add_widget(ticket_card)
        layout.add_widget(
            label(
                "Tunjukkan kode booking kepada petugas saat check-in. Pesanan tersimpan di perangkat ini.",
                48,
                10,
                COLORS["muted"],
                False,
                "center",
            )
        )
        ticket_actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        orders_button = GhostButton(text="Pesanan Saya", height=dp(44))
        orders_button.bind(on_release=lambda *_: self.go("orders"))
        home_button = PrimaryButton(text="Ke Beranda", height=dp(44))
        home_button.bind(on_release=lambda *_: self.go("home"))
        ticket_actions.add_widget(orders_button)
        ticket_actions.add_widget(home_button)
        layout.add_widget(ticket_actions)
        screen.add_widget(layout)
        return screen

    def build_gallery(self):
        screen = Screen(name="gallery")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        header = Card(orientation="vertical", size_hint_y=None, height=dp(112), padding=dp(14), background=COLORS["forest"])
        header.add_widget(label("CERITA DARI KOLAM", 18, 8, COLORS["sand"], True))
        header.add_widget(label("Galeri & Komunitas", 38, 22, COLORS["white"], True))
        header.add_widget(label("Momen strike, juara, dan kabar terbaru", 24, 10, COLORS["mint"]))
        content.add_widget(header)
        community_actions = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(7))
        for title, target in (("Leaderboard", "leaderboard"), ("Berita", "news"), ("Status Hari Ini", "daily_status")):
            action = GhostButton(text=title, height=dp(40), font_size="10sp")
            action.bind(on_release=lambda _button, name=target: self.go(name))
            community_actions.add_widget(action)
        content.add_widget(community_actions)
        items = (
            ("gallery-nila.png", "Tangkapan nila terbaik pekan ini", "Arif - Nila 4,8 kg | Lapak 17"),
            ("event-nila.png", "Keseruan Grand Mix Babaon", "Pelepasan 225 kg nila dengan 82 lapak"),
            ("carousel-night-nila.png", "Event Nila 150 KG", "Suasana event malam bersama komunitas"),
        )
        for filename, title, subtitle in items:
            card = Card(
                orientation="vertical",
                size_hint_y=None,
                height=dp(382),
                padding=dp(10),
                spacing=dp(7),
            )
            card.add_widget(
                Image(
                    source=asset(filename),
                    fit_mode="cover",
                )
            )
            card.add_widget(label("MOMEN KOMUNITAS NILA", 18, 9, COLORS["terracotta"], True))
            card.add_widget(label(title, 34, 18, COLORS["forest"], True))
            card.add_widget(label(subtitle, 26, 12, COLORS["muted"]))
            content.add_widget(card)
        screen.add_widget(scroll)
        return screen

    def section_header(self, title, subtitle, back_target):
        wrapper = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(146), spacing=dp(7))
        back = GhostButton(text="< Kembali", size_hint_x=0.34, height=dp(34))
        back.bind(on_release=lambda *_: self.go(back_target))
        wrapper.add_widget(back)
        header = Card(orientation="vertical", padding=(dp(14), dp(9)), background=COLORS["forest"])
        header.add_widget(label("NILA KEDIRI", 16, 8, COLORS["sand"], True))
        header.add_widget(label(title, 32, 20, COLORS["white"], True))
        header.add_widget(label(subtitle, 22, 10, COLORS["mint"]))
        wrapper.add_widget(header)
        return wrapper

    def build_leaderboard(self):
        screen = Screen(name="leaderboard")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Leaderboard Nila", "Hasil tangkapan terberat bulan ini", "gallery"))
        podium = BoxLayout(size_hint_y=None, height=dp(130), spacing=dp(8))
        for rank, name, weight, background in (
            ("2", "Dimas", "4,3 kg", COLORS["sky"]),
            ("1", "Arif", "4,8 kg", COLORS["sand"]),
            ("3", "Rian", "4,1 kg", COLORS["coral"]),
        ):
            card = Card(orientation="vertical", padding=dp(8), background=background)
            card.add_widget(label(f"JUARA {rank}", 25, 10, COLORS["forest"], True, "center"))
            card.add_widget(label(name, 34, 16, COLORS["forest"], True, "center"))
            card.add_widget(label(weight, 28, 12, COLORS["muted"], True, "center"))
            podium.add_widget(card)
        content.add_widget(podium)
        content.add_widget(section_heading("Peringkat berikutnya", "Hasil yang sudah diverifikasi panitia"))
        for rank, name, weight, spot in (
            (4, "Budi Santoso", "3,9 kg", "Lapak 08"),
            (5, "Bayu Pratama", "3,7 kg", "Lapak 21"),
            (6, "Wahyu Setiawan", "3,5 kg", "Lapak 14"),
            (7, "Joko Susilo", "3,2 kg", "Lapak 30"),
        ):
            row = Card(size_hint_y=None, height=dp(70), padding=dp(11), spacing=dp(8))
            row.add_widget(label(f"#{rank}", 44, 16, COLORS["terracotta"], True, "center"))
            row.add_widget(label(f"{name}\n{spot}", 48, 12, COLORS["forest"], True))
            row.add_widget(label(weight, 44, 15, COLORS["forest"], True, "right"))
            content.add_widget(row)
        content.add_widget(label("Peringkat diperbarui setelah hasil event diverifikasi panitia.", 45, 10, COLORS["muted"], False, "center"))
        screen.add_widget(scroll)
        return screen

    def build_news(self):
        screen = Screen(name="news")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Berita & Pengumuman", "Kabar terbaru dari kolam nila", "gallery"))
        articles = (
            ("carousel-event-nila.png", "Event segera", "Grand Mix Babaon 225 KG dibuka", "Tersedia 82 lapak dengan tiket Rp100.000. Pelepasan nila dilakukan sebelum event."),
            ("gallery-nila.png", "12 September", "Event Nila 200 KG", "Tiket Rp85.000 per lapak dengan kapasitas total 82 lapak."),
            ("carousel-night-nila.png", "18 September", "Event Nila 150 KG", "Tiket Rp70.000. Siapkan penerangan dan umpan alami terbaik untuk sesi malam."),
            ("venue-nila.png", "26 September", "Event Nila 100 KG", "Tiket Rp50.000 per lapak. Jadwal dan informasi terbaru tersedia di aplikasi."),
        )
        for image_name, category, title, body in articles:
            card = Card(orientation="vertical", size_hint_y=None, height=dp(292), padding=dp(10), spacing=dp(5))
            card.add_widget(Image(source=asset(image_name), fit_mode="cover"))
            card.add_widget(label(category.upper(), 20, 9, COLORS["terracotta"], True))
            card.add_widget(label(title, 31, 16, COLORS["forest"], True))
            card.add_widget(label(body, 48, 10, COLORS["muted"]))
            content.add_widget(card)
        screen.add_widget(scroll)
        return screen

    def build_daily_status(self):
        screen = Screen(name="daily_status")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Status Hari Ini", "Selasa, 1 September 2026", "gallery"))
        hero = Card(orientation="vertical", size_hint_y=None, height=dp(170), padding=dp(16), background=COLORS["sand"])
        hero.add_widget(label("IKAN SEDANG AKTIF", 40, 23, COLORS["forest"], True, "center"))
        hero.add_widget(label("Nafsu makan baik sejak pagi", 30, 12, COLORS["muted"], False, "center"))
        hero.add_widget(label("Rekomendasi: lumut, cacing, atau jagung alami", 42, 11, COLORS["forest"], True, "center"))
        content.add_widget(hero)
        facts = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        for value, caption, background in (
            ("225 kg", "Pelepasan nila", COLORS["mint"]),
            ("27 C", "Berawan", COLORS["sky"]),
            ("06-22", "Jam buka", COLORS["coral"]),
        ):
            fact = Card(orientation="vertical", padding=dp(8), background=background)
            fact.add_widget(label(value, 38, 17, COLORS["forest"], True, "center"))
            fact.add_widget(label(caption, 28, 9, COLORS["muted"], False, "center"))
            facts.add_widget(fact)
        content.add_widget(facts)
        content.add_widget(self.info_card("Catatan petugas", "Air kolam stabil dan ikan aktif di sisi timur sejak pukul 07.30. Hindari racikan terlalu manis pada sesi siang.", 140))
        content.add_widget(self.info_card("Aturan tetap berlaku", BAIT_RULE_SHORT, 120, COLORS["sand"]))
        screen.add_widget(scroll)
        return screen

    def build_orders(self):
        screen = Screen(name="orders")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Pesanan Saya", "Tiket yang tersimpan di perangkat ini", "info"))
        self.orders_content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.orders_content.bind(minimum_height=self.orders_content.setter("height"))
        content.add_widget(self.orders_content)
        screen.add_widget(scroll)
        return screen

    def refresh_orders(self):
        self.orders_content.clear_widgets()
        connection = sqlite3.connect(DB_PATH)
        rows = connection.execute(
            "SELECT booking_code, event_id, spot_number, total_amount, payment_status, created_at FROM bookings ORDER BY id DESC LIMIT 20"
        ).fetchall()
        connection.close()
        if not rows:
            self.orders_content.add_widget(self.info_card("Belum ada pesanan", "Tiket yang berhasil dibuat akan muncul di halaman ini.", 125, COLORS["mint"]))
            return
        for code, event_id, spot_number, total, status, created_at in rows:
            event = EVENTS.get(event_id, {"title": event_id})
            status_text = "Bayar saat check-in" if status == "pay_at_venue" else "Menunggu pembayaran"
            card = Card(orientation="vertical", size_hint_y=None, height=dp(138), padding=dp(13), spacing=dp(2))
            card.add_widget(label(event["title"], 30, 15, COLORS["forest"], True))
            card.add_widget(label(f"{code} | Lapak {spot_number or '-'}", 25, 11, COLORS["terracotta"], True))
            card.add_widget(label(f"{rupiah(total)} | {status_text}", 25, 11, COLORS["muted"]))
            card.add_widget(label(created_at.replace("T", " "), 22, 9, COLORS["muted"]))
            self.orders_content.add_widget(card)

    def build_admin(self):
        screen = Screen(name="admin")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Dashboard Admin", "Ringkasan operasional pemancingan", "info"))
        metrics = BoxLayout(size_hint_y=None, height=dp(112), spacing=dp(8))
        for value, caption, background in (
            ("4", "Paket event", COLORS["mint"]),
            ("82", "Total lapak", COLORS["sky"]),
            ("675 kg", "Total 4 paket", COLORS["sand"]),
        ):
            metric = Card(orientation="vertical", padding=dp(8), background=background)
            metric.add_widget(label(value, 42, 18, COLORS["forest"], True, "center"))
            metric.add_widget(label(caption, 30, 9, COLORS["muted"], False, "center"))
            metrics.add_widget(metric)
        content.add_widget(metrics)
        content.add_widget(section_heading("Akses pengelolaan", "Pilih data operasional yang akan diperbarui"))
        for title, subtitle, action in (
            ("Kelola Operasional", "Jam buka, mood ikan, dan pelepasan nila", lambda: self.go("operations")),
            ("Lihat Pesanan", "Pantau booking yang masuk di perangkat", lambda: self.go("orders")),
            ("Kelola Event", "Fitur editor event pada iterasi berikutnya", lambda: self.show_message("Tahap berikutnya", "Editor event akan dihubungkan ke database pada iterasi selanjutnya.")),
            ("Kelola Galeri & Berita", "Fitur unggah konten pada iterasi berikutnya", lambda: self.show_message("Tahap berikutnya", "Unggah konten akan ditambahkan setelah sistem akun admin.")),
        ):
            card = Card(size_hint_y=None, height=dp(82), padding=dp(11), spacing=dp(8))
            copy = BoxLayout(orientation="vertical")
            copy.add_widget(label(title, 30, 14, COLORS["forest"], True))
            copy.add_widget(label(subtitle, 28, 9, COLORS["muted"]))
            card.add_widget(copy)
            button = PrimaryButton(text="Buka", size_hint_x=None, width=dp(70), height=dp(38))
            button.bind(on_release=lambda _button, callback=action: callback())
            card.add_widget(button)
            content.add_widget(card)
        screen.add_widget(scroll)
        return screen

    def build_operations(self):
        screen = Screen(name="operations")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kelola Operasional", "Perbarui informasi harian kolam", "admin"))
        content.add_widget(section_heading("Status publik", "Informasi ini akan dilihat oleh pengunjung"))
        content.add_widget(label("Status pemancingan", 28, 13, COLORS["forest"], True))
        self.operation_status = StyledSpinner(text="Buka", values=("Buka", "Tutup sementara"))
        content.add_widget(self.operation_status)
        content.add_widget(label("Mood ikan nila", 28, 13, COLORS["forest"], True))
        self.operation_mood = StyledSpinner(text="Aktif / nafsu makan", values=("Aktif / nafsu makan", "Biasa", "Kurang aktif"))
        content.add_widget(self.operation_mood)
        content.add_widget(section_heading("Catatan lapangan", "Perbarui jumlah tebar dan kondisi kolam"))
        content.add_widget(label("Jumlah pelepasan hari ini (kg)", 28, 13, COLORS["forest"], True))
        self.operation_release = StyledTextInput(text="225", multiline=False, input_filter="int")
        content.add_widget(self.operation_release)
        content.add_widget(label("Catatan petugas", 28, 13, COLORS["forest"], True))
        self.operation_note = StyledTextInput(text="Ikan aktif di sisi timur sejak pagi.", multiline=True, height=dp(105))
        content.add_widget(self.operation_note)
        save = PrimaryButton(text="Simpan Informasi Harian")
        save.bind(on_release=lambda *_: self.save_operations())
        content.add_widget(save)
        screen.add_widget(scroll)
        return screen

    def save_operations(self):
        release = self.operation_release.text.strip() or "0"
        self.show_message("Informasi disimpan", f"Status {self.operation_status.text}, mood {self.operation_mood.text}, pelepasan {release} kg nila.")

    def build_info(self):
        screen = Screen(name="info")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        header = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            padding=(dp(16), dp(12)),
            background=COLORS["forest"],
        )
        header.add_widget(label("PANDUAN PENGUNJUNG", 18, 8, COLORS["sand"], True))
        header.add_widget(label("Informasi Pemancingan", 38, 22, COLORS["white"], True))
        header.add_widget(label("Semua yang perlu disiapkan sebelum datang", 24, 10, COLORS["mint"]))
        content.add_widget(header)
        venue_media = Card(size_hint_y=None, height=dp(232), padding=dp(6), background=COLORS["deep_forest"])
        venue_media.add_widget(Image(source=asset("venue-nila.png"), fit_mode="cover"))
        content.add_widget(venue_media)

        overview = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        for value, caption, background in (
            ("06-22", "Buka setiap hari", COLORS["mint"]),
            ("AKTIF", "Mood nila", COLORS["sand"]),
            ("27 C", "Berawan", COLORS["sky"]),
        ):
            fact = Card(orientation="vertical", padding=dp(9), background=background)
            fact.add_widget(label(value, 38, 17, COLORS["forest"], True, "center"))
            fact.add_widget(label(caption, 26, 9, COLORS["muted"], False, "center"))
            overview.add_widget(fact)
        content.add_widget(overview)

        content.add_widget(self.info_card("Kolam khusus ikan nila", "Seluruh kolam, event, pelepasan ikan, dan hasil tangkapan di aplikasi ini khusus ikan nila.", 125))
        content.add_widget(self.info_card("Rekomendasi hari ini", "Nila sedang aktif. Gunakan lumut, cacing, jagung, singkong, kroto, atau racikan bahan pangan alami.", 135, COLORS["mint"]))
        content.add_widget(self.info_card("Peraturan umpan", BAIT_RULE_FULL, 230, COLORS["sand"]))

        content.add_widget(section_heading("Fasilitas", "Kebutuhan dasar tersedia di area kolam"))
        facilities = BoxLayout(size_hint_y=None, height=dp(92), spacing=dp(8))
        for name in ("Parkir\nmotor/mobil", "Musala &\ntoilet", "Kantin &\numpan alami"):
            facility = Card(background=COLORS["white"], padding=dp(8))
            facility.add_widget(label(name, 65, 11, COLORS["forest"], True, "center"))
            facilities.add_widget(facility)
        content.add_widget(facilities)

        location = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(230),
            padding=dp(16),
            spacing=dp(8),
            background=COLORS["deep_forest"],
        )
        location.add_widget(label("LOKASI RESMI", 22, 9, COLORS["sand"], True))
        location.add_widget(label("Petunjuk Google Maps", 34, 18, COLORS["white"], True))
        location.add_widget(
            label(
                "Gunakan titik resmi pemancingan untuk melihat rute terkini dari pusat Kota Kediri atau dari posisi Anda. Petunjuk akan dibuka langsung di Google Maps.",
                82,
                11,
                COLORS["mint"],
            )
        )
        map_button = PrimaryButton(text="Buka Lokasi Resmi di Google Maps")
        map_button.bind(on_release=lambda *_: self.open_map())
        location.add_widget(map_button)
        content.add_widget(location)
        content.add_widget(
            self.info_card(
                "Peraturan umum",
                "1. Satu joran untuk satu tiket.\n2. Jaga kebersihan lapak.\n3. Dilarang mengganggu lapak lain.\n4. Keputusan panitia event bersifat final.\n5. Ikan dan area lomba hanya khusus nila.",
                180,
            )
        )
        content.add_widget(section_heading("Menu lainnya", "Status, pesanan, dan akses pengelola"))
        more_menu = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(7))
        for title, target in (("Status", "daily_status"), ("Pesanan", "orders"), ("Admin", "admin")):
            menu_button = GhostButton(text=title, height=dp(44))
            menu_button.bind(on_release=lambda _button, name=target: self.go(name))
            more_menu.add_widget(menu_button)
        content.add_widget(more_menu)
        screen.add_widget(scroll)
        return screen

    def info_card(self, title, body, height, background=None):
        card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(height),
            padding=dp(16),
            spacing=dp(6),
            background=background or COLORS["white"],
        )
        card.add_widget(label(title, 34, 18, COLORS["forest"], True))
        card.add_widget(label(body, dp(height - 60), 12, COLORS["muted"]))
        return card

    def go(self, screen_name):
        if screen_name == "orders":
            self.refresh_orders()
        self.manager.current = screen_name
        if hasattr(self, "nav_buttons"):
            for name, button in self.nav_buttons.items():
                active = name == screen_name
                button.set_active(active)

    def on_stop(self):
        if hasattr(self, "hero_clock"):
            self.hero_clock.cancel()

    def start_booking(self, event_id):
        event = EVENTS[event_id]
        self.current_event_id = event_id
        self.selected_spot = None
        connection = sqlite3.connect(DB_PATH)
        booked_spots = connection.execute(
            "SELECT spot_number FROM bookings WHERE event_id = ? AND spot_number IS NOT NULL AND payment_status != 'cancelled'",
            (event_id,),
        ).fetchall()
        connection.close()
        self.occupied_spots = {
            spot_number for (spot_number,) in booked_spots if 1 <= spot_number <= 82
        }
        remaining_spots = 82 - len(self.occupied_spots)
        self.spot_event_title.text = event["title"]
        self.spot_event_meta.text = f'{event["date"]} | {rupiah(event["price"])} | {remaining_spots}/82 tersedia'
        self.selected_spot_label.text = "Belum memilih lapak"
        self.spot_price_label.text = rupiah(event["price"])
        for number, button in self.spot_buttons.items():
            button.set_status("occupied" if number in self.occupied_spots else "available")
        self.booking_image.source = asset(event["image"])
        self.booking_title.text = event["title"]
        self.booking_schedule.text = f'{event["date"]}\n{event["time"]}'
        self.booking_release.text = event["release"]
        self.bait_checkbox.active = False
        self.go("booking")

    def select_spot(self, spot_number):
        if spot_number in self.occupied_spots:
            return
        if self.selected_spot:
            self.spot_buttons[self.selected_spot].set_status("available")
        self.selected_spot = spot_number
        self.spot_buttons[spot_number].set_status("selected")
        self.selected_spot_label.text = f"Lapak dipilih: {spot_number:02d}"

    def continue_to_booking_data(self):
        if not self.selected_spot:
            self.show_message("Pilih lapak", "Pilih satu lapak berwarna hijau sebelum melanjutkan.")
            return
        self.data_spot_label.text = f"Lapak {self.selected_spot:02d}"
        self.go("booking_data")

    def continue_to_payment(self):
        name = self.customer_name.text.strip()
        phone = self.customer_phone.text.strip()
        if len(name) < 3 or len(phone) < 9:
            self.show_message("Data belum lengkap", "Isi nama dan nomor WhatsApp yang valid.")
            return
        if not self.bait_checkbox.active:
            self.show_message("Aturan belum disetujui", "Setujui aturan umpan alami sebelum melanjutkan.")
            return
        event = EVENTS[self.current_event_id]
        self.payment_event_label.text = event["title"]
        self.payment_spot_label.text = f"Lapak {self.selected_spot:02d} | 1 tiket"
        self.payment_customer_label.text = f"Pemesan: {name} | {phone}"
        self.payment_schedule_label.text = f'{event["date"]}\n{event["time"]}'
        self.payment_ticket_price.text = f'Tiket: {rupiah(event["price"])}'
        self.update_payment_total()
        self.go("payment")

    def update_payment_total(self):
        if not self.current_event_id:
            return
        fee = 0 if self.payment_method.text == "Bayar di lokasi" else 2_500
        price = EVENTS[self.current_event_id]["price"]
        self.payment_fee.text = f"Biaya layanan: {rupiah(fee)}"
        self.payment_total_label.text = f"Total: {rupiah(price + fee)}"

    def submit_booking(self):
        name = self.customer_name.text.strip()
        phone = self.customer_phone.text.strip()
        event = EVENTS[self.current_event_id]

        booking_code = "PN-" + uuid4().hex[:6].upper()
        method = self.payment_method.text
        fee = 0 if method == "Bayar di lokasi" else 2_500
        total = event["price"] + fee
        status = "pay_at_venue" if method == "Bayar di lokasi" else "pending"
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO bookings (
                    booking_code, event_id, customer_name, customer_phone,
                    ticket_count, payment_method, total_amount, payment_status,
                    spot_number, bait_rule_accepted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    booking_code,
                    self.current_event_id,
                    name,
                    phone,
                    1,
                    method,
                    total,
                    status,
                    self.selected_spot,
                    1,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

        self.ticket_event.text = event["title"]
        self.ticket_code.text = booking_code
        self.ticket_qr.set_code(booking_code)
        self.ticket_detail.text = f'{event["date"]}\nLapak {self.selected_spot:02d} | {rupiah(total)}\n{method}'
        self.ticket_status.text = (
            "BAYAR SAAT CHECK-IN" if status == "pay_at_venue" else "MENUNGGU PEMBAYARAN"
        )
        self.customer_name.text = ""
        self.customer_phone.text = ""
        self.go("ticket")

    def open_map(self):
        webbrowser.open(GOOGLE_MAPS_URL)

    def show_message(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        content.add_widget(label(message, 90, 13, COLORS["ink"], False, "center"))
        close_button = PrimaryButton(text="Mengerti")
        content.add_widget(close_button)
        popup = Popup(title=title, content=content, size_hint=(0.84, None), height=dp(235))
        close_button.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    FishingMVPApp().run()
