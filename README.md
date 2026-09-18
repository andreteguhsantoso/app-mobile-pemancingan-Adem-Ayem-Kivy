# Aplikasi Kivy Pemancingan Adem Ayem Dlopo

Aplikasi Python/Kivy yang mengikuti tampilan, data, aset, dan alur utama versi Expo React Native Pemancingan Adem Ayem Dlopo. Seluruh kolam dan event khusus ikan nila.

## Fitur Aplikasi

- Desain teal, krem, emas, dan oranye yang sama dengan aplikasi Expo
- Pratinjau desktop 390x844 seperti layar ponsel
- Beranda dengan carousel seluruh event aktif yang berganti otomatis setiap lima detik tanpa batas empat slide
- Daftar dan detail empat paket event khusus nila
- Denah interaktif 82 lapak dengan status tersedia, terisi, dan dipilih
- Empat paket event: 225 kg/Rp100.000, 200 kg/Rp85.000, 150 kg/Rp70.000, dan 100 kg/Rp50.000
- Alur booking bertahap: pilih lapak, isi data, pembayaran, lalu tiket
- Pilihan pembayaran QRIS/e-wallet, transfer bank, atau bayar di lokasi
- Persetujuan aturan umpan sebelum booking dapat dibuat
- Tiket digital dengan visual kode dan kode booking unik
- Database SQLite lokal untuk menyimpan event, inventaris 82 lapak, dan pesanan
- Tiket dan riwayat pesanan tetap tersedia setelah aplikasi ditutup
- Kuota event dan status lapak langsung diperbarui setelah pemesanan berhasil
- Tiket lama dapat dibuka kembali dari Profil maupun halaman Pesanan Saya
- Catatan opsional peserta diteruskan ke ringkasan pembayaran dan data pesanan
- Pembatalan tiket belum dibayar dengan pengembalian lapak otomatis
- Informasi operasional persisten dan langsung diperbarui pada Beranda
- Audit log dan backup database lokal
- Menu admin dilindungi PIN dari environment
- Sesi admin dapat dikunci kembali dari Dashboard Admin
- Pemeriksaan kesehatan SQLite tampil pada Dashboard Admin
- Registrasi mewajibkan persetujuan Privasi & Ketentuan
- Halaman privasi dan ketentuan penggunaan
- Mode tamu untuk melihat seluruh informasi tanpa login
- Login dan registrasi diwajibkan hanya saat pengguna memesan tiket
- Riwayat tiket dipisahkan untuk setiap akun
- Profil dapat mengubah nama, username, nomor WhatsApp, serta menambah, mengganti, atau menghapus foto dari perangkat
- Riwayat login berhasil/gagal dan penggantian password mandiri
- Admin dapat melihat akun, menonaktifkan pengguna, dan mereset password
- Admin dapat membuat, mengubah, menerbitkan, dan mengarsipkan event/jadwal langsung dari aplikasi
- Editor event dapat memperbarui nama, tanggal, jam, harga, jumlah ikan, foto, dan inventaris lapak tanpa mengganggu lapak yang sudah dibooking
- Admin dapat memilih foto event dan mengunggah foto galeri dari perangkat
- Pengguna yang login dapat mengirim foto galeri; foto baru tampil setelah disetujui admin
- Admin dapat menyetujui atau menolak kiriman foto beserta identitas pengirimnya
- Admin dapat menambah, mengedit, dan mengarsipkan data Papan Juara langsung dari aplikasi
- Admin dapat menerbitkan berita, pengumuman, aturan, dan kabar kolam tanpa mengubah kode
- Event, galeri, dan berita dikelola dari SQLite dan langsung tersinkron ke halaman publik
- Galeri khusus foto dengan filter dan tampilan foto besar
- Papan Juara dengan filter periode, foto pemancing, berat terbesar, total berat, dan jumlah ikan
- Berita dengan filter kategori serta halaman detail artikel
- Profil dengan tiket aktif, riwayat tersimpan, status harian, panduan, berita, dan lokasi
- Informasi operasional, cuaca, fasilitas, aturan, dan petunjuk lokasi
- Tombol rute menggunakan titik Google Maps resmi pemancingan
- Dashboard admin dan formulir pembaruan operasional lokal
- Seluruh gambar disimpan lokal di `assets/generated`

## Sistem Desain

- Bahnschrift digunakan untuk judul, harga, tombol, dan angka penting pada Windows.
- Trebuchet MS digunakan untuk teks isi agar tetap nyaman dibaca.
- Perangkat tanpa font tersebut otomatis memakai font bawaan Kivy.
- Warna utama menggunakan teal kolam, terracotta untuk CTA, mint untuk status tersedia, serta emas untuk highlight event.
- Alur booking memiliki progress empat langkah: lapak, data, bayar, dan tiket.
- Seluruh kartu, tombol, input, filter, dan navigasi menggunakan bentuk rounded yang konsisten.

## Aturan Umpan

Umpan utama wajib berasal dari bahan alami. Media, bahan, atau umpan yang tidak berasal dari alam dilarang. Essen dan pemanis diperbolehkan hanya sebagai campuran umpan alami, bukan sebagai umpan utama.

## Menjalankan Aplikasi

Virtual environment Python 3.13 dan Kivy sudah tersedia di proyek ini.

```powershell
.\.venv\Scripts\python.exe app.py
```

Untuk mengaktifkan akses admin pada sesi PowerShell:

```powershell
$env:ADEM_AYEM_ADMIN_PIN="pin-minimal-6-digit"
.\.venv\Scripts\python.exe app.py
```

Untuk memasang ulang dependensi:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Database otomatis dibuat atau dimigrasikan pada `mvp.db`. Data lama dipertahankan, sedangkan transaksi booking baru memakai penguncian SQLite dan indeks unik untuk mencegah pemesanan ganda pada event dan lapak yang sama.

## Mengelola Konten dari Aplikasi

1. Jalankan aplikasi dengan `ADEM_AYEM_ADMIN_PIN` seperti contoh di atas.
2. Buka `Akun > Panduan & Lokasi > Admin`, lalu masukkan PIN pengelola.
3. Pilih `Kelola Event & Jadwal`, `Kelola Galeri`, `Kelola Peringkat`, atau `Kelola Berita`.
4. Isi formulir, pilih foto PNG/JPG dari perangkat, lalu tekan tombol simpan atau terbitkan.
5. Konten langsung tampil pada Agenda, Galeri, Berita, dan carousel Beranda.

Foto yang dipilih disalin ke folder data aplikasi pada subfolder `content/event`, `content/gallery`, `content/user_gallery`, `content/leaderboard`, atau `content/news`. Batas ukuran setiap foto adalah 10 MB. Mengarsipkan konten hanya menyembunyikannya dari publik dan tidak menghapus riwayat database.

Pengguna dapat membuka halaman `Galeri` lalu memilih `Kirim Foto`. Login diperlukan untuk mengirim foto agar nama pengirim dan status moderasi dapat dicatat. Kiriman pengguna berstatus `pending` sampai admin menyetujui atau menolaknya melalui `Kelola Galeri`.

Foto profil dikelola melalui `Akun > Tambah/Ganti Foto Profil` atau `Akun > Pengaturan akun`. Pilih foto PNG/JPG maksimal 5 MB, periksa pratinjau, lalu tekan `Simpan Perubahan Profil`. Tombol `Hapus Foto` mengembalikan avatar ke inisial nama pengguna.

Mode publik lokal hanya mengaktifkan `Bayar di lokasi`, sehingga aplikasi tidak pernah menandai pembayaran digital sebagai berhasil tanpa gateway resmi. Simulasi QRIS/transfer hanya dapat diaktifkan untuk pengembangan dengan `ADEM_AYEM_ENABLE_SIMULATED_PAYMENTS=1`.

Titik lokasi resmi yang dipakai aplikasi:

https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7

## Menjalankan Pemeriksaan MVP

```powershell
.\.venv\Scripts\python.exe tests\test_smoke.py
.\.venv\Scripts\python.exe tests\test_database.py
```

Pemeriksaan ini menguji lima tab utama, carousel dengan lebih dari empat event, filter Galeri/Juara/Berita, konten dinamis admin, alur pemilihan lapak, persetujuan aturan, mode pembayaran aman, persistensi tiket, penolakan lapak ganda, dan Profil.

Audit kesiapan rilis lokal:

```powershell
.\.venv\Scripts\python.exe release_check.py
```

Audit ketat untuk rilis multi-perangkat:

```powershell
.\.venv\Scripts\python.exe release_check.py --strict-public
```

## Melihat Isi Database

File `mvp.db` adalah file biner SQLite dan tidak dapat dibaca sebagai teks biasa. Gunakan alat inspeksi berikut:

```powershell
.\.venv\Scripts\python.exe inspect_database.py
.\.venv\Scripts\python.exe inspect_database.py users
.\.venv\Scripts\python.exe inspect_database.py bookings --limit 50
.\.venv\Scripts\python.exe inspect_database.py login_logs --limit 50
```

Kolom `password_hash` dan `password_salt` sengaja tidak ditampilkan. Password tidak dapat didekripsi; jika pengguna lupa password, sistem produksi harus menyediakan proses reset password.

## Status Pengembangan

Versi 1.2.0 siap sebagai beta publik lokal/satu perangkat dengan pembayaran di lokasi. Payment gateway, QR yang dapat dipindai, cuaca langsung, notifikasi, dan sinkronisasi backend tetap diperlukan sebelum distribusi multi-perangkat.

Status kesiapan produksi dan blocker peluncuran publik dijelaskan pada [`LAUNCH_READINESS.md`](LAUNCH_READINESS.md). Versi SQLite saat ini cocok untuk satu perangkat operasional; peluncuran multi-pengguna membutuhkan backend pusat agar ketersediaan lapak sinkron di semua perangkat.

## Referensi Wireframe

Empat board wireframe dan pemetaan 16 layar tersedia di [`WIREFRAME.md`](WIREFRAME.md).
