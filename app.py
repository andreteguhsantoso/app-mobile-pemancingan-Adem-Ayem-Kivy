import hashlib
import hmac
import os
import shutil
import sqlite3
import sys
import webbrowser
from datetime import datetime
from uuid import uuid4

os.environ.setdefault("KIVY_HOME", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".kivy"))

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, InstructionGroup, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import platform as kivy_platform

from database import (
    AccountExistsError,
    BookingConflictError,
    BookingDatabase,
    BookingStateError,
    PasswordError,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets", "generated")
DB_PATH = os.path.join(BASE_DIR, "mvp.db")
GOOGLE_MAPS_URL = "https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7"
APP_VERSION = "1.1.0"
WINDOWS_FONT_DIR = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")


def system_font(filename, fallback="Roboto"):
    path = os.path.join(WINDOWS_FONT_DIR, filename)
    return path if os.path.exists(path) else fallback


FONT_DISPLAY = system_font("bahnschrift.ttf")
FONT_BODY = system_font("trebuc.ttf")


COLORS = {
    "cream": (0.961, 0.941, 0.89, 1),
    "forest": (0.031, 0.184, 0.2, 1),
    "deep_forest": (0.086, 0.282, 0.294, 1),
    "terracotta": (0.894, 0.318, 0.18, 1),
    "ink": (0.031, 0.184, 0.2, 1),
    "muted": (0.408, 0.478, 0.471, 1),
    "mint": (0.796, 0.902, 0.847, 1),
    "sage": (0.149, 0.482, 0.341, 1),
    "sand": (0.949, 0.757, 0.306, 1),
    "sky": (0.663, 0.843, 0.859, 1),
    "coral": (0.894, 0.318, 0.18, 1),
    "white": (1, 1, 1, 1),
}


HERO_SLIDES = (
    {
        "image": "carousel-event-nila.png",
        "kicker": "EVENT PILIHAN PEKAN INI",
        "title": "Grand Mix Babaon",
        "meta": "06 SEP | 08.00 - 13.00 | Rp100.000",
        "event_id": "NILA-GP",
    },
    {
        "image": "gallery-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Pesta Nila 200 KG",
        "meta": "12 SEP | 15.00 - 20.00 | Rp85.000",
        "event_id": "NILA-200",
    },
    {
        "image": "carousel-night-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Nila Night Strike",
        "meta": "18 SEP | 19.00 - 23.30 | Rp70.000",
        "event_id": "NILA-150",
    },
    {
        "image": "hero-nila.png",
        "kicker": "PAKET EVENT IKAN NILA",
        "title": "Fun Fishing Nila",
        "meta": "27 SEP | 07.00 - 11.30 | Rp50.000",
        "event_id": "NILA-100",
    },
)


EVENTS = {
    "NILA-GP": {
        "title": "Grand Mix Babaon",
        "date": "Minggu, 6 September 2026",
        "time": "08.00 - 13.00 WIB",
        "price": 100_000,
        "quota": 82,
        "available": 14,
        "release": "Pelepasan nila 225 kg",
        "image": "carousel-event-nila.png",
    },
    "NILA-200": {
        "title": "Pesta Nila 200 KG",
        "date": "Sabtu, 12 September 2026",
        "time": "15.00 - 20.00 WIB",
        "price": 85_000,
        "quota": 82,
        "available": 31,
        "release": "Pelepasan nila 200 kg",
        "image": "gallery-nila.png",
    },
    "NILA-150": {
        "title": "Nila Night Strike",
        "date": "Jumat, 18 September 2026",
        "time": "19.00 - 23.30 WIB",
        "price": 70_000,
        "quota": 82,
        "available": 25,
        "release": "Pelepasan nila 150 kg",
        "image": "carousel-night-nila.png",
    },
    "NILA-100": {
        "title": "Fun Fishing Nila",
        "date": "Minggu, 27 September 2026",
        "time": "07.00 - 11.30 WIB",
        "price": 50_000,
        "quota": 82,
        "available": 46,
        "release": "Pelepasan nila 100 kg",
        "image": "hero-nila.png",
    },
}


def seeded_occupied(count, offset):
    ordered = sorted(range(1, 83), key=lambda number: ((number * 29 + offset) % 83, number))
    return set(ordered[:count])


BASE_OCCUPIED = {
    event_id: seeded_occupied(event["quota"] - event["available"], index * 11)
    for index, (event_id, event) in enumerate(EVENTS.items())
}


GALLERY_ITEMS = (
    ("gallery-release.png", "Pelepasan 225 KG Nila", "Event"),
    ("leaderboard-champion.png", "Senyum Sang Juara", "Tangkapan"),
    ("gallery-night-event.png", "Strike di Bawah Lampu", "Event"),
    ("gallery-family.png", "Mancing Bareng Keluarga", "Momen"),
    ("gallery-nila.png", "Nila Pilihan Hari Ini", "Tangkapan"),
    ("venue-nila.png", "Pagi Tenang di Kolam", "Kolam"),
)


LEADERBOARD_ENTRIES = (
    {
        "name": "Satria Wibowo",
        "event": "Grand Mix Babaon",
        "biggest": 3.82,
        "total": 12.4,
        "count": 4,
        "spot": "Lapak 27",
        "image": "leaderboard-champion.png",
        "periods": ("Hari Ini", "Per Event", "Bulanan"),
    },
    {
        "name": "Bayu Prasetyo",
        "event": "Grand Mix Babaon",
        "biggest": 3.45,
        "total": 11.7,
        "count": 4,
        "spot": "Lapak 41",
        "image": "leaderboard-man.png",
        "periods": ("Hari Ini", "Per Event", "Bulanan"),
    },
    {
        "name": "Ayu Lestari",
        "event": "Grand Mix Babaon",
        "biggest": 3.20,
        "total": 9.8,
        "count": 3,
        "spot": "Lapak 08",
        "image": "leaderboard-woman.png",
        "periods": ("Hari Ini", "Per Event", "Bulanan"),
    },
    {
        "name": "Dimas Ardana",
        "event": "Nila Night Strike",
        "biggest": 3.08,
        "total": 14.2,
        "count": 5,
        "spot": "Lapak 63",
        "image": "gallery-night-event.png",
        "periods": ("Per Event", "Bulanan"),
    },
    {
        "name": "Rudi Hartono",
        "event": "Fun Fishing Nila",
        "biggest": 2.94,
        "total": 10.5,
        "count": 4,
        "spot": "Lapak 15",
        "image": "gallery-family.png",
        "periods": ("Per Event", "Bulanan"),
    },
    {
        "name": "Andi Saputra",
        "event": "Mancing Harian",
        "biggest": 2.86,
        "total": 8.7,
        "count": 3,
        "spot": "Lapak 72",
        "image": "gallery-nila.png",
        "periods": ("Bulanan",),
    },
)


NEWS_ITEMS = (
    {
        "category": "Event",
        "title": "Pendaftaran Grand Mix Babaon Sudah Dibuka",
        "summary": "225 kg ikan nila, tiket Rp100.000, dan total 82 lapak.",
        "date": "2 September 2026",
        "badge": "PENDAFTARAN DIBUKA",
        "image": "carousel-event-nila.png",
        "event_id": "NILA-GP",
        "body": (
            "Pemancingan Adem Ayem Dlopo membuka pendaftaran Grand Mix Babaon untuk Minggu, 6 September 2026. Event berlangsung pukul 08.00 sampai 13.00 WIB.",
            "Sebanyak 225 kg ikan nila dilepas untuk dipancing. Satu tiket berlaku untuk satu lapak dari total 82 lapak.",
            "Peserta wajib memakai umpan alami. Essen atau pemanis hanya boleh digunakan sebagai campuran umpan alami.",
        ),
        "facts": "225 KG NILA  |  Rp100.000  |  82 LAPAK",
    },
    {
        "category": "Kolam",
        "title": "Persiapan Pelepasan 225 KG Nila",
        "summary": "Pelepasan dilakukan bertahap agar ikan tersebar merata.",
        "date": "1 September 2026",
        "badge": "DARI KOLAM",
        "image": "gallery-release.png",
        "event_id": None,
        "body": (
            "Tim kolam menyiapkan proses pelepasan ikan nila untuk Grand Mix Babaon. Pelepasan dilakukan bertahap di beberapa titik kolam.",
            "Jumlah ikan yang disiapkan adalah 225 kg dan seluruhnya merupakan ikan nila.",
            "Dokumentasi pelepasan menjadi bagian dari transparansi event Pemancingan Adem Ayem Dlopo.",
        ),
        "facts": "IKAN NILA  |  225 KG  |  PERSIAPAN",
    },
    {
        "category": "Aturan",
        "title": "Panduan Umpan Alami di Kolam Adem Ayem",
        "summary": "Umpan wajib alami; essen atau pemanis hanya sebagai campuran.",
        "date": "31 Agustus 2026",
        "badge": "WAJIB DIBACA",
        "image": "news-natural-bait.png",
        "event_id": None,
        "body": (
            "Semua pemancing wajib menggunakan umpan yang berasal dari bahan alami seperti cacing, jagung, singkong, lumut, nasi, dan adonan alami.",
            "Media umpan non-alami tidak diperbolehkan. Essen atau pemanis boleh digunakan hanya sebagai campuran.",
            "Operator berhak memeriksa umpan untuk menjaga kondisi kolam dan rasa adil bagi semua peserta.",
        ),
        "facts": "BAHAN ALAMI  |  ESSEN BOLEH DICAMPUR  |  NON-ALAMI DILARANG",
    },
    {
        "category": "Pengumuman",
        "title": "Prediksi Agenda Nila Bulan Oktober",
        "summary": "Tanggal, harga, dan jumlah ikan belum final.",
        "date": "29 Agustus 2026",
        "badge": "BELUM FINAL",
        "image": "gallery-family.png",
        "event_id": None,
        "body": (
            "Pengelola sedang menyusun agenda ikan nila untuk bulan Oktober, termasuk sesi keluarga dan event malam.",
            "Informasi ini masih berupa prediksi dan belum dapat dipesan.",
            "Pengumuman resmi akan muncul di Agenda setelah jadwal diselesaikan.",
        ),
        "facts": "OKTOBER 2026  |  PREDIKSI  |  BELUM DIBUKA",
    },
)


BAIT_RULE_SHORT = "Umpan wajib alami. Essen/pemanis boleh hanya sebagai campuran umpan alami."
BAIT_RULE_FULL = (
    "Umpan hanya boleh berasal dari bahan alami, misalnya cacing, lumut, jagung, "
    "singkong, kroto, atau racikan bahan pangan alami. Media, bahan, atau umpan lain "
    "yang tidak berasal dari alam dilarang. Essen dan pemanis diperbolehkan hanya "
    "sebagai campuran pada umpan alami, bukan digunakan sebagai umpan utama."
)


def asset(filename):
    return os.path.join(ASSET_DIR, filename)


def media_source(path):
    """Resolve bundled asset names and admin-uploaded absolute paths."""
    if path and os.path.isabs(path):
        return path
    return asset(path or "brand-adem-ayem-icon.png")


def rupiah(value):
    return "Rp {:,.0f}".format(value).replace(",", ".")


def payment_status_text(status):
    return {
        "paid": "Pembayaran berhasil",
        "pay_at_venue": "Bayar saat check-in",
        "pending": "Menunggu pembayaran",
        "cancelled": "Pesanan dibatalkan",
    }.get(status, status.replace("_", " ").title())


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
        kwargs.setdefault("hint_text_color", (0.408, 0.478, 0.471, 0.72))
        kwargs.setdefault("cursor_color", COLORS["terracotta"])
        kwargs.setdefault("cursor_width", dp(2))
        kwargs.setdefault("selection_color", (0.663, 0.843, 0.859, 0.55))
        kwargs.setdefault("write_tab", False)
        kwargs.setdefault("font_name", FONT_BODY)
        super().__init__(**kwargs)
        # TextInput renders glyphs in canvas.before. Insert the custom field first
        # so its white fill never covers typed text or the hint.
        self.field_background = InstructionGroup()
        self.field_color = Color(*COLORS["white"])
        self.field_rect = RoundedRectangle(
            pos=self.pos, size=self.size, radius=[dp(12)]
        )
        self.field_background.add(self.field_color)
        self.field_background.add(self.field_rect)
        self.canvas.before.insert(0, self.field_background)
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
        self.code = "ADEM-AYEM-DLOPO"
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
    title = "Pemancingan Adem Ayem Dlopo"
    database_path = None

    def build(self):
        Window.clearcolor = COLORS["cream"]
        # Desktop/Linux uses a 1:2 phone preview that still fits a 720 px screen.
        # Android and iOS use the device viewport supplied by the operating system.
        if kivy_platform not in ("android", "ios"):
            Window.size = (390, 844)
        self.icon = asset("brand-adem-ayem-icon.png")
        self.current_event_id = None
        self.hero_index = 0
        database_path = self.database_path
        if not database_path:
            database_path = (
                os.path.join(self.user_data_dir, "mvp.db")
                if kivy_platform in ("android", "ios")
                or getattr(sys, "frozen", False)
                else DB_PATH
            )
        self.database_path = database_path
        self.database = BookingDatabase(database_path)
        self.database.initialize(EVENTS, BASE_OCCUPIED, GALLERY_ITEMS, NEWS_ITEMS)
        self.reload_content_data()
        self.current_user = None
        self.session_bookings = []
        self.pending_booking_event_id = None
        self.orders_admin_mode = False
        self.operational_status = self.database.operational_status()
        self.admin_authenticated = False
        self.selected_spot = None
        self.current_ticket_booking = None

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
        self.manager.add_widget(self.build_news_detail())
        self.manager.add_widget(self.build_daily_status())
        self.manager.add_widget(self.build_orders())
        self.manager.add_widget(self.build_auth())
        self.manager.add_widget(self.build_register())
        self.manager.add_widget(self.build_profile())
        self.manager.add_widget(self.build_edit_profile())
        self.manager.add_widget(self.build_account_security())
        self.manager.add_widget(self.build_admin())
        self.manager.add_widget(self.build_admin_users())
        self.manager.add_widget(self.build_admin_events())
        self.manager.add_widget(self.build_admin_gallery())
        self.manager.add_widget(self.build_admin_news())
        self.manager.add_widget(self.build_operations())
        self.manager.add_widget(self.build_info())
        self.manager.add_widget(self.build_legal())
        root.add_widget(self.manager)
        self.navigation = self.build_navigation()
        root.add_widget(self.navigation)
        self.hero_clock = Clock.schedule_interval(self.next_hero_slide, 5)
        return root

    def reload_content_data(self, refresh_widgets=False):
        global GALLERY_ITEMS, NEWS_ITEMS, HERO_SLIDES
        all_event_rows = self.database.list_events(active_only=False)
        self.all_events = {
            row["event_id"]: {key: value for key, value in row.items() if key != "event_id"}
            for row in all_event_rows
        }
        event_rows = [row for row in all_event_rows if row["is_active"]]
        EVENTS.clear()
        EVENTS.update(
            (row["event_id"], {key: value for key, value in row.items() if key != "event_id"})
            for row in event_rows
        )
        gallery_rows = self.database.list_gallery_items(active_only=True)
        GALLERY_ITEMS = tuple(
            (row["image_path"], row["title"], row["category"])
            for row in gallery_rows
        )
        NEWS_ITEMS = tuple(self.database.list_news_items(active_only=True))
        if event_rows:
            HERO_SLIDES = tuple(
                {
                    "image": event["image"],
                    "kicker": "EVENT TERBARU ADEM AYEM",
                    "title": event["title"],
                    "meta": f'{event["date"]} | {event["time"]} | {rupiah(event["price"])}',
                    "event_id": event["event_id"],
                }
                for event in tuple(reversed(event_rows))[:4]
            )
        if refresh_widgets:
            self.rebuild_event_cards()
            self.filter_gallery("Semua")
            self.filter_news("Semua")
            if HERO_SLIDES and hasattr(self, "hero_image"):
                self.show_hero_slide(0)
            self.refresh_home_content()
            self.refresh_news_featured()

    def first_event_id(self):
        return next(iter(EVENTS), None)

    def event_for(self, event_id):
        return EVENTS.get(event_id) or getattr(self, "all_events", {}).get(event_id)

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
            ("MOMEN\nGaleri", "gallery"),
            ("JUARA\nPeringkat", "leaderboard"),
            ("AKUN\nProfil", "profile"),
        ):
            button = NavButton(
                text=title,
                active=screen_name == "home",
            )
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
        app_bar.add_widget(
            Image(
                source=asset("brand-adem-ayem-icon.png"),
                size_hint_x=None,
                width=dp(46),
                fit_mode="cover",
            )
        )
        brand = BoxLayout(orientation="vertical")
        brand.add_widget(label("ADEM AYEM", 30, 18, COLORS["white"], True))
        brand.add_widget(label("Dlopo | Kolam khusus nila", 22, 9, COLORS["mint"]))
        app_bar.add_widget(brand)
        status = BoxLayout(orientation="vertical", size_hint_x=0.34)
        self.home_status_label = label(
            self.operational_status["venue_status"].upper(),
            25,
            9,
            COLORS["sand"],
            True,
            "right",
        )
        self.home_hours_label = label(
            self.operational_status["opening_hours"],
            25,
            11,
            COLORS["white"],
            True,
            "right",
        )
        status.add_widget(self.home_status_label)
        status.add_widget(self.home_hours_label)
        app_bar.add_widget(status)
        content.add_widget(app_bar)

        announcement = Card(
            size_hint_y=None,
            height=dp(42),
            padding=(dp(12), dp(6)),
            background=COLORS["sand"],
        )
        self.home_event_count = label(f"{len(EVENTS)} PAKET EVENT", 28, 10, COLORS["forest"], True)
        announcement.add_widget(self.home_event_count)
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
            source=media_source(HERO_SLIDES[0]["image"]),
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
        shortcuts.add_widget(self.quick_action("01", "BOOKING\nEVENT", COLORS["terracotta"], lambda: self.go("events")))
        shortcuts.add_widget(self.quick_action("02", "82\nLAPAK", COLORS["sand"], lambda: self.start_booking(self.first_event_id())))
        shortcuts.add_widget(self.quick_action("03", "GALERI\nMOMEN", COLORS["sky"], lambda: self.go("gallery")))
        shortcuts.add_widget(self.quick_action("04", "BUKA\nMAPS", COLORS["mint"], lambda: self.open_map()))
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
        event_date.add_widget(label("EVENT", 42, 14, COLORS["forest"], True, "center"))
        event_date.add_widget(label("BARU", 24, 10, COLORS["forest"], True, "center"))
        next_event.add_widget(event_date)
        event_copy = BoxLayout(orientation="vertical", spacing=dp(1))
        self.home_event_title = label("Grand Mix Babaon", 28, 16, COLORS["forest"], True)
        self.home_event_meta = label("08.00 - 13.00 | Tiket Rp 100.000", 23, 11, COLORS["muted"])
        event_copy.add_widget(self.home_event_title)
        event_copy.add_widget(self.home_event_meta)
        self.home_availability_label = label(
            "14 dari 82 lapak tersisa", 22, 10, COLORS["terracotta"], True
        )
        event_copy.add_widget(self.home_availability_label)
        event_button = PrimaryButton(text="Daftar sekarang", height=dp(34), size_hint_x=0.7)
        event_button.bind(on_release=lambda *_: self.start_booking(self.first_event_id()))
        event_copy.add_widget(event_button)
        next_event.add_widget(event_copy)
        content.add_widget(next_event)

        content.add_widget(section_heading("Terbaru di Adem Ayem", "Kabar resmi dari pengelola kolam"))
        news_card = Card(
            size_hint_y=None,
            height=dp(156),
            padding=dp(9),
            spacing=dp(10),
            background=COLORS["white"],
        )
        self.home_news_image = Image(source=asset("gallery-release.png"), size_hint_x=0.38, fit_mode="cover")
        news_card.add_widget(self.home_news_image)
        news_copy = BoxLayout(orientation="vertical", spacing=dp(2))
        self.home_news_badge = label("PENDAFTARAN DIBUKA", 21, 8, COLORS["terracotta"], True)
        self.home_news_title = label("Grand Mix Babaon siap digelar", 42, 15, COLORS["forest"], True)
        self.home_news_summary = label("225 kg nila | Tiket Rp100.000", 24, 10, COLORS["muted"])
        news_copy.add_widget(self.home_news_badge)
        news_copy.add_widget(self.home_news_title)
        news_copy.add_widget(self.home_news_summary)
        news_button = GhostButton(text="Baca semua kabar", height=dp(35), size_hint_x=0.82)
        news_button.bind(on_release=lambda *_: self.go("news"))
        news_copy.add_widget(news_button)
        news_card.add_widget(news_copy)
        content.add_widget(news_card)

        content.add_widget(section_heading("Kondisi kolam hari ini", "Informasi terbaru dari petugas"))
        stats = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        for value, caption, background in (
            (f'{self.operational_status["daily_release_kg"]} kg', "Nila dilepas", COLORS["mint"]),
            (self.operational_status["fish_mood"].split(" /")[0].upper(), "Mood makan", COLORS["sand"]),
            ("27 C", "Berawan", COLORS["sky"]),
        ):
            stat = Card(orientation="vertical", padding=dp(10), background=background)
            value_label = label(value, 36, 18, COLORS["forest"], True, "center")
            if caption == "Nila dilepas":
                self.home_release_label = value_label
            elif caption == "Mood makan":
                self.home_mood_label = value_label
            stat.add_widget(value_label)
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
        location_copy.add_widget(label("Pemancingan Adem Ayem Dlopo", 36, 14, COLORS["forest"], True))
        location_copy.add_widget(label("Buka rute langsung dari lokasi Anda.", 26, 10, COLORS["muted"]))
        home_map_button = PrimaryButton(text="Buka Maps", height=dp(36), size_hint_x=0.68)
        home_map_button.bind(on_release=lambda *_: self.open_map())
        location_copy.add_widget(home_map_button)
        location_card.add_widget(location_copy)
        content.add_widget(location_card)
        screen.add_widget(scroll)
        self.refresh_home_content()
        return screen

    def refresh_home_content(self):
        if hasattr(self, "home_event_count"):
            self.home_event_count.text = f"{len(EVENTS)} PAKET EVENT"
        event_id = self.first_event_id()
        event = EVENTS.get(event_id) if event_id else None
        if event and hasattr(self, "home_event_title"):
            self.home_event_title.text = event["title"]
            self.home_event_meta.text = f'{event["time"]} | Tiket {rupiah(event["price"])}'
            self.home_availability_label.text = f'{event["available"]} dari {event["quota"]} lapak tersisa'
        if NEWS_ITEMS and hasattr(self, "home_news_title"):
            item = NEWS_ITEMS[0]
            self.home_news_image.source = media_source(item["image"])
            self.home_news_badge.text = item["badge"]
            self.home_news_title.text = item["title"]
            self.home_news_summary.text = item["summary"]

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
        self.hero_image.source = media_source(slide["image"])
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
        self.start_booking(self.current_event_id or self.first_event_id())

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
        self.event_availability_labels = {}
        self.rebuild_event_cards()
        content.add_widget(self.event_list)
        self.filter_events("Semua")
        screen.add_widget(scroll)
        return screen

    def build_event_card(self, event_id, event, index):
        accents = (COLORS["sand"], COLORS["sage"], COLORS["sky"], COLORS["coral"])
        card = Card(size_hint_y=None, height=dp(202), padding=dp(10), spacing=dp(11))
        media = BoxLayout(orientation="vertical", size_hint_x=0.36, spacing=dp(5))
        media.add_widget(Image(source=media_source(event["image"]), fit_mode="cover"))
        badge = Card(size_hint_y=None, height=dp(27), padding=dp(3), background=accents[index % len(accents)])
        badge.add_widget(label(event["release"].replace("Pelepasan nila ", ""), 21, 10, COLORS["forest"], True, "center"))
        media.add_widget(badge)
        card.add_widget(media)

        details = BoxLayout(orientation="vertical", spacing=dp(1))
        details.add_widget(label("PAKET EVENT NILA", 18, 9, COLORS["terracotta"], True))
        details.add_widget(label(event["title"], 36, 17, COLORS["forest"], True))
        details.add_widget(label(event["date"], 23, 10, COLORS["muted"]))
        details.add_widget(label(event["time"], 22, 10, COLORS["muted"]))
        availability_label = label(
            f'{event["available"]} dari {event["quota"]} lapak tersisa',
            24,
            10,
            COLORS["forest"],
            True,
        )
        self.event_availability_labels[event_id] = availability_label
        details.add_widget(availability_label)
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

    def rebuild_event_cards(self):
        if not hasattr(self, "event_list"):
            return
        self.event_cards = {}
        self.event_availability_labels = {}
        self.event_list.clear_widgets()
        for index, (event_id, event) in enumerate(EVENTS.items()):
            self.event_cards[event_id] = self.build_event_card(event_id, event, index)
        if EVENTS:
            self.filter_events("Semua")
        else:
            self.event_list.add_widget(
                self.info_card(
                    "Belum ada event aktif",
                    "Jadwal baru akan tampil setelah diterbitkan oleh admin.",
                    120,
                )
            )

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
        event = EVENTS.get(event_id)
        if not event:
            self.show_message("Event tidak tersedia", "Event ini sudah diarsipkan atau belum diterbitkan.")
            return
        self.detail_event_id = event_id
        self.detail_image.source = media_source(event["image"])
        self.detail_title.text = event["title"]
        self.detail_schedule.text = f'{event["date"]}\n{event["time"]}'
        self.detail_release.value_label.text = event["release"].replace("Pelepasan nila ", "")
        self.detail_quota.value_label.text = f"{self.remaining_spots(event_id)}/{event['quota']}"
        self.detail_price.value_label.text = rupiah(event["price"]).replace("Rp ", "")
        self.go("event_detail")

    def build_booking(self):
        screen = Screen(name="booking")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        back = GhostButton(text="< Kembali ke detail event", size_hint_x=0.63, height=dp(38))
        back.bind(on_release=lambda *_: self.open_event_detail(self.current_event_id or self.first_event_id()))
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
            input_type="text",
        )
        content.add_widget(self.customer_name)
        content.add_widget(label("Nomor WhatsApp", 24, 13, COLORS["ink"], True))
        self.customer_phone = StyledTextInput(
            hint_text="08xxxxxxxxxx",
            multiline=False,
            input_filter="int",
            input_type="number",
        )
        content.add_widget(self.customer_phone)
        content.add_widget(label("Catatan untuk petugas (opsional)", 32, 13, COLORS["ink"], True))
        self.customer_notes = StyledTextInput(
            hint_text="Contoh: datang bersama keluarga",
            multiline=True,
            height=dp(82),
            input_type="text",
        )
        content.add_widget(self.customer_notes)
        self.customer_name.focus_next = self.customer_phone
        self.customer_phone.focus_next = self.customer_notes
        self.customer_name.bind(
            on_text_validate=lambda *_: setattr(self.customer_phone, "focus", True)
        )
        self.customer_phone.bind(
            on_text_validate=lambda *_: setattr(self.customer_notes, "focus", True)
        )

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
        order = Card(orientation="vertical", size_hint_y=None, height=dp(205), padding=dp(14), spacing=dp(4))
        self.payment_event_label = label("-", 36, 17, COLORS["forest"], True)
        self.payment_spot_label = label("Lapak -", 28, 12, COLORS["terracotta"], True)
        self.payment_customer_label = label("-", 28, 11, COLORS["muted"])
        self.payment_schedule_label = label("-", 42, 11, COLORS["muted"])
        self.payment_notes_label = label("Catatan: -", 34, 10, COLORS["muted"])
        order.add_widget(self.payment_event_label)
        order.add_widget(self.payment_spot_label)
        order.add_widget(self.payment_customer_label)
        order.add_widget(self.payment_schedule_label)
        order.add_widget(self.payment_notes_label)
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
        persistence_note = Card(
            size_hint_y=None,
            height=dp(72),
            padding=dp(11),
            spacing=dp(8),
            background=COLORS["sky"],
        )
        persistence_note.add_widget(label("DATA AMAN", 28, 10, COLORS["forest"], True))
        persistence_note.add_widget(
            label(
                "Pesanan dan lapak tersimpan permanen di perangkat ini.",
                52,
                10,
                COLORS["forest"],
                False,
                "right",
            )
        )
        content.add_widget(persistence_note)
        content.add_widget(label("Pembayaran pada MVP masih disimulasikan. Integrasi payment gateway dilakukan pada fase produksi.", 54, 10, COLORS["muted"], False, "center"))
        self.pay_button = PrimaryButton(text="Konfirmasi & Buat Tiket")
        self.pay_button.bind(on_release=lambda *_: self.show_booking_confirmation())
        content.add_widget(self.pay_button)
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
        ticket_brand.add_widget(label("ADEM AYEM DLOPO", 24, 11, COLORS["sand"], True))
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
                "Tunjukkan kode booking kepada petugas saat check-in. Tiket tersimpan dan dapat dibuka kembali.",
                48,
                10,
                COLORS["muted"],
                False,
                "center",
            )
        )
        ticket_actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        orders_button = GhostButton(text="Pesanan Saya", height=dp(44))
        orders_button.bind(on_release=lambda *_: self.open_user_orders())
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
        header = Card(orientation="vertical", size_hint_y=None, height=dp(118), padding=dp(15), background=COLORS["forest"])
        header.add_widget(label("CERITA DARI TEPI KOLAM", 20, 8, COLORS["sand"], True))
        header.add_widget(label("Galeri pemancingan.", 40, 24, COLORS["white"], True))
        header.add_widget(label("Dokumentasi event, tangkapan, momen, dan suasana kolam.", 25, 9, COLORS["mint"]))
        content.add_widget(header)

        featured = Card(orientation="vertical", size_hint_y=None, height=dp(260), padding=dp(7), spacing=dp(5), background=COLORS["deep_forest"])
        featured.add_widget(Image(source=asset("gallery-release.png"), fit_mode="cover"))
        featured.add_widget(label("ALBUM TERBARU", 18, 8, COLORS["sand"], True))
        featured.add_widget(label("Pelepasan ikan sebelum event", 35, 18, COLORS["white"], True))
        content.add_widget(featured)

        content.add_widget(section_heading("Foto pilihan", "Jelajahi momen Pemancingan Adem Ayem Dlopo"))
        filters = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        self.gallery_filter_buttons = {}
        for category in ("Semua", "Event", "Tangkapan", "Momen", "Kolam"):
            button = GhostButton(text=category, height=dp(36), font_size="8sp")
            button.bind(on_release=lambda _button, value=category: self.filter_gallery(value))
            self.gallery_filter_buttons[category] = button
            filters.add_widget(button)
        content.add_widget(filters)

        self.gallery_grid = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, row_default_height=dp(250), row_force_default=True)
        self.gallery_grid.bind(minimum_height=self.gallery_grid.setter("height"))
        content.add_widget(self.gallery_grid)
        self.filter_gallery("Semua")
        screen.add_widget(scroll)
        return screen

    def filter_gallery(self, category):
        if not hasattr(self, "gallery_grid"):
            return
        for name, button in self.gallery_filter_buttons.items():
            active = name == category
            button.resting_color = COLORS["forest"] if active else COLORS["mint"]
            button.button_color.rgba = button.resting_color
            button.color = COLORS["white"] if active else COLORS["forest"]
        self.gallery_grid.clear_widgets()
        for filename, title, item_category in GALLERY_ITEMS:
            if category != "Semua" and item_category != category:
                continue
            card = Card(orientation="vertical", padding=dp(7), spacing=dp(3), background=COLORS["white"])
            card.add_widget(Image(source=media_source(filename), fit_mode="cover"))
            card.add_widget(label(item_category.upper(), 18, 7, COLORS["terracotta"], True))
            card.add_widget(label(title, 34, 11, COLORS["forest"], True))
            open_button = GhostButton(text="Lihat foto", height=dp(30), font_size="8sp")
            open_button.bind(on_release=lambda _button, image_name=filename, caption=title: self.show_photo(image_name, caption))
            card.add_widget(open_button)
            self.gallery_grid.add_widget(card)

    def show_photo(self, filename, caption):
        popup_content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        popup_content.add_widget(Image(source=media_source(filename), fit_mode="contain"))
        popup_content.add_widget(label(caption, 36, 15, COLORS["forest"], True, "center"))
        close_button = PrimaryButton(text="Tutup")
        popup_content.add_widget(close_button)
        popup = Popup(title="Galeri Adem Ayem", content=popup_content, size_hint=(0.94, 0.9))
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def section_header(self, title, subtitle, back_target):
        wrapper = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(146), spacing=dp(7))
        back = GhostButton(text="< Kembali", size_hint_x=0.34, height=dp(34))
        back.bind(on_release=lambda *_: self.go(back_target))
        wrapper.add_widget(back)
        header = Card(orientation="vertical", padding=(dp(14), dp(9)), background=COLORS["forest"])
        header.add_widget(label("ADEM AYEM DLOPO", 16, 8, COLORS["sand"], True))
        header.add_widget(label(title, 32, 20, COLORS["white"], True))
        header.add_widget(label(subtitle, 22, 10, COLORS["mint"]))
        wrapper.add_widget(header)
        return wrapper

    def build_leaderboard(self):
        screen = Screen(name="leaderboard")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        header = Card(orientation="vertical", size_hint_y=None, height=dp(126), padding=dp(15), background=COLORS["forest"])
        header.add_widget(label("REKOR TANGKAPAN NILA", 20, 8, COLORS["sand"], True))
        header.add_widget(label("Papan juara.", 42, 25, COLORS["white"], True))
        header.add_widget(label("Peringkat berdasarkan satu ekor nila paling berat.", 24, 9, COLORS["mint"]))
        content.add_widget(header)

        periods = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        self.leaderboard_period_buttons = {}
        for period in ("Hari Ini", "Per Event", "Bulanan"):
            button = GhostButton(text=period, height=dp(38), font_size="9sp")
            button.bind(on_release=lambda _button, value=period: self.filter_leaderboard(value))
            self.leaderboard_period_buttons[period] = button
            periods.add_widget(button)
        content.add_widget(periods)

        champion = Card(orientation="vertical", size_hint_y=None, height=dp(330), padding=dp(7), spacing=dp(3), background=COLORS["deep_forest"])
        champion.add_widget(Image(source=asset("leaderboard-champion.png"), fit_mode="cover"))
        champion.add_widget(label("#1 REKOR TERBERAT", 18, 8, COLORS["sand"], True))
        champion.add_widget(label("3.82 KG | Satria Wibowo", 35, 20, COLORS["white"], True))
        champion.add_widget(label("Grand Mix Babaon | Lapak 27", 20, 9, COLORS["mint"]))
        content.add_widget(champion)

        summary = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(8))
        self.leaderboard_people = self.fact_card("PEMANCING", "5", COLORS["sand"])
        self.leaderboard_fish = self.fact_card("IKAN TERCATAT", "20", COLORS["mint"])
        summary.add_widget(self.leaderboard_people)
        summary.add_widget(self.leaderboard_fish)
        content.add_widget(summary)
        content.add_widget(section_heading("Rekor nila terbesar", "Semua hasil telah diverifikasi operator"))
        self.leaderboard_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.leaderboard_list.bind(minimum_height=self.leaderboard_list.setter("height"))
        content.add_widget(self.leaderboard_list)
        self.filter_leaderboard("Per Event")
        note = Card(size_hint_y=None, height=dp(84), padding=dp(12), background=COLORS["forest"])
        note.add_widget(label("PENIMBANGAN TRANSPARAN", 58, 10, COLORS["sand"], True))
        note.add_widget(label("Berat dicatat di area operator dan dilengkapi foto tangkapan.", 58, 9, COLORS["mint"]))
        content.add_widget(note)
        screen.add_widget(scroll)
        return screen

    def filter_leaderboard(self, period):
        if not hasattr(self, "leaderboard_list"):
            return
        for name, button in self.leaderboard_period_buttons.items():
            active = name == period
            button.resting_color = COLORS["forest"] if active else COLORS["mint"]
            button.button_color.rgba = button.resting_color
            button.color = COLORS["white"] if active else COLORS["forest"]
        entries = [entry for entry in LEADERBOARD_ENTRIES if period in entry["periods"]]
        self.leaderboard_people.value_label.text = str(len(entries))
        self.leaderboard_fish.value_label.text = str(sum(entry["count"] for entry in entries))
        self.leaderboard_list.clear_widgets()
        for rank, entry in enumerate(entries, start=1):
            row = Card(size_hint_y=None, height=dp(88), padding=dp(8), spacing=dp(8), background=COLORS["white"] if rank > 1 else (1, 0.976, 0.91, 1))
            row.add_widget(label(f"#{rank}", 66, 15, COLORS["terracotta"] if rank > 1 else COLORS["forest"], True, "center"))
            row.add_widget(Image(source=asset(entry["image"]), size_hint_x=None, width=dp(58), fit_mode="cover"))
            copy = BoxLayout(orientation="vertical", spacing=dp(0))
            copy.add_widget(label(entry["name"], 28, 12, COLORS["forest"], True))
            copy.add_widget(label(entry["event"], 20, 8, COLORS["muted"]))
            copy.add_widget(label(f'{entry["count"]} ekor | {entry["total"]:.1f} kg total', 20, 8, COLORS["muted"]))
            row.add_widget(copy)
            row.add_widget(label(f'{entry["biggest"]:.2f}\nKG', 66, 15, COLORS["terracotta"], True, "right"))
            self.leaderboard_list.add_widget(row)

    def build_news(self):
        screen = Screen(name="news")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kabar Adem Ayem", "Pengumuman resmi, kondisi kolam, dan aturan", "home"))

        featured_item = NEWS_ITEMS[0]
        featured = Card(orientation="vertical", size_hint_y=None, height=dp(330), padding=dp(8), spacing=dp(4), background=COLORS["deep_forest"])
        self.news_featured_image = Image(source=media_source(featured_item["image"]), fit_mode="cover")
        self.news_featured_badge = label(featured_item["badge"], 18, 8, COLORS["sand"], True)
        self.news_featured_title = label(featured_item["title"], 50, 19, COLORS["white"], True)
        self.news_featured_summary = label(featured_item["summary"], 34, 9, COLORS["mint"])
        featured.add_widget(self.news_featured_image)
        featured.add_widget(self.news_featured_badge)
        featured.add_widget(self.news_featured_title)
        featured.add_widget(self.news_featured_summary)
        featured_button = PrimaryButton(text="Baca Selengkapnya", height=dp(37), size_hint_x=0.62)
        featured_button.bind(on_release=lambda *_: self.open_news_detail(NEWS_ITEMS[0]))
        featured.add_widget(featured_button)
        content.add_widget(featured)

        content.add_widget(section_heading("Dari pengelola kolam", "Informasi terbaru dan terverifikasi"))
        filters = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        self.news_filter_buttons = {}
        for category in ("Semua", "Event", "Kolam", "Aturan", "Pengumuman"):
            button = GhostButton(text=category, height=dp(36), font_size="8sp")
            button.bind(on_release=lambda _button, value=category: self.filter_news(value))
            self.news_filter_buttons[category] = button
            filters.add_widget(button)
        content.add_widget(filters)
        self.news_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(9))
        self.news_list.bind(minimum_height=self.news_list.setter("height"))
        content.add_widget(self.news_list)
        self.filter_news("Semua")

        official = Card(size_hint_y=None, height=dp(84), padding=dp(12), background=COLORS["forest"])
        official.add_widget(label("SUMBER INFORMASI RESMI", 58, 10, COLORS["sand"], True))
        official.add_widget(label("Perubahan jadwal dianggap resmi jika tampil di aplikasi ini.", 58, 9, COLORS["mint"]))
        content.add_widget(official)
        screen.add_widget(scroll)
        return screen

    def refresh_news_featured(self):
        if not NEWS_ITEMS or not hasattr(self, "news_featured_image"):
            return
        item = NEWS_ITEMS[0]
        self.news_featured_image.source = media_source(item["image"])
        self.news_featured_badge.text = item["badge"]
        self.news_featured_title.text = item["title"]
        self.news_featured_summary.text = item["summary"]

    def filter_news(self, category):
        if not hasattr(self, "news_list"):
            return
        for name, button in self.news_filter_buttons.items():
            active = name == category
            button.resting_color = COLORS["forest"] if active else COLORS["mint"]
            button.button_color.rgba = button.resting_color
            button.color = COLORS["white"] if active else COLORS["forest"]
        self.news_list.clear_widgets()
        for item in NEWS_ITEMS:
            if category != "Semua" and item["category"] != category:
                continue
            card = Card(size_hint_y=None, height=dp(142), padding=dp(8), spacing=dp(9))
            card.add_widget(Image(source=media_source(item["image"]), size_hint_x=0.37, fit_mode="cover"))
            copy = BoxLayout(orientation="vertical", spacing=dp(1))
            copy.add_widget(label(f'{item["category"].upper()} | {item["date"]}', 20, 7, COLORS["terracotta"], True))
            copy.add_widget(label(item["title"], 42, 13, COLORS["forest"], True))
            copy.add_widget(label(item["summary"], 34, 8, COLORS["muted"]))
            button = GhostButton(text="Baca kabar", height=dp(30), size_hint_x=0.58, font_size="8sp")
            button.bind(on_release=lambda _button, article=item: self.open_news_detail(article))
            copy.add_widget(button)
            card.add_widget(copy)
            self.news_list.add_widget(card)

    def build_news_detail(self):
        screen = Screen(name="news_detail")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kabar Resmi", "Pemancingan Adem Ayem Dlopo", "news"))
        media = Card(size_hint_y=None, height=dp(290), padding=dp(6), background=COLORS["deep_forest"])
        self.news_detail_image = Image(fit_mode="cover")
        media.add_widget(self.news_detail_image)
        content.add_widget(media)
        self.news_detail_badge = label("-", 22, 8, COLORS["terracotta"], True)
        self.news_detail_title = label("Kabar", 78, 25, COLORS["forest"], True)
        self.news_detail_summary = label("-", 58, 12, COLORS["muted"])
        self.news_detail_facts = label("-", 58, 10, COLORS["forest"], True, "center")
        content.add_widget(self.news_detail_badge)
        content.add_widget(self.news_detail_title)
        content.add_widget(self.news_detail_summary)
        facts_card = Card(size_hint_y=None, height=dp(76), padding=dp(10), background=COLORS["mint"])
        facts_card.add_widget(self.news_detail_facts)
        content.add_widget(facts_card)
        self.news_detail_body = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.news_detail_body.bind(minimum_height=self.news_detail_body.setter("height"))
        content.add_widget(self.news_detail_body)
        self.news_event_button = PrimaryButton(text="Lihat Detail Event")
        self.news_event_button.bind(on_release=lambda *_: self.open_news_event())
        content.add_widget(self.news_event_button)
        source = Card(size_hint_y=None, height=dp(86), padding=dp(12), background=COLORS["white"])
        source.add_widget(Image(source=asset("brand-adem-ayem-icon.png"), size_hint_x=None, width=dp(58), fit_mode="cover"))
        source.add_widget(label("Pemancingan Adem Ayem Dlopo\nDiterbitkan langsung oleh pengelola.", 60, 10, COLORS["forest"], True))
        content.add_widget(source)
        screen.add_widget(scroll)
        return screen

    def open_news_detail(self, item):
        self.current_news_item = item
        self.news_detail_image.source = media_source(item["image"])
        self.news_detail_badge.text = f'{item["category"].upper()} | {item["date"]} | {item["badge"]}'
        self.news_detail_title.text = item["title"]
        self.news_detail_summary.text = item["summary"]
        self.news_detail_facts.text = item["facts"]
        self.news_detail_body.clear_widgets()
        for paragraph in item["body"]:
            self.news_detail_body.add_widget(label(paragraph, 92, 11, COLORS["ink"]))
        self.news_event_button.height = dp(48) if item["event_id"] else 0
        self.news_event_button.opacity = 1 if item["event_id"] else 0
        self.news_event_button.disabled = not bool(item["event_id"])
        self.go("news_detail")

    def open_news_event(self):
        event_id = getattr(self, "current_news_item", {}).get("event_id")
        if event_id:
            self.open_event_detail(event_id)

    def build_daily_status(self):
        screen = Screen(name="daily_status")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Status Hari Ini", "Kamis, 17 September 2026", "profile"))
        hero = Card(orientation="vertical", size_hint_y=None, height=dp(170), padding=dp(16), background=COLORS["sand"])
        mood = self.operational_status["fish_mood"]
        self.daily_mood_label = label(f"IKAN {mood.upper()}", 44, 21, COLORS["forest"], True, "center")
        self.daily_venue_label = label(f'Status kolam: {self.operational_status["venue_status"]}', 30, 12, COLORS["muted"], False, "center")
        hero.add_widget(self.daily_mood_label)
        hero.add_widget(self.daily_venue_label)
        hero.add_widget(label("Rekomendasi: lumut, cacing, atau jagung alami", 42, 11, COLORS["forest"], True, "center"))
        content.add_widget(hero)
        facts = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(8))
        for value, caption, background in (
            (f'{self.operational_status["daily_release_kg"]} kg', "Pelepasan hari ini", COLORS["mint"]),
            ("27 C", "Berawan", COLORS["sky"]),
            ("06-22", "Jam buka", COLORS["coral"]),
        ):
            fact = Card(orientation="vertical", padding=dp(8), background=background)
            value_label = label(value, 38, 17, COLORS["forest"], True, "center")
            if caption == "Pelepasan hari ini":
                self.daily_release_label = value_label
            fact.add_widget(value_label)
            fact.add_widget(label(caption, 28, 9, COLORS["muted"], False, "center"))
            facts.add_widget(fact)
        content.add_widget(facts)
        daily_note_card = self.info_card("Catatan petugas", self.operational_status["operator_note"], 140)
        self.daily_note_label = daily_note_card.body_label
        content.add_widget(daily_note_card)
        content.add_widget(self.info_card("Aturan tetap berlaku", BAIT_RULE_SHORT, 120, COLORS["sand"]))
        screen.add_widget(scroll)
        return screen

    def build_orders(self):
        screen = Screen(name="orders")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Pesanan Saya", "Riwayat tersimpan di perangkat ini", "profile"))
        self.orders_content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.orders_content.bind(minimum_height=self.orders_content.setter("height"))
        content.add_widget(self.orders_content)
        screen.add_widget(scroll)
        return screen

    def refresh_orders(self):
        self.orders_content.clear_widgets()
        source_rows = (
            self.database.list_bookings()
            if self.orders_admin_mode
            else self.session_bookings
        )
        rows = list(reversed(source_rows[-20:]))
        if not rows:
            self.orders_content.add_widget(self.info_card("Belum ada pesanan", "Pemesanan yang berhasil akan tersimpan permanen dan muncul di halaman ini.", 145, COLORS["mint"]))
            return
        for row in rows:
            code = row["booking_code"]
            event_id = row["event_id"]
            spot_number = row["spot_number"]
            total = row["total_amount"]
            status = row["payment_status"]
            created_at = row["created_at"]
            event = self.event_for(event_id) or {"title": event_id}
            status_text = payment_status_text(status)
            card = Card(orientation="vertical", size_hint_y=None, height=dp(180), padding=dp(13), spacing=dp(3))
            card.add_widget(label(event["title"], 30, 15, COLORS["forest"], True))
            card.add_widget(label(f"{code} | Lapak {spot_number or '-'}", 25, 11, COLORS["terracotta"], True))
            card.add_widget(label(f"{rupiah(total)} | {status_text}", 25, 11, COLORS["muted"]))
            card.add_widget(label(created_at.replace("T", " "), 22, 9, COLORS["muted"]))
            actions = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(7))
            open_button = PrimaryButton(text="Buka Tiket", height=dp(36))
            open_button.bind(
                on_release=lambda _button, booking=row: self.open_saved_ticket(booking)
            )
            actions.add_widget(open_button)
            if status in ("pending", "pay_at_venue") and spot_number is not None:
                cancel_button = GhostButton(text="Batalkan", height=dp(36))
                cancel_button.bind(
                    on_release=lambda _button, booking=row: self.confirm_cancellation(
                        booking
                    )
                )
                actions.add_widget(cancel_button)
            card.add_widget(actions)
            self.orders_content.add_widget(card)

    def confirm_cancellation(self, booking):
        event = self.event_for(booking["event_id"])
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(
            label(
                f'{event["title"]}\nLapak {booking["spot_number"]:02d}\n{booking["booking_code"]}',
                92,
                14,
                COLORS["forest"],
                True,
                "center",
            )
        )
        content.add_widget(
            label(
                "Lapak akan tersedia kembali. Tindakan ini tidak dapat dibatalkan.",
                55,
                10,
                COLORS["muted"],
                False,
                "center",
            )
        )
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        keep_button = GhostButton(text="Pertahankan", height=dp(42))
        cancel_button = PrimaryButton(text="Batalkan Pesanan", height=dp(42))
        actions.add_widget(keep_button)
        actions.add_widget(cancel_button)
        content.add_widget(actions)
        popup = Popup(
            title="Konfirmasi Pembatalan",
            content=content,
            size_hint=(0.9, None),
            height=dp(315),
        )
        keep_button.bind(on_release=popup.dismiss)

        def cancel(*_args):
            popup.dismiss()
            self.cancel_booking(booking["booking_code"])

        cancel_button.bind(on_release=cancel)
        popup.open()

    def cancel_booking(self, booking_code):
        try:
            self.database.cancel_booking(booking_code)
        except BookingStateError as error:
            self.show_message("Tidak dapat membatalkan", str(error))
            return
        except sqlite3.DatabaseError:
            self.show_message(
                "Pembatalan gagal", "Database tidak dapat diperbarui. Silakan coba lagi."
            )
            return
        self.session_bookings = self.database.list_bookings(
            user_id=self.current_user["id"] if self.current_user else None
        )
        self.refresh_availability()
        self.refresh_orders()
        self.refresh_profile()
        self.show_message(
            "Pesanan dibatalkan", "Lapak sudah dikembalikan ke daftar tersedia."
        )

    def build_auth(self):
        screen = Screen(name="auth")
        scroll, content = page_content(padding=(18, 16, 18, 32), spacing=12)
        back = GhostButton(text="< Lanjut sebagai tamu", size_hint_x=0.62)
        back.bind(on_release=lambda *_: self.continue_as_guest())
        content.add_widget(back)
        header = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(154),
            padding=dp(18),
            spacing=dp(3),
            background=COLORS["forest"],
        )
        header.add_widget(label("AKUN PEMANCING", 24, 9, COLORS["sand"], True))
        header.add_widget(label("Masuk ke Adem Ayem", 42, 24, COLORS["white"], True))
        self.auth_context_label = label(
            "Login hanya diperlukan untuk memesan tiket.",
            40,
            10,
            COLORS["mint"],
        )
        header.add_widget(self.auth_context_label)
        content.add_widget(header)
        content.add_widget(section_heading("Selamat datang kembali", "Gunakan username dan password Anda"))
        content.add_widget(label("Username", 24, 12, COLORS["ink"], True))
        self.login_username = StyledTextInput(
            hint_text="contoh: budi_nila", multiline=False, input_type="text"
        )
        content.add_widget(self.login_username)
        content.add_widget(label("Password", 24, 12, COLORS["ink"], True))
        self.login_password = StyledTextInput(
            hint_text="Password akun",
            multiline=False,
            password=True,
            input_type="text",
        )
        content.add_widget(self.login_password)
        self.login_username.focus_next = self.login_password
        self.login_username.bind(
            on_text_validate=lambda *_: setattr(self.login_password, "focus", True)
        )
        login_button = PrimaryButton(text="Masuk & Lanjutkan")
        login_button.bind(on_release=lambda *_: self.login_user())
        self.login_password.bind(on_text_validate=lambda *_: self.login_user())
        content.add_widget(login_button)
        register_button = GhostButton(text="Belum punya akun? Buat Akun")
        register_button.bind(on_release=lambda *_: self.go("register"))
        content.add_widget(register_button)
        content.add_widget(
            self.info_card(
                "Tetap bebas melihat-lihat",
                "Tanpa login Anda tetap dapat membuka jadwal, detail event, galeri, berita, leaderboard, status kolam, dan lokasi.",
                140,
                COLORS["mint"],
            )
        )
        screen.add_widget(scroll)
        return screen

    def build_register(self):
        screen = Screen(name="register")
        scroll, content = page_content(padding=(18, 16, 18, 32), spacing=10)
        back = GhostButton(text="< Kembali ke Login", size_hint_x=0.55)
        back.bind(on_release=lambda *_: self.go("auth"))
        content.add_widget(back)
        content.add_widget(section_heading("Buat Akun Pemancing", "Satu akun untuk tiket dan riwayat Anda"))
        fields = (
            ("Nama lengkap", "register_full_name", "Contoh: Budi Santoso", False, None),
            ("Username", "register_username", "Huruf, angka, atau garis bawah", False, None),
            ("Nomor WhatsApp", "register_phone", "08xxxxxxxxxx", False, "int"),
            ("Password", "register_password", "Minimal 8 karakter", True, None),
            ("Ulangi password", "register_password_confirm", "Ketik password kembali", True, None),
        )
        previous = None
        for title, attribute, hint, password, input_filter in fields:
            content.add_widget(label(title, 24, 12, COLORS["ink"], True))
            field = StyledTextInput(
                hint_text=hint,
                multiline=False,
                password=password,
                input_filter=input_filter,
                input_type="number" if input_filter == "int" else "text",
            )
            setattr(self, attribute, field)
            content.add_widget(field)
            if previous:
                previous.focus_next = field
            previous = field
        create_button = PrimaryButton(text="Buat Akun & Masuk")
        create_button.bind(on_release=lambda *_: self.register_user())
        self.register_password_confirm.bind(
            on_text_validate=lambda *_: self.register_user()
        )
        content.add_widget(create_button)
        content.add_widget(label("Dengan membuat akun, Anda menyetujui Privasi & Ketentuan aplikasi.", 48, 10, COLORS["muted"], False, "center"))
        screen.add_widget(scroll)
        return screen

    def login_user(self):
        username = self.login_username.text.strip()
        password = self.login_password.text
        user = self.database.authenticate_user(username, password)
        if not user:
            self.login_password.text = ""
            self.show_message(
                "Login gagal", "Username atau password tidak sesuai."
            )
            return
        self.login_password.text = ""
        self.complete_login(user)

    def register_user(self):
        full_name = self.register_full_name.text.strip()
        username = self.register_username.text.strip().lower()
        phone = self.register_phone.text.strip()
        password = self.register_password.text
        confirmation = self.register_password_confirm.text
        if len(full_name) < 3:
            self.show_message("Nama belum valid", "Masukkan nama lengkap minimal 3 karakter.")
            return
        if not self.valid_username(username):
            self.show_message("Username belum valid", "Gunakan 3-24 karakter berupa huruf, angka, atau garis bawah.")
            return
        if len(phone) < 9:
            self.show_message("WhatsApp belum valid", "Masukkan nomor WhatsApp aktif minimal 9 angka.")
            return
        if len(password) < 8 or password != confirmation:
            self.show_message("Password belum valid", "Gunakan minimal 8 karakter dan pastikan kedua password sama.")
            return
        try:
            user = self.database.create_user(username, password, full_name, phone)
        except AccountExistsError as error:
            self.show_message("Tidak dapat membuat akun", str(error))
            return
        for field in (
            self.register_full_name,
            self.register_username,
            self.register_phone,
            self.register_password,
            self.register_password_confirm,
        ):
            field.text = ""
        self.complete_login(user)

    @staticmethod
    def valid_username(username):
        return 3 <= len(username) <= 24 and username.replace("_", "").isalnum()

    def complete_login(self, user):
        self.current_user = user
        self.session_bookings = self.database.list_bookings(user_id=user["id"])
        self.refresh_profile()
        pending_event = self.pending_booking_event_id
        self.pending_booking_event_id = None
        if pending_event:
            self.start_booking(pending_event)
        else:
            self.go("profile")

    def logout_user(self):
        self.current_user = None
        self.session_bookings = []
        self.current_ticket_booking = None
        self.pending_booking_event_id = None
        self.refresh_profile()
        self.go("profile")

    def continue_as_guest(self):
        self.pending_booking_event_id = None
        self.go("home")

    def open_user_orders(self):
        if not self.current_user:
            self.auth_context_label.text = "Masuk untuk melihat tiket dan riwayat pesanan Anda."
            self.go("auth")
            return
        self.orders_admin_mode = False
        self.session_bookings = self.database.list_bookings(
            user_id=self.current_user["id"]
        )
        self.go("orders")

    def open_admin_orders(self):
        if not self.admin_authenticated:
            self.request_admin_access()
            return
        self.orders_admin_mode = True
        self.go("orders")

    def build_profile(self):
        screen = Screen(name="profile")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)

        hero = Card(orientation="vertical", size_hint_y=None, height=dp(230), padding=dp(15), spacing=dp(7), background=COLORS["forest"])
        top = BoxLayout(size_hint_y=None, height=dp(30))
        top.add_widget(label("AKUN PEMANCING", 30, 9, COLORS["sand"], True))
        self.profile_account_badge = label("MODE TAMU", 30, 8, COLORS["mint"], True, "right")
        top.add_widget(self.profile_account_badge)
        hero.add_widget(top)
        identity = BoxLayout(spacing=dp(12))
        self.profile_avatar = Card(size_hint_x=None, width=dp(88), padding=dp(5), background=COLORS["terracotta"])
        identity.add_widget(self.profile_avatar)
        copy = BoxLayout(orientation="vertical", spacing=dp(1))
        self.profile_name_label = label("Pengunjung Tamu", 38, 23, COLORS["white"], True)
        self.profile_username_label = label("@guest", 25, 10, COLORS["mint"])
        self.profile_phone_label = label("Login untuk memesan tiket", 25, 9, COLORS["sand"], True)
        copy.add_widget(self.profile_name_label)
        copy.add_widget(self.profile_username_label)
        copy.add_widget(self.profile_phone_label)
        identity.add_widget(copy)
        hero.add_widget(identity)
        content.add_widget(hero)

        stats = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(7))
        self.profile_active_count = self.fact_card("TIKET AKTIF", "0", COLORS["white"])
        stats.add_widget(self.profile_active_count)
        self.profile_event_count = self.fact_card("EVENT DIIKUTI", "0", COLORS["white"])
        stats.add_widget(self.profile_event_count)
        self.profile_member_status = self.fact_card("STATUS", "TAMU", COLORS["white"])
        stats.add_widget(self.profile_member_status)
        content.add_widget(stats)

        content.add_widget(section_heading("Tiket aktif", "Akses cepat untuk check-in event"))
        ticket_card = Card(orientation="vertical", size_hint_y=None, height=dp(172), padding=dp(13), spacing=dp(4), background=COLORS["white"])
        self.profile_ticket_status = label("BELUM ADA PEMESANAN", 20, 8, COLORS["terracotta"], True)
        self.profile_ticket_title = label("Pesan tiket event pertamamu", 34, 17, COLORS["forest"], True)
        self.profile_ticket_meta = label("Pilih event dan salah satu dari 82 lapak", 28, 10, COLORS["muted"])
        self.profile_ticket_code = label("PILIH EVENT", 24, 10, COLORS["forest"], True)
        ticket_card.add_widget(self.profile_ticket_status)
        ticket_card.add_widget(self.profile_ticket_title)
        ticket_card.add_widget(self.profile_ticket_meta)
        ticket_card.add_widget(self.profile_ticket_code)
        self.profile_ticket_button = PrimaryButton(text="Lihat Jadwal Event", height=dp(38), size_hint_x=0.62)
        self.profile_ticket_button.bind(on_release=lambda *_: self.open_profile_ticket())
        ticket_card.add_widget(self.profile_ticket_button)
        content.add_widget(ticket_card)

        content.add_widget(section_heading("Informasi & bantuan", "Pusat akun Pemancingan Adem Ayem Dlopo"))
        for title, subtitle, background, callback in (
            ("Pengaturan akun", "Login, edit username, foto profil, atau logout", COLORS["coral"], lambda: self.open_account_settings()),
            ("Keamanan akun", "Ganti password dan lihat aktivitas login", COLORS["sky"], lambda: self.open_account_security()),
            ("Pesanan saya", "Tiket aktif dan status pembayaran", COLORS["mint"], lambda: self.open_user_orders()),
            ("Status hari ini", "Cuaca, mood nila, dan jam operasional", COLORS["sky"], lambda: self.go("daily_status")),
            ("Berita & pengumuman", "Informasi resmi dari pengelola", COLORS["sand"], lambda: self.go("news")),
            ("Panduan pengunjung", "Aturan umpan, fasilitas, dan lokasi", COLORS["mint"], lambda: self.go("info")),
            ("Buka Google Maps", "Rute resmi dari pusat Kota Kediri", COLORS["sky"], lambda: self.open_map()),
        ):
            row = Card(size_hint_y=None, height=dp(78), padding=dp(10), spacing=dp(9), background=COLORS["white"])
            marker = Card(size_hint_x=None, width=dp(48), padding=dp(5), background=background)
            marker.add_widget(label("AA", 48, 11, COLORS["forest"], True, "center"))
            row.add_widget(marker)
            copy = BoxLayout(orientation="vertical")
            copy.add_widget(label(title, 30, 13, COLORS["forest"], True))
            copy.add_widget(label(subtitle, 27, 9, COLORS["muted"]))
            row.add_widget(copy)
            open_button = GhostButton(text=">", size_hint_x=None, width=dp(42), height=dp(40))
            open_button.bind(on_release=lambda _button, action=callback: action())
            row.add_widget(open_button)
            content.add_widget(row)

        rule = Card(orientation="vertical", size_hint_y=None, height=dp(130), padding=dp(14), spacing=dp(5), background=COLORS["sand"])
        rule.add_widget(label("ATURAN UMPAN", 20, 8, COLORS["terracotta"], True))
        rule.add_widget(label("Umpan wajib berbahan alami", 34, 17, COLORS["forest"], True))
        rule.add_widget(label("Media non-alami dilarang. Essen/pemanis hanya boleh sebagai campuran.", 45, 10, COLORS["muted"]))
        content.add_widget(rule)
        content.add_widget(label(f"PEMANCINGAN ADEM AYEM DLOPO | APP {APP_VERSION}", 34, 8, COLORS["muted"], True, "center"))
        screen.add_widget(scroll)
        return screen

    def build_edit_profile(self):
        screen = Screen(name="edit_profile")
        scroll, content = page_content(padding=(16, 14, 16, 30), spacing=10)
        back = GhostButton(text="< Kembali ke Profil", size_hint_x=0.58)
        back.bind(on_release=lambda *_: self.go("profile"))
        content.add_widget(back)
        content.add_widget(section_heading("Edit Profil", "Sesuaikan identitas akun pemancing"))
        avatar_card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(210),
            padding=dp(12),
            spacing=dp(8),
            background=COLORS["mint"],
        )
        self.edit_avatar_preview = Card(
            size_hint=(None, None),
            size=(dp(108), dp(108)),
            pos_hint={"center_x": 0.5},
            padding=dp(4),
            background=COLORS["terracotta"],
        )
        avatar_card.add_widget(self.edit_avatar_preview)
        choose_photo = GhostButton(text="Pilih Foto dari Perangkat", height=dp(40))
        choose_photo.bind(on_release=lambda *_: self.choose_profile_photo())
        avatar_card.add_widget(choose_photo)
        content.add_widget(avatar_card)
        for title, attribute, hint, input_filter in (
            ("Nama lengkap", "edit_full_name", "Nama lengkap", None),
            ("Username", "edit_username", "Username unik", None),
            ("Nomor WhatsApp", "edit_phone", "08xxxxxxxxxx", "int"),
        ):
            content.add_widget(label(title, 24, 12, COLORS["ink"], True))
            field = StyledTextInput(
                hint_text=hint,
                multiline=False,
                input_filter=input_filter,
                input_type="number" if input_filter == "int" else "text",
            )
            setattr(self, attribute, field)
            content.add_widget(field)
        save_button = PrimaryButton(text="Simpan Perubahan Profil")
        save_button.bind(on_release=lambda *_: self.save_profile())
        content.add_widget(save_button)
        logout_button = GhostButton(text="Keluar dari Akun")
        logout_button.bind(on_release=lambda *_: self.logout_user())
        content.add_widget(logout_button)
        content.add_widget(
            label(
                "Foto disalin ke penyimpanan aplikasi. Format yang didukung: PNG, JPG, dan JPEG hingga 5 MB.",
                58,
                10,
                COLORS["muted"],
                False,
                "center",
            )
        )
        screen.add_widget(scroll)
        return screen

    def open_account_settings(self):
        if not self.current_user:
            self.auth_context_label.text = "Masuk atau buat akun untuk memesan tiket dan mengatur profil."
            self.go("auth")
            return
        self.edit_full_name.text = self.current_user["full_name"]
        self.edit_username.text = self.current_user["username"]
        self.edit_phone.text = self.current_user["phone"]
        self.pending_avatar_path = self.current_user.get("avatar_path")
        self.render_avatar(
            self.edit_avatar_preview,
            self.pending_avatar_path,
            self.current_user["full_name"],
            96,
        )
        self.go("edit_profile")

    def choose_profile_photo(self):
        chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"],
            multiselect=False,
        )
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        layout.add_widget(chooser)
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        close_button = GhostButton(text="Batal", height=dp(42))
        select_button = PrimaryButton(text="Gunakan Foto", height=dp(42))
        actions.add_widget(close_button)
        actions.add_widget(select_button)
        layout.add_widget(actions)
        popup = Popup(
            title="Pilih Foto Profil",
            content=layout,
            size_hint=(0.96, 0.9),
        )
        close_button.bind(on_release=popup.dismiss)

        def select(*_args):
            if not chooser.selection:
                return
            source = chooser.selection[0]
            if not os.path.isfile(source) or os.path.getsize(source) > 5 * 1024 * 1024:
                popup.dismiss()
                self.show_message(
                    "Foto tidak dapat digunakan",
                    "Pilih file PNG/JPG berukuran maksimal 5 MB.",
                )
                return
            extension = os.path.splitext(source)[1].lower()
            avatar_directory = os.path.join(self.user_data_dir, "avatars")
            os.makedirs(avatar_directory, exist_ok=True)
            destination = os.path.join(
                avatar_directory, f"user-{self.current_user['id']}-{uuid4().hex}{extension}"
            )
            try:
                shutil.copy2(source, destination)
            except OSError:
                popup.dismiss()
                self.show_message(
                    "Foto gagal disalin", "Periksa izin dan ruang penyimpanan perangkat."
                )
                return
            self.pending_avatar_path = destination
            self.render_avatar(
                self.edit_avatar_preview,
                destination,
                self.edit_full_name.text or self.current_user["full_name"],
                96,
            )
            popup.dismiss()

        select_button.bind(on_release=select)
        popup.open()

    def save_profile(self):
        if not self.current_user:
            self.go("auth")
            return
        full_name = self.edit_full_name.text.strip()
        username = self.edit_username.text.strip().lower()
        phone = self.edit_phone.text.strip()
        if len(full_name) < 3 or not self.valid_username(username) or len(phone) < 9:
            self.show_message(
                "Profil belum valid",
                "Periksa nama, username 3-24 karakter, dan nomor WhatsApp.",
            )
            return
        try:
            self.current_user = self.database.update_user(
                self.current_user["id"],
                username,
                full_name,
                phone,
                self.pending_avatar_path,
            )
        except AccountExistsError as error:
            self.show_message("Username tidak tersedia", str(error))
            return
        self.refresh_profile()
        self.go("profile")
        self.show_message("Profil diperbarui", "Perubahan akun berhasil disimpan.")

    def render_avatar(self, container, avatar_path, full_name, size=82):
        container.clear_widgets()
        if avatar_path and os.path.isfile(avatar_path):
            container.add_widget(Image(source=avatar_path, fit_mode="cover"))
            return
        initials = "".join(part[0] for part in full_name.split()[:2]).upper() or "AA"
        container.add_widget(label(initials, size, 27, COLORS["white"], True, "center"))

    def build_account_security(self):
        screen = Screen(name="account_security")
        scroll, content = page_content(padding=(16, 14, 16, 30), spacing=10)
        back = GhostButton(text="< Kembali ke Profil", size_hint_x=0.58)
        back.bind(on_release=lambda *_: self.go("profile"))
        content.add_widget(back)
        content.add_widget(section_heading("Keamanan Akun", "Kelola password dan aktivitas login"))
        security_card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(315),
            padding=dp(14),
            spacing=dp(7),
            background=COLORS["white"],
        )
        security_card.add_widget(label("Ganti password", 30, 17, COLORS["forest"], True))
        self.security_current_password = StyledTextInput(
            hint_text="Password saat ini", multiline=False, password=True
        )
        self.security_new_password = StyledTextInput(
            hint_text="Password baru, minimal 8 karakter", multiline=False, password=True
        )
        self.security_confirm_password = StyledTextInput(
            hint_text="Ulangi password baru", multiline=False, password=True
        )
        security_card.add_widget(self.security_current_password)
        security_card.add_widget(self.security_new_password)
        security_card.add_widget(self.security_confirm_password)
        change_button = PrimaryButton(text="Perbarui Password", height=dp(42))
        change_button.bind(on_release=lambda *_: self.change_account_password())
        security_card.add_widget(change_button)
        content.add_widget(security_card)
        content.add_widget(section_heading("Aktivitas login", "Riwayat login terbaru pada akun ini"))
        self.security_login_history = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(8)
        )
        self.security_login_history.bind(
            minimum_height=self.security_login_history.setter("height")
        )
        content.add_widget(self.security_login_history)
        screen.add_widget(scroll)
        return screen

    def open_account_security(self):
        if not self.current_user:
            self.auth_context_label.text = "Masuk untuk membuka pengaturan keamanan akun."
            self.go("auth")
            return
        self.security_current_password.text = ""
        self.security_new_password.text = ""
        self.security_confirm_password.text = ""
        self.refresh_login_history()
        self.go("account_security")

    def refresh_login_history(self):
        self.security_login_history.clear_widgets()
        if not self.current_user:
            return
        rows = self.database.login_history(self.current_user["id"], limit=10)
        if not rows:
            self.security_login_history.add_widget(
                self.info_card("Belum ada aktivitas", "Riwayat login akan muncul di sini.", 110)
            )
            return
        for row in rows:
            success = bool(row["success"])
            card = Card(
                size_hint_y=None,
                height=dp(72),
                padding=dp(11),
                spacing=dp(8),
                background=COLORS["mint"] if success else COLORS["sand"],
            )
            card.add_widget(
                label(
                    "LOGIN BERHASIL" if success else "LOGIN GAGAL",
                    34,
                    11,
                    COLORS["forest"] if success else COLORS["terracotta"],
                    True,
                )
            )
            card.add_widget(
                label(
                    row["created_at"].replace("T", " "),
                    34,
                    10,
                    COLORS["muted"],
                    False,
                    "right",
                )
            )
            self.security_login_history.add_widget(card)

    def change_account_password(self):
        if not self.current_user:
            self.go("auth")
            return
        current = self.security_current_password.text
        new_password = self.security_new_password.text
        confirmation = self.security_confirm_password.text
        if len(new_password) < 8 or new_password != confirmation:
            self.show_message(
                "Password belum valid",
                "Password baru minimal 8 karakter dan kedua isian harus sama.",
            )
            return
        try:
            self.database.change_password(
                self.current_user["id"], current, new_password
            )
        except PasswordError as error:
            self.show_message("Password tidak berubah", str(error))
            return
        self.security_current_password.text = ""
        self.security_new_password.text = ""
        self.security_confirm_password.text = ""
        self.show_message(
            "Password diperbarui", "Gunakan password baru pada login berikutnya."
        )

    def refresh_profile(self):
        if not hasattr(self, "profile_active_count"):
            return
        if not self.current_user:
            self.profile_account_badge.text = "MODE TAMU"
            self.profile_name_label.text = "Pengunjung Tamu"
            self.profile_username_label.text = "@guest"
            self.profile_phone_label.text = "Login hanya diperlukan untuk memesan"
            self.render_avatar(self.profile_avatar, None, "Pengunjung Tamu")
            self.profile_active_count.value_label.text = "0"
            self.profile_event_count.value_label.text = "0"
            self.profile_member_status.value_label.text = "TAMU"
            self.profile_ticket_status.text = "BELUM LOGIN"
            self.profile_ticket_title.text = "Masuk untuk memesan tiket"
            self.profile_ticket_meta.text = "Jelajah aplikasi tetap bebas tanpa akun"
            self.profile_ticket_code.text = "AKUN DIPERLUKAN SAAT BOOKING"
            self.profile_ticket_button.text = "Masuk atau Buat Akun"
            return

        self.profile_account_badge.text = "AKUN AKTIF"
        self.profile_name_label.text = self.current_user["full_name"]
        self.profile_username_label.text = f'@{self.current_user["username"]}'
        self.profile_phone_label.text = self.current_user["phone"]
        self.render_avatar(
            self.profile_avatar,
            self.current_user.get("avatar_path"),
            self.current_user["full_name"],
        )
        active_bookings = [
            booking
            for booking in self.session_bookings
            if booking["payment_status"] != "cancelled"
        ]
        active_count = len(active_bookings)
        self.profile_active_count.value_label.text = str(active_count)
        self.profile_event_count.value_label.text = str(
            len({booking["event_id"] for booking in self.session_bookings})
        )
        self.profile_member_status.value_label.text = "MEMBER"
        if not active_bookings:
            self.profile_ticket_status.text = "BELUM ADA PEMESANAN"
            self.profile_ticket_title.text = "Pesan tiket event pertamamu"
            self.profile_ticket_meta.text = "Pilih event dan salah satu dari 82 lapak"
            self.profile_ticket_code.text = "PILIH EVENT"
            self.profile_ticket_button.text = "Lihat Jadwal Event"
            return
        booking = active_bookings[-1]
        event = self.event_for(booking["event_id"])
        self.profile_ticket_status.text = "SIAP DIGUNAKAN"
        self.profile_ticket_title.text = event["title"]
        spot_text = (
            f'Lapak {booking["spot_number"]:02d}'
            if booking["spot_number"] is not None
            else "Lapak belum tercatat"
        )
        self.profile_ticket_meta.text = f'{spot_text} | {event["date"]}'
        self.profile_ticket_code.text = booking["booking_code"]
        self.profile_ticket_button.text = "Buka Tiket Digital"

    def open_profile_ticket(self):
        if not self.current_user:
            self.auth_context_label.text = "Masuk untuk memilih lapak dan membeli tiket event."
            self.go("auth")
            return
        active_bookings = [
            booking
            for booking in self.session_bookings
            if booking["payment_status"] != "cancelled"
        ]
        if active_bookings:
            self.open_saved_ticket(active_bookings[-1])
        else:
            self.go("events")

    def build_admin(self):
        screen = Screen(name="admin")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Dashboard Admin", "Ringkasan operasional pemancingan", "info"))
        metrics = BoxLayout(size_hint_y=None, height=dp(112), spacing=dp(8))
        for value, caption, background in (
            (str(len(EVENTS)), "Paket event", COLORS["mint"]),
            ("82", "Total lapak", COLORS["sky"]),
            (self.total_release_text(), "Total pelepasan", COLORS["sand"]),
        ):
            metric = Card(orientation="vertical", padding=dp(8), background=background)
            value_label = label(value, 42, 18, COLORS["forest"], True, "center")
            if caption == "Paket event":
                self.admin_event_metric = value_label
            elif caption == "Total pelepasan":
                self.admin_release_metric = value_label
            metric.add_widget(value_label)
            metric.add_widget(label(caption, 30, 9, COLORS["muted"], False, "center"))
            metrics.add_widget(metric)
        content.add_widget(metrics)
        content.add_widget(section_heading("Akses pengelolaan", "Pilih data operasional yang akan diperbarui"))
        for title, subtitle, action in (
            ("Kelola Operasional", "Jam buka, mood ikan, dan pelepasan nila", lambda: self.go("operations")),
            ("Kelola Akun", "Pengguna, login terakhir, status, dan reset password", lambda: self.open_admin_users()),
            ("Lihat Pesanan", "Pantau seluruh booking yang masuk", lambda: self.open_admin_orders()),
            ("Backup Database", "Buat salinan aman seluruh data lokal", lambda: self.create_database_backup()),
            ("Kelola Event & Jadwal", "Tambah, ubah, terbitkan, atau arsipkan event", lambda: self.open_admin_events()),
            ("Kelola Galeri", "Unggah foto baru langsung dari perangkat", lambda: self.open_admin_gallery()),
            ("Kelola Berita", "Terbitkan pengumuman dan kabar kolam", lambda: self.open_admin_news()),
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

    def total_release_text(self):
        total = 0
        for event in EVENTS.values():
            digits = "".join(character for character in event["release"] if character.isdigit())
            total += int(digits or 0)
        return f"{total} kg"

    def refresh_admin_metrics(self):
        if hasattr(self, "admin_event_metric"):
            self.admin_event_metric.text = str(len(EVENTS))
            self.admin_release_metric.text = self.total_release_text()

    def build_admin_events(self):
        screen = Screen(name="admin_events")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kelola Event", "Jadwal dan tiket tersimpan ke database", "admin"))
        content.add_widget(section_heading("Form event", "Kosongkan untuk membuat event baru"))
        self.admin_event_mode = label("EVENT BARU", 28, 11, COLORS["terracotta"], True)
        content.add_widget(self.admin_event_mode)
        self.admin_event_inputs = {}
        for key, title, hint, input_filter in (
            ("title", "Nama event", "Contoh: Grand Mix Oktober", None),
            ("date", "Tanggal", "Contoh: Minggu, 4 Oktober 2026", None),
            ("time", "Jam acara", "Contoh: 08.00 - 13.00 WIB", None),
            ("price", "Harga tiket", "Contoh: 100000", "int"),
            ("release_kg", "Ikan nila dilepas (kg)", "Contoh: 225", "int"),
            ("available", "Lapak tersedia saat diterbitkan", "0 sampai 82", "int"),
        ):
            content.add_widget(label(title, 24, 11, COLORS["forest"], True))
            field = StyledTextInput(
                hint_text=hint,
                multiline=False,
                input_filter=input_filter,
                input_type="number" if input_filter == "int" else "text",
            )
            self.admin_event_inputs[key] = field
            content.add_widget(field)
        self.admin_event_image = None
        self.admin_event_image_label = label("Belum ada foto dipilih", 35, 9, COLORS["muted"], False, "center")
        content.add_widget(self.admin_event_image_label)
        choose_image = GhostButton(text="Pilih Foto Event dari Perangkat")
        choose_image.bind(on_release=lambda *_: self.choose_content_image("event"))
        content.add_widget(choose_image)
        event_actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        reset_button = GhostButton(text="Form Baru")
        reset_button.bind(on_release=lambda *_: self.reset_event_form())
        save_button = PrimaryButton(text="Simpan & Terbitkan")
        save_button.bind(on_release=lambda *_: self.save_admin_event())
        event_actions.add_widget(reset_button)
        event_actions.add_widget(save_button)
        content.add_widget(event_actions)
        content.add_widget(section_heading("Daftar event", "Perubahan langsung tampil pada menu Agenda"))
        self.admin_event_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(9))
        self.admin_event_list.bind(minimum_height=self.admin_event_list.setter("height"))
        content.add_widget(self.admin_event_list)
        screen.add_widget(scroll)
        return screen

    def open_admin_events(self):
        if not self.admin_authenticated:
            self.request_admin_access()
            return
        self.refresh_admin_events()
        self.go("admin_events")

    def reset_event_form(self):
        self.editing_event_id = None
        self.admin_event_mode.text = "EVENT BARU"
        for field in self.admin_event_inputs.values():
            field.text = ""
        self.admin_event_inputs["available"].text = "82"
        self.admin_event_inputs["available"].disabled = False
        self.admin_event_image = None
        self.admin_event_image_label.text = "Belum ada foto dipilih"

    def edit_admin_event(self, event):
        self.editing_event_id = event["event_id"]
        self.admin_event_mode.text = f'EDIT EVENT | {event["event_id"]}'
        self.admin_event_inputs["title"].text = event["title"]
        self.admin_event_inputs["date"].text = event["date"]
        self.admin_event_inputs["time"].text = event["time"]
        self.admin_event_inputs["price"].text = str(event["price"])
        digits = "".join(character for character in event["release"] if character.isdigit())
        self.admin_event_inputs["release_kg"].text = digits
        self.admin_event_inputs["available"].text = str(event["available"])
        self.admin_event_inputs["available"].disabled = True
        self.admin_event_image = event["image"]
        self.admin_event_image_label.text = os.path.basename(event["image"])

    def save_admin_event(self):
        values = {key: field.text.strip() for key, field in self.admin_event_inputs.items()}
        if not all(values[key] for key in ("title", "date", "time", "price", "release_kg")):
            self.show_message("Data belum lengkap", "Isi nama, tanggal, jam, harga, dan jumlah ikan.")
            return
        try:
            price = int(values["price"])
            release_kg = int(values["release_kg"])
            available = int(values["available"] or 82)
        except ValueError:
            self.show_message("Angka belum valid", "Harga, jumlah ikan, dan lapak harus berupa angka.")
            return
        if price < 1 or release_kg < 1 or not 0 <= available <= 82:
            self.show_message("Data belum valid", "Harga dan ikan minimal 1; lapak tersedia 0 sampai 82.")
            return
        if not self.admin_event_image:
            self.show_message("Foto diperlukan", "Pilih satu foto event sebelum menerbitkan jadwal.")
            return
        payload = {
            "title": values["title"], "date": values["date"], "time": values["time"],
            "price": price, "quota": 82, "release": f"Pelepasan nila {release_kg} kg",
            "image": self.admin_event_image,
        }
        try:
            if getattr(self, "editing_event_id", None):
                self.database.update_event(self.editing_event_id, payload)
                message = "Perubahan event telah diterbitkan."
            else:
                payload["event_id"] = f"EVT-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"
                self.database.create_event(payload, available)
                message = "Event baru telah diterbitkan."
        except (ValueError, sqlite3.DatabaseError) as error:
            self.show_message("Event gagal disimpan", str(error))
            return
        self.admin_event_inputs["available"].disabled = False
        self.reset_event_form()
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_events()
        self.show_message("Event tersimpan", message)

    def refresh_admin_events(self):
        if not hasattr(self, "admin_event_list"):
            return
        self.admin_event_list.clear_widgets()
        rows = self.database.list_events(active_only=False)
        for event in rows:
            card = Card(orientation="vertical", size_hint_y=None, height=dp(146), padding=dp(10), spacing=dp(2))
            status = "TERBIT" if event["is_active"] else "DIARSIPKAN"
            card.add_widget(label(f'{status} | {event["event_id"]}', 22, 8, COLORS["sage"] if event["is_active"] else COLORS["muted"], True))
            card.add_widget(label(event["title"], 30, 15, COLORS["forest"], True))
            card.add_widget(label(f'{event["date"]} | {event["time"]}', 24, 9, COLORS["muted"]))
            card.add_widget(label(f'{event["release"]} | {rupiah(event["price"])} | {event["available"]}/82 lapak', 24, 9, COLORS["terracotta"], True))
            actions = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(7))
            edit = GhostButton(text="Edit", height=dp(36))
            edit.bind(on_release=lambda _button, item=event: self.edit_admin_event(item))
            toggle = PrimaryButton(text="Arsipkan" if event["is_active"] else "Terbitkan", height=dp(36))
            toggle.bind(on_release=lambda _button, item=event: self.toggle_event_active(item))
            actions.add_widget(edit)
            actions.add_widget(toggle)
            card.add_widget(actions)
            self.admin_event_list.add_widget(card)

    def toggle_event_active(self, event):
        active_rows = self.database.list_events(active_only=True)
        if event["is_active"] and len(active_rows) <= 1:
            self.show_message("Event tetap aktif", "Terbitkan event lain sebelum mengarsipkan event terakhir.")
            return
        self.database.set_event_active(event["event_id"], not event["is_active"])
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_events()

    def build_admin_gallery(self):
        screen = Screen(name="admin_gallery")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kelola Galeri", "Unggah dokumentasi langsung dari perangkat", "admin"))
        self.admin_gallery_title = StyledTextInput(hint_text="Judul foto", multiline=False)
        self.admin_gallery_category = StyledSpinner(text="Event", values=("Event", "Tangkapan", "Momen", "Kolam"))
        self.admin_gallery_image = None
        self.admin_gallery_image_label = label("Belum ada foto dipilih", 34, 9, COLORS["muted"], False, "center")
        content.add_widget(label("Judul foto", 24, 11, COLORS["forest"], True))
        content.add_widget(self.admin_gallery_title)
        content.add_widget(label("Kategori", 24, 11, COLORS["forest"], True))
        content.add_widget(self.admin_gallery_category)
        content.add_widget(self.admin_gallery_image_label)
        choose = GhostButton(text="Pilih Foto Galeri")
        choose.bind(on_release=lambda *_: self.choose_content_image("gallery"))
        content.add_widget(choose)
        save = PrimaryButton(text="Unggah ke Galeri")
        save.bind(on_release=lambda *_: self.save_gallery_item())
        content.add_widget(save)
        content.add_widget(section_heading("Foto tersimpan", "Arsipkan foto yang tidak lagi ditampilkan"))
        self.admin_gallery_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(9))
        self.admin_gallery_list.bind(minimum_height=self.admin_gallery_list.setter("height"))
        content.add_widget(self.admin_gallery_list)
        screen.add_widget(scroll)
        return screen

    def open_admin_gallery(self):
        if not self.admin_authenticated:
            self.request_admin_access()
            return
        self.refresh_admin_gallery()
        self.go("admin_gallery")

    def save_gallery_item(self):
        title = self.admin_gallery_title.text.strip()
        if len(title) < 3 or not self.admin_gallery_image:
            self.show_message("Foto belum lengkap", "Isi judul dan pilih foto terlebih dahulu.")
            return
        self.database.create_gallery_item(title, self.admin_gallery_category.text, self.admin_gallery_image)
        self.admin_gallery_title.text = ""
        self.admin_gallery_image = None
        self.admin_gallery_image_label.text = "Belum ada foto dipilih"
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_gallery()
        self.show_message("Foto diunggah", "Foto baru sudah tampil di halaman Galeri.")

    def refresh_admin_gallery(self):
        if not hasattr(self, "admin_gallery_list"):
            return
        self.admin_gallery_list.clear_widgets()
        for item in self.database.list_gallery_items(active_only=False):
            card = Card(size_hint_y=None, height=dp(92), padding=dp(8), spacing=dp(8))
            card.add_widget(Image(source=media_source(item["image_path"]), size_hint_x=0.28, fit_mode="cover"))
            card.add_widget(label(f'{item["title"]}\n{item["category"]} | {"TERBIT" if item["is_active"] else "ARSIP"}', 70, 11, COLORS["forest"], True))
            toggle = GhostButton(text="Arsipkan" if item["is_active"] else "Terbitkan", size_hint_x=0.31, height=dp(38))
            toggle.bind(on_release=lambda _button, row=item: self.toggle_gallery_active(row))
            card.add_widget(toggle)
            self.admin_gallery_list.add_widget(card)

    def toggle_gallery_active(self, item):
        self.database.set_gallery_active(item["id"], not bool(item["is_active"]))
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_gallery()

    def build_admin_news(self):
        screen = Screen(name="admin_news")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kelola Berita", "Terbitkan pengumuman tanpa mengubah kode", "admin"))
        self.admin_news_fields = {}
        for key, title, hint, multiline, height in (
            ("title", "Judul berita", "Judul utama", False, 52),
            ("summary", "Ringkasan", "Ringkasan singkat", True, 82),
            ("date", "Tanggal terbit", "Contoh: 17 September 2026", False, 52),
            ("badge", "Label", "Contoh: PENDAFTARAN DIBUKA", False, 52),
            ("facts", "Fakta singkat", "Contoh: 225 KG | 82 LAPAK", False, 52),
            ("body", "Isi berita", "Pisahkan paragraf dengan satu baris kosong", True, 150),
        ):
            content.add_widget(label(title, 24, 11, COLORS["forest"], True))
            field = StyledTextInput(hint_text=hint, multiline=multiline, height=dp(height))
            self.admin_news_fields[key] = field
            content.add_widget(field)
        content.add_widget(label("Kategori", 24, 11, COLORS["forest"], True))
        self.admin_news_category = StyledSpinner(text="Event", values=("Event", "Kolam", "Aturan", "Pengumuman"))
        content.add_widget(self.admin_news_category)
        content.add_widget(label("Tautkan ke event (opsional)", 24, 11, COLORS["forest"], True))
        self.admin_news_event = StyledSpinner(text="Tidak terkait event", values=("Tidak terkait event",))
        content.add_widget(self.admin_news_event)
        self.admin_news_image = None
        self.admin_news_image_label = label("Belum ada foto dipilih", 34, 9, COLORS["muted"], False, "center")
        content.add_widget(self.admin_news_image_label)
        choose = GhostButton(text="Pilih Foto Berita")
        choose.bind(on_release=lambda *_: self.choose_content_image("news"))
        content.add_widget(choose)
        save = PrimaryButton(text="Terbitkan Berita")
        save.bind(on_release=lambda *_: self.save_news_item())
        content.add_widget(save)
        content.add_widget(section_heading("Berita tersimpan", "Kontrol pengumuman yang tampil ke publik"))
        self.admin_news_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(9))
        self.admin_news_list.bind(minimum_height=self.admin_news_list.setter("height"))
        content.add_widget(self.admin_news_list)
        screen.add_widget(scroll)
        return screen

    def open_admin_news(self):
        if not self.admin_authenticated:
            self.request_admin_access()
            return
        event_ids = tuple(self.database.list_events(active_only=True))
        self.admin_news_event.values = ("Tidak terkait event",) + tuple(row["event_id"] for row in event_ids)
        self.refresh_admin_news()
        self.go("admin_news")

    def save_news_item(self):
        values = {key: field.text.strip() for key, field in self.admin_news_fields.items()}
        if not all(values.values()) or not self.admin_news_image:
            self.show_message("Berita belum lengkap", "Lengkapi semua kolom dan pilih foto berita.")
            return
        event_id = None if self.admin_news_event.text == "Tidak terkait event" else self.admin_news_event.text
        item = {
            "category": self.admin_news_category.text, "title": values["title"],
            "summary": values["summary"], "date": values["date"], "badge": values["badge"].upper(),
            "image": self.admin_news_image, "event_id": event_id,
            "body": values["body"], "facts": values["facts"],
        }
        self.database.create_news_item(item)
        for field in self.admin_news_fields.values():
            field.text = ""
        self.admin_news_image = None
        self.admin_news_image_label.text = "Belum ada foto dipilih"
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_news()
        self.show_message("Berita diterbitkan", "Kabar baru sudah tampil di halaman Berita.")

    def refresh_admin_news(self):
        if not hasattr(self, "admin_news_list"):
            return
        self.admin_news_list.clear_widgets()
        for item in self.database.list_news_items(active_only=False):
            card = Card(orientation="vertical", size_hint_y=None, height=dp(112), padding=dp(9), spacing=dp(2))
            card.add_widget(label(f'{item["category"].upper()} | {item["date"]} | {"TERBIT" if item["is_active"] else "ARSIP"}', 22, 8, COLORS["terracotta"], True))
            card.add_widget(label(item["title"], 38, 13, COLORS["forest"], True))
            toggle = GhostButton(text="Arsipkan" if item["is_active"] else "Terbitkan", height=dp(34), size_hint_x=0.46)
            toggle.bind(on_release=lambda _button, row=item: self.toggle_news_active(row))
            card.add_widget(toggle)
            self.admin_news_list.add_widget(card)

    def toggle_news_active(self, item):
        active = self.database.list_news_items(active_only=True)
        if item["is_active"] and len(active) <= 1:
            self.show_message("Berita tetap aktif", "Terbitkan berita lain sebelum mengarsipkan berita terakhir.")
            return
        self.database.set_news_active(item["id"], not bool(item["is_active"]))
        self.reload_content_data(refresh_widgets=True)
        self.refresh_admin_news()

    def choose_content_image(self, content_type):
        chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"],
            multiselect=False,
        )
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        layout.add_widget(chooser)
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        cancel = GhostButton(text="Batal")
        select = PrimaryButton(text="Gunakan Foto")
        actions.add_widget(cancel)
        actions.add_widget(select)
        layout.add_widget(actions)
        popup = Popup(title="Pilih Foto Konten", content=layout, size_hint=(0.96, 0.9))
        cancel.bind(on_release=popup.dismiss)

        def use_image(*_args):
            if not chooser.selection:
                return
            source = chooser.selection[0]
            if not os.path.isfile(source) or os.path.getsize(source) > 10 * 1024 * 1024:
                popup.dismiss()
                self.show_message("Foto tidak dapat digunakan", "Pilih PNG/JPG berukuran maksimal 10 MB.")
                return
            extension = os.path.splitext(source)[1].lower()
            directory = os.path.join(self.user_data_dir, "content", content_type)
            os.makedirs(directory, exist_ok=True)
            destination = os.path.join(directory, f"{content_type}-{uuid4().hex}{extension}")
            try:
                shutil.copy2(source, destination)
            except OSError:
                popup.dismiss()
                self.show_message("Foto gagal disalin", "Periksa izin dan ruang penyimpanan perangkat.")
                return
            setattr(self, f"admin_{content_type}_image", destination)
            getattr(self, f"admin_{content_type}_image_label").text = os.path.basename(destination)
            popup.dismiss()

        select.bind(on_release=use_image)
        popup.open()

    def build_admin_users(self):
        screen = Screen(name="admin_users")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(
            self.section_header("Kelola Akun", "Data pengguna dan keamanan", "admin")
        )
        self.admin_users_summary = label(
            "0 akun terdaftar", 30, 12, COLORS["forest"], True, "center"
        )
        content.add_widget(self.admin_users_summary)
        self.admin_users_list = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(10)
        )
        self.admin_users_list.bind(
            minimum_height=self.admin_users_list.setter("height")
        )
        content.add_widget(self.admin_users_list)
        screen.add_widget(scroll)
        return screen

    def open_admin_users(self):
        if not self.admin_authenticated:
            self.request_admin_access()
            return
        self.refresh_admin_users()
        self.go("admin_users")

    def refresh_admin_users(self):
        users = self.database.list_users()
        self.admin_users_list.clear_widgets()
        active_count = sum(user["status"] == "active" for user in users)
        self.admin_users_summary.text = (
            f"{len(users)} akun terdaftar | {active_count} aktif"
        )
        if not users:
            self.admin_users_list.add_widget(
                self.info_card("Belum ada pengguna", "Akun yang mendaftar akan muncul di sini.", 120)
            )
            return
        for user in users:
            status_active = user["status"] == "active"
            card = Card(
                orientation="vertical",
                size_hint_y=None,
                height=dp(158),
                padding=dp(12),
                spacing=dp(3),
                background=COLORS["white"],
            )
            top = BoxLayout(size_hint_y=None, height=dp(34))
            top.add_widget(label(user["full_name"], 38, 15, COLORS["forest"], True))
            top.add_widget(
                label(
                    "AKTIF" if status_active else "NONAKTIF",
                    24,
                    9,
                    COLORS["sage"] if status_active else COLORS["terracotta"],
                    True,
                    "right",
                )
            )
            card.add_widget(top)
            card.add_widget(
                label(
                    f'@{user["username"]} | {user["phone"]}',
                    30,
                    10,
                    COLORS["muted"],
                )
            )
            last_login = (
                user["last_login"].replace("T", " ")
                if user["last_login"]
                else "Belum pernah login"
            )
            card.add_widget(
                label(
                    f'{user["booking_count"]} booking | Login: {last_login}',
                    32,
                    9,
                    COLORS["muted"],
                )
            )
            actions = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(7))
            status_button = GhostButton(
                text="Nonaktifkan" if status_active else "Aktifkan", height=dp(36)
            )
            status_button.bind(
                on_release=lambda _button, account=user: self.toggle_user_status(
                    account
                )
            )
            reset_button = PrimaryButton(text="Reset Password", height=dp(36))
            reset_button.bind(
                on_release=lambda _button, account=user: self.show_password_reset(
                    account
                )
            )
            actions.add_widget(status_button)
            actions.add_widget(reset_button)
            card.add_widget(actions)
            self.admin_users_list.add_widget(card)

    def toggle_user_status(self, user):
        new_status = "inactive" if user["status"] == "active" else "active"
        self.database.set_user_status(user["id"], new_status)
        self.refresh_admin_users()
        self.show_message(
            "Status akun diperbarui",
            f'Akun @{user["username"]} sekarang {"aktif" if new_status == "active" else "nonaktif"}.',
        )

    def show_password_reset(self, user):
        content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        content.add_widget(
            label(
                f'Tetapkan password sementara untuk @{user["username"]}.',
                48,
                12,
                COLORS["forest"],
                True,
                "center",
            )
        )
        password_input = StyledTextInput(
            hint_text="Password sementara minimal 8 karakter",
            multiline=False,
            password=True,
        )
        confirmation_input = StyledTextInput(
            hint_text="Ulangi password sementara",
            multiline=False,
            password=True,
        )
        content.add_widget(password_input)
        content.add_widget(confirmation_input)
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        close_button = GhostButton(text="Batal", height=dp(42))
        save_button = PrimaryButton(text="Simpan Password", height=dp(42))
        actions.add_widget(close_button)
        actions.add_widget(save_button)
        content.add_widget(actions)
        popup = Popup(
            title="Reset Password Pengguna",
            content=content,
            size_hint=(0.92, None),
            height=dp(330),
        )
        close_button.bind(on_release=popup.dismiss)

        def reset(*_args):
            password = password_input.text
            if len(password) < 8 or password != confirmation_input.text:
                password_input.text = ""
                confirmation_input.text = ""
                password_input.hint_text = "Minimal 8 karakter dan harus sama"
                return
            try:
                self.database.reset_user_password(user["id"], password)
            except PasswordError as error:
                popup.dismiss()
                self.show_message("Reset gagal", str(error))
                return
            popup.dismiss()
            self.show_message(
                "Password direset",
                "Berikan password sementara kepada pengguna melalui jalur pribadi.",
            )

        save_button.bind(on_release=reset)
        popup.open()

    def build_operations(self):
        screen = Screen(name="operations")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=10)
        content.add_widget(self.section_header("Kelola Operasional", "Perbarui informasi harian kolam", "admin"))
        content.add_widget(section_heading("Status publik", "Informasi ini akan dilihat oleh pengunjung"))
        content.add_widget(label("Status pemancingan", 28, 13, COLORS["forest"], True))
        self.operation_status = StyledSpinner(
            text=self.operational_status["venue_status"],
            values=("Buka", "Tutup sementara"),
        )
        content.add_widget(self.operation_status)
        content.add_widget(label("Mood ikan nila", 28, 13, COLORS["forest"], True))
        self.operation_mood = StyledSpinner(
            text=self.operational_status["fish_mood"],
            values=("Aktif / nafsu makan", "Biasa", "Kurang aktif"),
        )
        content.add_widget(self.operation_mood)
        content.add_widget(section_heading("Catatan lapangan", "Perbarui jumlah tebar dan kondisi kolam"))
        content.add_widget(label("Jumlah pelepasan hari ini (kg)", 28, 13, COLORS["forest"], True))
        self.operation_release = StyledTextInput(
            text=self.operational_status["daily_release_kg"],
            multiline=False,
            input_filter="int",
        )
        content.add_widget(self.operation_release)
        content.add_widget(label("Catatan petugas", 28, 13, COLORS["forest"], True))
        self.operation_note = StyledTextInput(
            text=self.operational_status["operator_note"],
            multiline=True,
            height=dp(105),
        )
        content.add_widget(self.operation_note)
        save = PrimaryButton(text="Simpan Informasi Harian")
        save.bind(on_release=lambda *_: self.save_operations())
        content.add_widget(save)
        screen.add_widget(scroll)
        return screen

    def save_operations(self):
        release = self.operation_release.text.strip() or "0"
        values = {
            "venue_status": self.operation_status.text,
            "fish_mood": self.operation_mood.text,
            "daily_release_kg": release,
            "operator_note": self.operation_note.text.strip(),
        }
        try:
            self.database.set_settings(values)
        except sqlite3.DatabaseError:
            self.show_message(
                "Gagal menyimpan", "Informasi operasional belum dapat disimpan."
            )
            return
        self.operational_status.update(values)
        self.refresh_operational_labels()
        self.show_message("Informasi disimpan", f"Status {self.operation_status.text}, mood {self.operation_mood.text}, pelepasan {release} kg nila.")

    def refresh_operational_labels(self):
        if hasattr(self, "home_status_label"):
            self.home_status_label.text = self.operational_status[
                "venue_status"
            ].upper()
        if hasattr(self, "home_hours_label"):
            self.home_hours_label.text = self.operational_status["opening_hours"]
        if hasattr(self, "home_release_label"):
            self.home_release_label.text = (
                f'{self.operational_status["daily_release_kg"]} kg'
            )
        if hasattr(self, "home_mood_label"):
            self.home_mood_label.text = self.operational_status["fish_mood"].split(
                " /"
            )[0].upper()
        if hasattr(self, "daily_mood_label"):
            self.daily_mood_label.text = (
                f'IKAN {self.operational_status["fish_mood"].upper()}'
            )
            self.daily_venue_label.text = (
                f'Status kolam: {self.operational_status["venue_status"]}'
            )
            self.daily_release_label.text = (
                f'{self.operational_status["daily_release_kg"]} kg'
            )
            self.daily_note_label.text = self.operational_status["operator_note"]

    def create_database_backup(self):
        destination = os.path.join(self.user_data_dir, "backups")
        try:
            backup_path = self.database.backup(destination)
        except (OSError, sqlite3.DatabaseError):
            self.show_message(
                "Backup gagal", "Database belum dapat disalin. Periksa ruang penyimpanan."
            )
            return
        self.show_message(
            "Backup berhasil", f"Salinan database dibuat di:\n{backup_path}"
        )

    def request_admin_access(self):
        if self.admin_authenticated:
            self.go("admin")
            return
        configured_pin = os.environ.get("ADEM_AYEM_ADMIN_PIN", "").strip()
        if len(configured_pin) < 6:
            self.show_message(
                "Admin belum dikonfigurasi",
                "Atur environment ADEM_AYEM_ADMIN_PIN minimal 6 digit sebelum menjalankan aplikasi admin.",
            )
            return

        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(
            label(
                "Masukkan PIN pengelola untuk membuka data dan pengaturan operasional.",
                66,
                11,
                COLORS["muted"],
                False,
                "center",
            )
        )
        pin_input = StyledTextInput(
            hint_text="6 digit atau lebih",
            multiline=False,
            password=True,
            input_filter="int",
            input_type="number",
        )
        content.add_widget(pin_input)
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        close_button = GhostButton(text="Batal", height=dp(42))
        login_button = PrimaryButton(text="Buka Admin", height=dp(42))
        actions.add_widget(close_button)
        actions.add_widget(login_button)
        content.add_widget(actions)
        popup = Popup(
            title="Akses Pengelola",
            content=content,
            size_hint=(0.88, None),
            height=dp(285),
        )
        close_button.bind(on_release=popup.dismiss)

        def login(*_args):
            if not hmac.compare_digest(pin_input.text, configured_pin):
                pin_input.text = ""
                pin_input.hint_text = "PIN salah, coba kembali"
                pin_input.focus = True
                return
            self.admin_authenticated = True
            popup.dismiss()
            self.go("admin")

        login_button.bind(on_release=login)
        pin_input.bind(on_text_validate=login)
        popup.open()
        Clock.schedule_once(lambda *_: setattr(pin_input, "focus", True), 0.1)

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
        for title, action in (
            ("Status", lambda: self.go("daily_status")),
            ("Pesanan", lambda: self.go("orders")),
            ("Privasi", lambda: self.go("legal")),
            ("Admin", lambda: self.request_admin_access()),
        ):
            menu_button = GhostButton(text=title, height=dp(44))
            menu_button.bind(on_release=lambda _button, callback=action: callback())
            more_menu.add_widget(menu_button)
        content.add_widget(more_menu)
        screen.add_widget(scroll)
        return screen

    def build_legal(self):
        screen = Screen(name="legal")
        scroll, content = page_content(padding=(14, 12, 14, 28), spacing=11)
        content.add_widget(
            self.section_header("Privasi & Ketentuan", "Informasi penggunaan aplikasi", "info")
        )
        content.add_widget(
            self.info_card(
                "Data yang disimpan",
                "Aplikasi menyimpan nama, nomor WhatsApp, pilihan event, nomor lapak, catatan, metode pembayaran, dan kode booking untuk memproses pesanan.",
                165,
                COLORS["mint"],
            )
        )
        content.add_widget(
            self.info_card(
                "Penyimpanan & akses",
                "Pada versi Kivy ini data tersimpan di perangkat pemancingan. Data hanya digunakan untuk operasional Pemancingan Adem Ayem Dlopo dan tidak dijual kepada pihak lain.",
                175,
            )
        )
        content.add_widget(
            self.info_card(
                "Ketentuan pemesanan",
                "Satu tiket berlaku untuk satu lapak. Peserta wajib memberikan data yang benar, mematuhi aturan umpan alami, dan menunjukkan tiket saat check-in. Pembatalan tiket berbayar harus melalui admin.",
                190,
                COLORS["sand"],
            )
        )
        content.add_widget(
            self.info_card(
                "Kontak pengelola",
                "Untuk koreksi data, pembatalan pembayaran, atau pertanyaan privasi, hubungi langsung pengelola Pemancingan Adem Ayem Dlopo.",
                145,
            )
        )
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
        card.title_label = label(title, 34, 18, COLORS["forest"], True)
        card.body_label = label(body, dp(height - 60), 12, COLORS["muted"])
        card.add_widget(card.title_label)
        card.add_widget(card.body_label)
        return card

    def go(self, screen_name):
        if screen_name == "orders":
            self.refresh_orders()
        if screen_name == "profile":
            self.refresh_profile()
        if screen_name == "admin":
            self.refresh_admin_metrics()
        self.manager.current = screen_name
        primary_screens = {"home", "events", "gallery", "leaderboard", "profile"}
        if hasattr(self, "navigation"):
            show_navigation = screen_name in primary_screens
            self.navigation.height = dp(68) if show_navigation else 0
            self.navigation.opacity = 1 if show_navigation else 0
            self.navigation.disabled = not show_navigation
        if hasattr(self, "nav_buttons"):
            for name, button in self.nav_buttons.items():
                active = name == screen_name
                button.set_active(active)

    def on_stop(self):
        if hasattr(self, "hero_clock"):
            self.hero_clock.cancel()

    def remaining_spots(self, event_id):
        return self.database.remaining_spots(event_id)

    def refresh_availability(self):
        for event_id, availability_label in getattr(
            self, "event_availability_labels", {}
        ).items():
            event = EVENTS.get(event_id)
            if not event:
                continue
            availability_label.text = (
                f'{self.remaining_spots(event_id)} dari {event["quota"]} lapak tersisa'
            )
        if hasattr(self, "home_availability_label"):
            event_id = self.first_event_id()
            if event_id:
                self.home_availability_label.text = (
                    f'{self.remaining_spots(event_id)} dari {EVENTS[event_id]["quota"]} lapak tersisa'
                )
        if (
            hasattr(self, "detail_quota")
            and getattr(self, "detail_event_id", None) in EVENTS
        ):
            event_id = self.detail_event_id
            self.detail_quota.value_label.text = (
                f'{self.remaining_spots(event_id)}/{EVENTS[event_id]["quota"]}'
            )

    def start_booking(self, event_id):
        if not event_id or event_id not in EVENTS:
            self.show_message("Belum ada event", "Saat ini belum ada event aktif yang dapat dipesan.")
            return
        if not self.current_user:
            self.pending_booking_event_id = event_id
            self.auth_context_label.text = (
                f'Masuk untuk memilih lapak dan memesan {EVENTS[event_id]["title"]}.'
            )
            self.go("auth")
            return
        event = EVENTS[event_id]
        self.current_event_id = event_id
        self.selected_spot = None
        self.occupied_spots = self.database.occupied_spots(event_id)
        remaining_spots = self.remaining_spots(event_id)
        if remaining_spots <= 0:
            self.show_message(
                "Lapak penuh",
                "Seluruh 82 lapak pada event ini sudah terisi. Silakan pilih event lain.",
            )
            return
        self.spot_event_title.text = event["title"]
        self.spot_event_meta.text = f'{event["date"]} | {rupiah(event["price"])} | {remaining_spots}/82 tersedia'
        self.selected_spot_label.text = "Belum memilih lapak"
        self.spot_price_label.text = rupiah(event["price"])
        for number, button in self.spot_buttons.items():
            button.set_status("occupied" if number in self.occupied_spots else "available")
        self.booking_image.source = media_source(event["image"])
        self.booking_title.text = event["title"]
        self.booking_schedule.text = f'{event["date"]}\n{event["time"]}'
        self.booking_release.text = event["release"]
        self.bait_checkbox.active = False
        self.customer_name.text = self.current_user["full_name"]
        self.customer_phone.text = self.current_user["phone"]
        self.customer_notes.text = ""
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
        event = self.event_for(self.current_event_id)
        self.payment_event_label.text = event["title"]
        self.payment_spot_label.text = f"Lapak {self.selected_spot:02d} | 1 tiket"
        self.payment_customer_label.text = f"Pemesan: {name} | {phone}"
        self.payment_schedule_label.text = f'{event["date"]}\n{event["time"]}'
        notes = self.customer_notes.text.strip()
        self.payment_notes_label.text = f"Catatan: {notes or '-'}"
        self.payment_ticket_price.text = f'Tiket: {rupiah(event["price"])}'
        self.update_payment_total()
        self.go("payment")

    def update_payment_total(self):
        if not self.current_event_id:
            return
        fee = 0 if self.payment_method.text == "Bayar di lokasi" else 2_500
        price = self.event_for(self.current_event_id)["price"]
        self.payment_fee.text = f"Biaya layanan: {rupiah(fee)}"
        self.payment_total_label.text = f"Total: {rupiah(price + fee)}"

    def show_booking_confirmation(self):
        if not self.current_event_id or not self.selected_spot:
            self.show_message(
                "Pesanan belum siap", "Pilih event dan lapak sebelum membuat tiket."
            )
            return
        event = self.event_for(self.current_event_id)
        fee = 0 if self.payment_method.text == "Bayar di lokasi" else 2_500
        total = event["price"] + fee
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(
            label(
                f'{event["title"]}\nLapak {self.selected_spot:02d}\n{self.payment_method.text}\nTotal {rupiah(total)}',
                116,
                14,
                COLORS["forest"],
                True,
                "center",
            )
        )
        content.add_widget(
            label(
                "Setelah dikonfirmasi, lapak langsung tercatat dan tidak dapat dipilih pemancing lain.",
                64,
                10,
                COLORS["muted"],
                False,
                "center",
            )
        )
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        cancel_button = GhostButton(text="Periksa Lagi", height=dp(42))
        confirm_button = PrimaryButton(text="Ya, Buat Tiket", height=dp(42))
        actions.add_widget(cancel_button)
        actions.add_widget(confirm_button)
        content.add_widget(actions)
        popup = Popup(
            title="Konfirmasi Pemesanan",
            content=content,
            size_hint=(0.9, None),
            height=dp(345),
        )
        cancel_button.bind(on_release=popup.dismiss)

        def confirm(*_args):
            popup.dismiss()
            self.submit_booking()

        confirm_button.bind(on_release=confirm)
        popup.open()

    def submit_booking(self):
        name = self.customer_name.text.strip()
        phone = self.customer_phone.text.strip()
        if (
            self.current_event_id not in EVENTS
            or not self.selected_spot
            or len(name) < 3
            or len(phone) < 9
            or not self.bait_checkbox.active
        ):
            self.show_message(
                "Pesanan belum lengkap",
                "Periksa kembali event, lapak, data pemesan, dan persetujuan aturan.",
            )
            return
        event = self.event_for(self.current_event_id)

        booking_code = "AA-" + uuid4().hex[:6].upper()
        method = self.payment_method.text
        fee = 0 if method == "Bayar di lokasi" else 2_500
        total = event["price"] + fee
        status = "pay_at_venue" if method == "Bayar di lokasi" else "paid"
        booking = {
            "booking_code": booking_code,
            "event_id": self.current_event_id,
            "customer_name": name,
            "customer_phone": phone,
            "customer_notes": self.customer_notes.text.strip(),
            "ticket_count": 1,
            "payment_method": method,
            "total_amount": total,
            "payment_status": status,
            "spot_number": self.selected_spot,
            "bait_rule_accepted": True,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "payment_reference": "SIM-" + uuid4().hex[:10].upper(),
            "user_id": self.current_user["id"],
        }
        self.pay_button.disabled = True
        self.pay_button.text = "Menyimpan Pesanan..."
        try:
            self.database.create_booking(booking)
        except BookingConflictError:
            self.occupied_spots = self.database.occupied_spots(self.current_event_id)
            for number, button in self.spot_buttons.items():
                button.set_status(
                    "occupied" if number in self.occupied_spots else "available"
                )
            self.show_message(
                "Lapak sudah terisi",
                "Lapak ini baru saja dipesan. Silakan kembali dan pilih lapak lain.",
            )
            return
        except sqlite3.DatabaseError:
            self.show_message(
                "Pesanan belum tersimpan",
                "Terjadi kendala saat menyimpan data. Silakan coba kembali.",
            )
            return
        finally:
            self.pay_button.disabled = False
            self.pay_button.text = "Konfirmasi & Buat Tiket"

        self.session_bookings = self.database.list_bookings(
            user_id=self.current_user["id"]
        )
        self.refresh_availability()
        self.render_ticket(booking)
        self.customer_name.text = ""
        self.customer_phone.text = ""
        self.customer_notes.text = ""
        self.go("ticket")

    def render_ticket(self, booking):
        event = self.event_for(booking["event_id"])
        self.current_ticket_booking = booking
        self.current_event_id = booking["event_id"]
        self.selected_spot = booking["spot_number"]
        self.ticket_event.text = event["title"]
        self.ticket_code.text = booking["booking_code"]
        self.ticket_qr.set_code(booking["booking_code"])
        spot_text = (
            f'Lapak {booking["spot_number"]:02d}'
            if booking["spot_number"] is not None
            else "Lapak belum tercatat"
        )
        self.ticket_detail.text = (
            f'{event["date"]}\n'
            f'{spot_text} | {rupiah(booking["total_amount"])}\n'
            f'{booking["customer_name"]} | {booking["payment_method"]}'
        )
        self.ticket_status.text = payment_status_text(
            booking["payment_status"]
        ).upper()

    def open_saved_ticket(self, booking):
        self.render_ticket(booking)
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
