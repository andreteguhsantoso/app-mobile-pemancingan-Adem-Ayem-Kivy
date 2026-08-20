import os
from kivy.config import Config

# Resolusi Layar Standar Wireframe (Aspect Ratio HP Modern)
Config.set('graphics', 'width', '380')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button

# Warna Dasar Aplikasi Background (Abu-abu sangat terang)
Window.clearcolor = (0.97, 0.97, 0.97, 1)

# KV Design Language - Clean & Rich Detail Syntax with Unified Logo/Icons
KV_DESIGN = '''
#:import SlideTransition kivy.uix.screenmanager.SlideTransition

# --- KOMPONEN REUSABLE GLOBAL ---
<NavButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    markup: True
    color: (0.05, 0.29, 0.34, 1) if self.state == 'normal' else (0.12, 0.55, 0.62, 1)
    font_size: '10sp'
    halign: 'center'
    valign: 'middle'

<BottomNav@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '56dp'
    padding: 0, 4
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0.85, 0.85, 0.85, 1
        Line:
            points: [self.x, self.y + self.height, self.x + self.width, self.y + self.height]
            width: 1

    NavButton:
        text: "🏠\\nBeranda"
        on_release: app.switch_screen('home')
    NavButton:
        text: "📅\\nJadwal"
        on_release: app.switch_screen('jadwal')
    NavButton:
        text: "🎣\\nBooking"
        on_release: app.switch_screen('booking')
    NavButton:
        text: "🛍️\\nToko"
        on_release: app.switch_screen('toko')
    NavButton:
        text: "👤\\nProfil"
        on_release: app.switch_screen('profil')


# ==========================================
# 1. BERANDA (HOME - DASHBOARD)
# ==========================================
<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'

        # HEADER TEAL
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 15, 0
            spacing: '10dp'
            canvas.before:
                Color:
                    rgba: 0.05, 0.29, 0.34, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "🐟 Adem Ayem Dlopo"
                font_size: '15sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'middle'
            Button:
                text: "🔔 Info"
                size_hint: None, None
                size: '60dp', '30dp'
                pos_hint: {'center_y': 0.5}
                background_normal: ''
                background_color: 0.12, 0.45, 0.52, 1
                font_size: '10sp'
                bold: True
                on_release: app.tampilkan_popup("Pemberitahuan", "Kolam buka setiap hari pukul 08:00 - 22:00 WIB.\\nUmpan dilarang menggunakan pelet beracun.")
            AsyncImage:
                source: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop'
                size_hint: None, None
                size: '30dp', '30dp'
                pos_hint: {'center_y': 0.5}

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '15dp'
                spacing: '15dp'

                # HERO BANNER
                RelativeLayout:
                    size_hint_y: None
                    height: '170dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12,]
                    AsyncImage:
                        source: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&auto=format&fit=crop'
                        allow_stretch: True
                        keep_ratio: False
                    BoxLayout:
                        orientation: 'vertical'
                        padding: '15dp'
                        canvas.before:
                            Color:
                                rgba: 0, 0, 0, 0.45
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [12,]
                        Widget:
                        Label:
                            text: "SENSASI STRIKE JUARA"
                            font_size: '14sp'
                            bold: True
                            color: 1, 1, 1, 1
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "Grand Prix Kolam Karangrejo, Kediri"
                            font_size: '11sp'
                            color: 0.9, 0.9, 0.9, 1
                            halign: 'left'
                            text_size: self.size

                # MENU 4 KOTAK INTERAKTIF
                GridLayout:
                    cols: 4
                    size_hint_y: None
                    height: '85dp'
                    spacing: '10dp'
                    AnimatedCard:
                        text_label: "🎣\\nBOOKING\\nLAPAK"
                        bg_color: 0.26, 0.57, 0.94, 1
                        on_release: app.switch_screen('booking')
                    AnimatedCard:
                        text_label: "🏆\\nJADWAL\\nLOMBA"
                        bg_color: 0.41, 0.63, 0.30, 1
                        on_release: app.switch_screen('jadwal')
                    AnimatedCard:
                        text_label: "🛍️\\nTOKO\\nPANCING"
                        bg_color: 0.88, 0.65, 0.18, 1
                        on_release: app.switch_screen('toko')
                    AnimatedCard:
                        text_label: "👤\\nPROFIL\\nSAYA"
                        bg_color: 0.86, 0.33, 0.25, 1
                        on_release: app.switch_screen('profil')

                Label:
                    text: "🔥 Informasi & Pengumuman Penting"
                    font_size: '13sp'
                    bold: True
                    size_hint_y: None
                    height: '20dp'
                    color: 0.1, 0.1, 0.1, 1
                    halign: 'left'
                    text_size: self.size

                # KARTU INFO / EVENT TERDEKAT DENGAN DETAIL TAMBAHAN
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '115dp'
                    padding: 12
                    spacing: '5dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.8, 0.75, 0.65, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1.2
                    BoxLayout:
                        Label:
                            text: "🐟 Galatama Ikan Mas Spesial"
                            bold: True
                            color: 0.1, 0.1, 0.1, 1
                            font_size: '13sp'
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "📅 25 Nov"
                            color: 0.05, 0.29, 0.34, 1
                            bold: True
                            font_size: '11sp'
                            size_hint_x: None
                            width: '65dp'
                    Label:
                        text: "Hadiah Utama: Rp 10.000.000 + Piala Bergilir.\\nSesi: 14:00 - 18:00 WIB | Ikan Rame & Super Diturunkan."
                        color: 0.4, 0.4, 0.4, 1
                        font_size: '10sp'
                        halign: 'left'
                        text_size: self.size
                    AnchorLayout:
                        anchor_x: 'right'
                        Button:
                            text: "🎯 Daftar Lapak Sekarang"
                            size_hint: None, None
                            size: '160dp', '26dp'
                            background_normal: ''
                            background_color: (0.05, 0.29, 0.34, 1)
                            bold: True
                            font_size: '10sp'
                            on_release: app.switch_screen('pilih_lapak')

        BottomNav:


# ==========================================
# 2. PILIH KOLAM (BOOKING FLOW 1)
# ==========================================
<BookingScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 10, 0
            canvas.before:
                Color:
                    rgba: 0.05, 0.29, 0.34, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "↩️ Kembali"
                size_hint_x: None
                width: '85dp'
                background_color: 0,0,0,0
                color: 1,1,1,1
                font_size: '12sp'
                bold: True
                on_release: app.switch_screen('home')
            Label:
                text: "Pilih Kolam Pancing"
                bold: True
                font_size: '15sp'
                halign: 'center'
            Widget:
                size_hint_x: None
                width: '85dp'

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 15
                spacing: '15dp'

                # DETAIL KOLAM 1
                RelativeLayout:
                    size_hint_y: None
                    height: '160dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                    AsyncImage:
                        source: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&auto=format&fit=crop'
                        allow_stretch: True
                        keep_ratio: False
                    BoxLayout:
                        orientation: 'vertical'
                        padding: 12
                        canvas.before:
                            Color:
                                rgba: 0, 0, 0, 0.55
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [10,]
                        Label:
                            text: "🌊 Kolam Galatama Utama (Ikan Mas)"
                            bold: True
                            font_size: '13sp'
                            color: 1,1,1,1
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "• Sirkulasi air deras & oksigen tinggi\\n• Kapasitas: 16 Lapak Profesional\\n• Fasilitas: Kantin, Mushola, Parkir Luas"
                            font_size: '10sp'
                            color: 0.9, 0.9, 0.9, 1
                            halign: 'left'
                            text_size: self.size
                    Button:
                        text: "🎯 Pilih Lapak Galatama"
                        size_hint: None, None
                        size: '170dp', '32dp'
                        pos_hint: {'center_x': 0.5, 'y': 0.12}
                        background_normal: ''
                        background_color: 0.05, 0.29, 0.34, 1
                        color: 1,1,1,1
                        bold: True
                        font_size: '11sp'
                        on_release: app.switch_screen('pilih_lapak')

                # DETAIL KOLAM 2
                RelativeLayout:
                    size_hint_y: None
                    height: '160dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                    AsyncImage:
                        source: 'https://images.unsplash.com/photo-1516214104703-d870798883c5?w=600&auto=format&fit=crop'
                        allow_stretch: True
                        keep_ratio: False
                    BoxLayout:
                        orientation: 'vertical'
                        padding: 12
                        canvas.before:
                            Color:
                                rgba: 0, 0, 0, 0.55
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [10,]
                        Label:
                            text: "🌿 Kolam Harian / Santai (Bawal & Lele)"
                            bold: True
                            font_size: '13sp'
                            color: 1,1,1,1
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "• Cocok untuk rekreasi keluarga & pemula\\n• Sistem timbang bayar atau harian bebas\\n• Suasana teduh di bawah pepohonan"
                            font_size: '10sp'
                            color: 0.9, 0.9, 0.9, 1
                            halign: 'left'
                            text_size: self.size
                    Button:
                        text: "🔒 Segera Dibuka"
                        size_hint: None, None
                        size: '140dp', '32dp'
                        pos_hint: {'center_x': 0.5, 'y': 0.12}
                        background_normal: ''
                        background_color: 0.3, 0.3, 0.3, 0.8
                        color: 1,1,1,1
                        bold: True
                        font_size: '11sp'


# ==========================================
# 3. LAYOUT INTERAKTIF DENAH LAPAK (GRID)
# ==========================================
<PilihLapakScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 10, 0
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Line:
                    points: [self.x, self.y, self.x+self.width, self.y]
            Button:
                text: "↩️ Kolam"
                size_hint_x: None
                width: '80dp'
                color: 0,0,0,1
                background_color: 0,0,0,0
                font_size: '12sp'
                bold: True
                on_release: app.switch_screen('booking')
            Label:
                text: "Pilih Nomor Lapak (1-16)"
                color: 0,0,0,1
                font_size: '13sp'
                bold: True
                halign: 'left'
                text_size: self.size
                valign: 'middle'

        # Legend Box
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            padding: 15
            spacing: '15dp'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            BoxLayout:
                spacing: '5dp'
                Widget:
                    size_hint_x: None
                    width: '14dp'
                    canvas.before:
                        Color:
                            rgba: 0.2, 0.6, 0.2, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                Label:
                    text: "🟢 Tersedia"
                    color: 0,0,0,1
                    font_size: '11sp'
            BoxLayout:
                spacing: '5dp'
                Widget:
                    size_hint_x: None
                    width: '14dp'
                    canvas.before:
                        Color:
                            rgba: 0.8, 0.2, 0.2, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                Label:
                    text: "🔴 Terisi"
                    color: 0,0,0,1
                    font_size: '11sp'
            BoxLayout:
                spacing: '5dp'
                Widget:
                    size_hint_x: None
                    width: '14dp'
                    canvas.before:
                        Color:
                            rgba: 0.05, 0.29, 0.34, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                Label:
                    text: "🔵 Dipilih"
                    color: 0,0,0,1
                    font_size: '11sp'

        # Dinamis Grid Lapak 16 Buah
        ScrollView:
            GridLayout:
                id: lapak_grid
                cols: 4
                size_hint_y: None
                height: self.minimum_height
                padding: 20
                spacing: '12dp'

        # Bottom Bar Status & Action
        BoxLayout:
            size_hint_y: None
            height: '80dp'
            padding: 15
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Line:
                    points: [self.x, self.y+self.height, self.x+self.width, self.y+self.height]
            BoxLayout:
                orientation: 'vertical'
                Label:
                    id: info_lapak_dipilih
                    text: "Lapak Dipilih: Belum ada"
                    bold: True
                    color: 0,0,0,1
                    font_size: '12sp'
                    halign: 'left'
                    text_size: self.size
                Label:
                    id: info_harga_lapak
                    text: "Total Biaya: Rp 0"
                    color: 0.4,0.4,0.4,1
                    font_size: '11sp'
                    halign: 'left'
                    text_size: self.size
            Button:
                text: "💳 Lanjut Bayar"
                size_hint_x: None
                width: '140dp'
                background_normal: ''
                background_color: (0.05, 0.29, 0.34, 1)
                bold: True
                font_size: '11sp'
                on_release: app.lanjut_ke_pembayaran()


# ==========================================
# 4. JADWAL LOMBA DENGAN DETAIL LENGKAP
# ==========================================
<JadwalScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 15, 0
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "🏆 Jadwal Turnamen & Lomba"
                color: 0, 0, 0, 1
                font_size: '15sp'
                bold: True
                halign: 'center'

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 15
                spacing: '15dp'

                # Item Card 1
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '130dp'
                    padding: 12
                    spacing: '4dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                    BoxLayout:
                        Label:
                            text: "🐟 Grand Prix Ikan Mas Spesial"
                            color: 0,0,0,1
                            bold: True
                            font_size: '12sp'
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "📅 25 Nov"
                            color: 0.05, 0.29, 0.34, 1
                            bold: True
                            font_size: '11sp'
                            size_hint_x: None
                            width: '60dp'
                    Label:
                        text: "📍 Lokasi: Kolam Adem Ayem Dlopo, Kediri\\n🎁 Hadiah Utama: Rp 10.000.000 + Trophy\\n⏱️ Waktu: 14.00 - 18.00 WIB (Sesi Sore)"
                        color: 0.3, 0.3, 0.3, 1
                        font_size: '10sp'
                        halign: 'left'
                        text_size: self.size
                    AnchorLayout:
                        anchor_x: 'right'
                        Button:
                            text: "🎯 Booking Lapak"
                            size_hint: None, None
                            size: '120dp', '26dp'
                            background_normal: ''
                            background_color: 0.05, 0.29, 0.34, 1
                            font_size: '10sp'
                            bold: True
                            on_release: app.switch_screen('pilih_lapak')

                # Item Card 2
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '130dp'
                    padding: 12
                    spacing: '4dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                    BoxLayout:
                        Label:
                            text: "🐟 Festival Lele Galatama Bulanan"
                            color: 0,0,0,1
                            bold: True
                            font_size: '12sp'
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "📅 02 Des"
                            color: 0.05, 0.29, 0.34, 1
                            bold: True
                            font_size: '11sp'
                            size_hint_x: None
                            width: '60dp'
                    Label:
                        text: "📍 Lokasi: Kolam Adem Ayem Dlopo, Kediri\\n🎁 Hadiah Utama: Rp 5.000.000 + Doorprize\\n⏱️ Waktu: 09.00 - 13.00 WIB (Sesi Pagi)"
                        color: 0.3, 0.3, 0.3, 1
                        font_size: '10sp'
                        halign: 'left'
                        text_size: self.size
                    AnchorLayout:
                        anchor_x: 'right'
                        Button:
                            text: "🎯 Booking Lapak"
                            size_hint: None, None
                            size: '120dp', '26dp'
                            background_normal: ''
                            background_color: 0.05, 0.29, 0.34, 1
                            font_size: '10sp'
                            bold: True
                            on_release: app.switch_screen('pilih_lapak')

        BottomNav:


# ==========================================
# 5. RINGKASAN PEMBAYARAN DENGAN DETAIL
# ==========================================
<PembayaranScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 10, 0
            canvas.before:
                Color:
                    rgba: 0.05, 0.29, 0.34, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "↩️ Lapak"
                size_hint_x: None
                width: '75dp'
                background_color: 0,0,0,0
                color: 1,1,1,1
                font_size: '12sp'
                bold: True
                on_release: app.switch_screen('pilih_lapak')
            Label:
                text: "Ringkasan Pembayaran"
                bold: True
                font_size: '15sp'
                halign: 'left'
                text_size: self.size
                valign: 'middle'

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 20
                spacing: '15dp'

                BoxLayout:
                    size_hint_y: None
                    height: '90dp'
                    padding: 10
                    spacing: '12dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                    Label:
                        text: "🎣"
                        font_size: '28sp'
                        size_hint_x: None
                        width: '40dp'
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            id: pay_summary_title
                            text: "Kolam Galatama - Lapak Dipilih"
                            bold: True
                            color: 0.1, 0.1, 0.1, 1
                            font_size: '12sp'
                            halign: 'left'
                            text_size: self.size
                        Label:
                            text: "Sesi: 14:00 - 18:00 WIB\\nTermasuk: Tiket Lomba & Konsumsi Ringan"
                            color: 0.4, 0.4, 0.4, 1
                            font_size: '10sp'
                            halign: 'left'
                            text_size: self.size
                            valign: 'top'

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '55dp'
                    Label:
                        text: "Total Tagihan Pembayaran"
                        font_size: '11sp'
                        color: 0.4, 0.4, 0.4, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        id: pay_summary_total
                        text: "Rp 500.000"
                        font_size: '22sp'
                        bold: True
                        color: 0, 0, 0, 1
                        halign: 'left'
                        text_size: self.size

                Label:
                    text: "Metode Pembayaran Tersedia"
                    font_size: '12sp'
                    bold: True
                    color: 0.2, 0.2, 0.2, 1
                    size_hint_y: None
                    height: '20dp'
                    halign: 'left'
                    text_size: self.size

                # QRIS Box Selected
                BoxLayout:
                    size_hint_y: None
                    height: '45dp'
                    padding: 10
                    canvas.before:
                        Color:
                            rgba: 0.85, 0.95, 0.95, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8,]
                        Color:
                            rgba: 0.05, 0.29, 0.34, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 8]
                            width: 1.2
                    Label:
                        text: "📱 QRIS / GoPay / OVO / Dana / Transfer Bank"
                        color: 0.05, 0.29, 0.34, 1
                        bold: True
                        font_size: '11sp'
                        halign: 'left'
                        text_size: self.size
                        valign: 'middle'

        # Bottom Action Bar
        BoxLayout:
            size_hint_y: None
            height: '75dp'
            padding: 15
            orientation: 'vertical'
            spacing: '5dp'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            AnchorLayout:
                anchor_x: 'right'
                Button:
                    text: "🔒 Konfirmasi & Bayar Sekarang"
                    size_hint_x: None
                    width: '250dp'
                    height: '38dp'
                    background_normal: ''
                    background_color: (0.05, 0.29, 0.34, 1)
                    bold: True
                    font_size: '11sp'
                    on_release: app.proses_pembayaran()
            Label:
                text: "⏱️ Batas waktu konfirmasi otomatis 60 menit"
                font_size: '10sp'
                color: 0.4, 0.4, 0.4, 1


# ==========================================
# 6. TOKO PANCING DENGAN DETAIL PRODUK
# ==========================================
<TokoScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            padding: 15, 0
            canvas.before:
                Color:
                    rgba: 0.05, 0.29, 0.34, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "🛍️ Toko Resmi Adem Ayem"
                bold: True
                color: 1, 1, 1, 1
                font_size: '15sp'
                halign: 'center'
                text_size: self.size
                valign: 'middle'

        ScrollView:
            GridLayout:
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                padding: 15
                spacing: '15dp'

                # PRODUCT 1
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '210dp'
                    padding: 8
                    spacing: '4dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.85, 0.85, 0.85, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                    AsyncImage:
                        source: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=300&auto=format&fit=crop'
                        allow_stretch: True
                        keep_ratio: False
                    Label:
                        text: "Jersey Mancing Eksklusif"
                        font_size: '11sp'
                        color: 0,0,0,1
                        bold: True
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: '18dp'
                    Label:
                        text: "Rp 175.000"
                        font_size: '11sp'
                        bold: True
                        color: 0.05, 0.29, 0.34, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: '18dp'
                    Button:
                        text: "🔍 Lihat Detail"
                        size_hint_y: None
                        height: '30dp'
                        background_normal: ''
                        background_color: 0.05, 0.29, 0.34, 1
                        bold: True
                        font_size: '10sp'
                        on_release: app.switch_screen('detail_toko')

                # PRODUCT 2
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '210dp'
                    padding: 8
                    spacing: '4dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                        Color:
                            rgba: 0.85, 0.85, 0.85, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                    AsyncImage:
                        source: 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=300&auto=format&fit=crop'
                        allow_stretch: True
                        keep_ratio: False
                    Label:
                        text: "Topi Snapback Mancing"
                        font_size: '11sp'
                        color: 0,0,0,1
                        bold: True
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: '18dp'
                    Label:
                        text: "Rp 95.000"
                        font_size: '11sp'
                        bold: True
                        color: 0.05, 0.29, 0.34, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: '18dp'
                    Button:
                        text: "🔍 Lihat Detail"
                        size_hint_y: None
                        height: '30dp'
                        background_normal: ''
                        background_color: 0.3, 0.3, 0.3, 0.8
                        bold: True
                        font_size: '10sp'
                        on_release: app.tampilkan_popup("Info Produk", "Topi Snapback anti panas sedang kosong.\\nStok baru akan tiba hari Senin.")

        BottomNav:


# ==========================================
# 7. DETAIL PRODUK & INTERACTIVE COUNTER
# ==========================================
<DetailTokoScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        RelativeLayout:
            size_hint_y: None
            height: '230dp'
            canvas.before:
                Color:
                    rgba: 0.05, 0.29, 0.34, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            AsyncImage:
                source: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop'
                allow_stretch: True
                keep_ratio: False
                opacity: 0.85
            Button:
                text: "↩️ Toko"
                size_hint: None, None
                size: '75dp', '35dp'
                pos_hint: {'x': 0.02, 'top': 0.95}
                background_color: 0,0,0,0
                color: 1,1,1,1
                font_size: '12sp'
                bold: True
                on_release: app.switch_screen('toko')

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 20
                spacing: '12dp'

                Label:
                    text: "Jersey Mancing Eksklusif Dlopo"
                    font_size: '16sp'
                    bold: True
                    color: 0, 0, 0, 1
                    size_hint_y: None
                    height: '24dp'
                    halign: 'left'
                    text_size: self.size

                Label:
                    text: "Rp 175.000"
                    font_size: '15sp'
                    bold: True
                    color: 0.05, 0.29, 0.34, 1
                    size_hint_y: None
                    height: '24dp'
                    halign: 'left'
                    text_size: self.size

                Label:
                    text: "Detail Spesifikasi:\\n• Bahan: Dry-fit Premium Anti UV\\n• Fitur: Cepat kering, tidak panas saat dipakai seharian di pinggir kolam.\\n• Ukuran Tersedia: M, L, XL, XXL"
                    font_size: '11sp'
                    color: 0.4, 0.4, 0.4, 1
                    size_hint_y: None
                    height: '75dp'
                    halign: 'left'
                    text_size: self.size
                    valign: 'top'

                # Quantity Controller Interactive
                BoxLayout:
                    size_hint_y: None
                    height: '40dp'
                    spacing: '10dp'
                    Label:
                        text: "Jumlah Pesanan:"
                        color: 0,0,0,1
                        bold: True
                        size_hint_x: None
                        width: '115dp'
                        halign: 'left'
                        text_size: self.size
                    Button:
                        text: "➖"
                        size_hint_x: None
                        width: '38dp'
                        background_normal: ''
                        background_color: 0.8, 0.8, 0.8, 1
                        color: 0,0,0,1
                        bold: True
                        on_release: app.kurang_qty()
                    Label:
                        id: label_qty
                        text: "1"
                        color: 0, 0, 0, 1
                        bold: True
                        size_hint_x: None
                        width: '30dp'
                        halign: 'center'
                    Button:
                        text: "➕"
                        size_hint_x: None
                        width: '38dp'
                        background_normal: ''
                        background_color: 0.8, 0.8, 0.8, 1
                        color: 0,0,0,1
                        bold: True
                        on_release: app.tambah_qty()

                BoxLayout:
                    size_hint_y: None
                    height: '30dp'
                    Label:
                        text: "Subtotal Harga Produk"
                        color: 0.4,0.4,0.4,1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        id: label_subtotal_toko
                        text: "Rp 175.000"
                        color: 0,0,0,1
                        bold: True
                        halign: 'right'
                        text_size: self.size

        BoxLayout:
            size_hint_y: None
            height: '65dp'
            padding: 12
            spacing: '10dp'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "⚡ Beli Langsung"
                background_normal: ''
                background_color: 0.88, 0.65, 0.18, 1
                color: 1,1,1,1
                bold: True
                font_size: '11sp'
                on_release: app.switch_screen('pembayaran')
            Button:
                text: "🛒+ Keranjang"
                background_normal: ''
                background_color: (0.05, 0.29, 0.34, 1)
                bold: True
                font_size: '11sp'
                color: 1,1,1,1
                on_release: app.tambah_keranjang_popup()


# ==========================================
# 8. PROFIL SAYA DENGAN DETAIL ANGGOTA
# ==========================================
<ProfilScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.29, 0.34, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        RelativeLayout:
            size_hint_y: None
            height: '55dp'
            Label:
                text: "👤 Profil Anggota Mancing"
                bold: True
                color: 1, 1, 1, 1
                font_size: '15sp'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: '130dp'
            spacing: '5dp'
            AsyncImage:
                source: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop'
                size_hint: None, None
                size: '65dp', '65dp'
                pos_hint: {'center_x': 0.5}
            Label:
                text: "Budi Santoso (Mbah Yo Dlopo)"
                bold: True
                font_size: '15sp'
                color: 1, 1, 1, 1
                size_hint_y: None
                height: '20dp'
            Label:
                text: "ID Anggota: MA-012345 | Kediri, Jatim"
                font_size: '11sp'
                color: 0.8, 0.8, 0.8, 1
                size_hint_y: None
                height: '15dp'

        BoxLayout:
            orientation: 'vertical'
            padding: 20, 15, 20, 0
            spacing: '12dp'
            canvas.before:
                Color:
                    rgba: 0.97, 0.97, 0.97, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20, 20, 0, 0]

            RelativeLayout:
                size_hint_y: None
                height: '130dp'
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15,]
                    Color:
                        rgba: 0.88, 0.65, 0.18, 0.2
                    RoundedRectangle:
                        pos: self.x, self.y
                        size: self.width, self.height/2
                        radius: [0, 0, 15, 15]
                Label:
                    text: "👑 Member VIP Gold"
                    color: 0.88, 0.65, 0.18, 1
                    bold: True
                    font_size: '13sp'
                    pos_hint: {'x': 0.05, 'top': 0.92}
                    size_hint: None, None
                    size: '130dp', '20dp'
                    halign: 'left'
                    text_size: self.size
                Label:
                    text: "⭐"
                    pos_hint: {'right': 0.95, 'top': 0.92}
                    size_hint: None, None
                    size: '30dp', '20dp'
                Label:
                    text: "Poin Loyalitas: 1.250 Pts\\nStatus Akun: Aktif & Terverifikasi"
                    color: 1,1,1,1
                    bold: True
                    font_size: '11sp'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.45}
                    size_hint: None, None
                    size: '220dp', '35dp'
                    halign: 'center'
                    text_size: self.size

            BoxLayout:
                orientation: 'vertical'
                spacing: '8dp'
                
                Button:
                    size_hint_y: None
                    height: '38dp'
                    background_normal: ''
                    background_color: 0,0,0,0
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8,]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 8]
                    Label:
                        text: "📋 Riwayat Booking Lapak Saya"
                        color: 0,0,0,1
                        font_size: '11sp'
                        pos: self.pos
                        size: self.size
                        halign: 'left'
                        padding: 15, 0
                        valign: 'middle'

                Button:
                    size_hint_y: None
                    height: '38dp'
                    background_normal: ''
                    background_color: 0,0,0,0
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8,]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 8]
                    Label:
                        text: "📦 Status Pesanan Toko Pancing"
                        color: 0,0,0,1
                        font_size: '11sp'
                        pos: self.pos
                        size: self.size
                        halign: 'left'
                        padding: 15, 0
                        valign: 'middle'

            Widget:

            Button:
                text: "🚪 Keluar dari Aplikasi"
                size_hint_y: None
                height: '38dp'
                background_normal: ''
                background_color: 0.8, 0.2, 0.2, 1
                color: 1,1,1,1
                bold: True
                font_size: '11sp'
                on_release: app.stop()

        Widget:
            size_hint_y: None
            height: '10dp'
            canvas.before:
                Color:
                    rgba: 0.97, 0.97, 0.97, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
'''


class AnimatedCard(BoxLayout):
    def __init__(self, text_label="CARD", bg_color=(0.12, 0.52, 0.75, 1), **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_release')
        self.orientation = 'vertical'
        self.padding = '5dp'
        
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            self.bg_color_instruction = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10,])
            Color(0.1, 0.1, 0.1, 1)
            self.border = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 10], width=1.1)
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        from kivy.uix.label import Label
        self.lbl = Label(text=text_label, font_size='10sp', bold=True, color=(1,1,1,1), halign='center', valign='middle')
        self.lbl.bind(size=self.lbl.setter('text_size'))
        self.add_widget(self.lbl)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rounded_rectangle = [self.x, self.y, self.width, self.height, 10]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size_hint=(0.95, 0.95), duration=0.08)
            anim.start(self)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            anim = Animation(size_hint=(1.0, 1.0), duration=0.08)
            anim.start(self)
            if self.collide_point(*touch.pos):
                self.dispatch('on_release')
            return True
        return super().on_touch_up(touch)

    def on_release(self):
        pass


class HomeScreen(Screen): pass
class BookingScreen(Screen): pass
class PilihLapakScreen(Screen): pass
class JadwalScreen(Screen): pass
class PembayaranScreen(Screen): pass
class TokoScreen(Screen): pass
class DetailTokoScreen(Screen): pass
class ProfilScreen(Screen): pass


class AppMancing(App):
    screen_order = ['home', 'jadwal', 'booking', 'pilih_lapak', 'pembayaran', 'toko', 'detail_toko', 'profil']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_lapak = None
        self.harga_per_lapak = 500000
        self.qty_produk = 1
        self.harga_satuan_produk = 175000

    def build(self):
        Builder.load_string(KV_DESIGN)
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(BookingScreen(name='booking'))
        self.sm.add_widget(PilihLapakScreen(name='pilih_lapak'))
        self.sm.add_widget(JadwalScreen(name='jadwal'))
        self.sm.add_widget(PembayaranScreen(name='pembayaran'))
        self.sm.add_widget(TokoScreen(name='toko'))
        self.sm.add_widget(DetailTokoScreen(name='detail_toko'))
        self.sm.add_widget(ProfilScreen(name='profil'))
        return self.sm

    def on_start(self):
        # Inisialisasi Grid Lapak Interaktif (16 Lapak) di PilihLapakScreen
        pilih_screen = self.sm.get_screen('pilih_lapak')
        grid = pilih_screen.ids.lapak_grid
        grid.clear_widgets()

        # Simulasi Lapak terisi (misal lapak 3, 7, 12 sudah terisi)
        terisi_list = [3, 7, 12]

        for i in range(1, 17):
            btn = Button(
                text=str(i),
                size_hint_y=None,
                height='48dp',
                bold=True,
                background_normal=''
            )
            if i in terisi_list:
                btn.background_color = (0.8, 0.2, 0.2, 1) # Merah (Terisi)
                btn.disabled = True
            else:
                btn.background_color = (0.2, 0.6, 0.2, 1) # Hijau (Tersedia)
                btn.bind(on_release=lambda x, lapak_num=i: self.pilih_nomor_lapak(lapak_num))
            grid.add_widget(btn)

    def pilih_nomor_lapak(self, nomor):
        self.selected_lapak = nomor
        pilih_screen = self.sm.get_screen('pilih_lapak')
        pilih_screen.ids.info_lapak_dipilih.text = f"Lapak Dipilih: Nomor {nomor}"
        pilih_screen.ids.info_harga_lapak.text = f"Total Biaya: Rp {self.harga_per_lapak:,.0f}".replace(',', '.')

        # Reset warna tombol & highlight yang dipilih
        grid = pilih_screen.ids.lapak_grid
        for child in grid.children:
            if not child.disabled:
                if child.text == str(nomor):
                    child.background_color = (0.05, 0.29, 0.34, 1) # Biru Gelap/Teal (Dipilih)
                else:
                    child.background_color = (0.2, 0.6, 0.2, 1) # Hijau kembali

    def lanjut_ke_pembayaran(self):
        if not self.selected_lapak:
            self.tampilkan_popup("Peringatan", "Silakan pilih nomor lapak terlebih dahulu!")
            return
        
        # Update teks ringkasan pembayaran
        pay_screen = self.sm.get_screen('pembayaran')
        pay_screen.ids.pay_summary_title.text = f"Kolam Galatama - Lapak Nomor {self.selected_lapak}"
        pay_screen.ids.pay_summary_total.text = f"Rp {self.harga_per_lapak:,.0f}".replace(',', '.')
        self.switch_screen('pembayaran')

    def kurang_qty(self):
        if self.qty_produk > 1:
            self.qty_produk -= 1
            self.update_toko_ui()

    def tambah_qty(self):
        self.qty_produk += 1
        self.update_toko_ui()

    def update_toko_ui(self):
        detail_screen = self.sm.get_screen('detail_toko')
        detail_screen.ids.label_qty.text = str(self.qty_produk)
        subtotal = self.qty_produk * self.harga_satuan_produk
        detail_screen.ids.label_subtotal_toko.text = f"Rp {subtotal:,.0f}".replace(',', '.')

    def tambah_keranjang_popup(self):
        self.tampilkan_popup("Berhasil", f"🛒 {self.qty_produk} Produk berhasil dimasukkan ke keranjang belanja!")

    def proses_pembayaran(self):
        self.tampilkan_popup("Sukses Berhasil!", f"🎉 Booking Lapak Nomor {self.selected_lapak} Berhasil Dikonfirmasi!\nSilakan lakukan pembayaran.")
        self.switch_screen('home')

    def tampilkan_popup(self, judul, pesan):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text=pesan, halign='center'))
        btn_close = Button(text="OK", size_hint_y=None, height='40dp', background_normal='', background_color=(0.05, 0.29, 0.34, 1))
        content.add_widget(btn_close)
        
        popup = Popup(title=judul, content=content, size_hint=(None, None), size=('310dp', '210dp'))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    def switch_screen(self, target_screen):
        if self.sm.current == target_screen:
            return

        current_idx = self.screen_order.index(self.sm.current) if self.sm.current in self.screen_order else 0
        target_idx = self.screen_order.index(target_screen) if target_screen in self.screen_order else 0

        if target_idx > current_idx:
            self.sm.transition = SlideTransition(direction='left', duration=0.2)
        else:
            self.sm.transition = SlideTransition(direction='right', duration=0.2)

        self.sm.current = target_screen

if __name__ == '__main__':
    AppMancing().run()