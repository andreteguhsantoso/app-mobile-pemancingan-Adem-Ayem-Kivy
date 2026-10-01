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

## Panduan Penggunaan Aplikasi

Bagian ini ditujukan untuk pengguna aplikasi, bukan untuk pengembang.

### Memulai aplikasi

1. Buka aplikasi Pemancingan Adem Ayem Dlopo.
2. Beranda dapat dibuka sebagai tamu untuk melihat event, galeri, berita, papan juara, informasi kolam, dan lokasi.
3. Pilih `Akun` untuk mendaftar atau masuk. Login diperlukan saat membuat booking, mengirim foto, dan mengakses data pribadi.
4. Pengguna yang sudah memiliki akun dapat memasukkan email dan password. Jika belum memiliki akun, pilih `Daftar`, lengkapi data, setujui Privasi & Ketentuan, lalu kirim formulir.

### Beranda

- Geser atau gunakan tombol panah pada carousel untuk melihat event yang tersedia.
- Tekan kartu event untuk membuka detail tanggal, jam, harga, jumlah ikan, dan ketersediaan lapak.
- Gunakan `Akses cepat` untuk menuju booking event, daftar lapak, galeri, atau peta lokasi.
- Bagian `Jadwal terdekat` menampilkan event yang paling dekat waktunya.

### Melihat event dan memilih lapak

1. Buka `Agenda` atau pilih event dari Beranda.
2. Tekan event yang ingin diikuti.
3. Periksa tanggal, jam, harga, kuota, dan aturan event.
4. Tekan tombol booking untuk membuka denah 82 lapak.
5. Pilih lapak berwarna tersedia. Lapak yang sudah terisi tidak dapat dipilih.
6. Lanjutkan ke formulir data peserta.

### Membuat booking dan tiket

1. Pastikan nama dan nomor WhatsApp peserta sudah benar.
2. Tambahkan catatan jika diperlukan.
3. Baca dan setujui aturan umpan.
4. Pilih metode pembayaran yang tersedia: QRIS/e-wallet, transfer bank, atau `Bayar di lokasi`.
5. Periksa kembali event, lapak, peserta, dan total biaya.
6. Tekan tombol konfirmasi.
7. Setelah berhasil, aplikasi menampilkan tiket digital beserta kode booking.

Simpan kode booking dan tunjukkan tiket digital saat check-in. Jangan membagikan tiket kepada orang lain. Jika lapak sudah diambil pengguna lain, aplikasi akan menolak booking dan meminta Anda memilih lapak lain.

### Melihat pesanan dan membatalkan booking

- Buka `Akun > Pesanan Saya` untuk melihat tiket aktif dan riwayat booking.
- Tekan tiket untuk melihat detail lengkap.
- Booking yang belum dibayar dapat dibatalkan melalui tombol pembatalan.
- Setelah pembatalan berhasil, lapak dikembalikan ke daftar tersedia sesuai aturan event.

### Galeri dan pengiriman foto

1. Buka tab `Momen` atau halaman `Galeri`.
2. Gunakan filter kategori untuk menyaring foto event, tangkapan, kolam, atau momen.
3. Tekan foto untuk melihat ukuran besar.
4. Untuk mengirim foto, pilih `Kirim Foto` dan masuk ke akun terlebih dahulu.
5. Pilih foto JPG, PNG, atau WEBP dari galeri perangkat.
6. Isi judul foto, lalu kirim.

Foto kiriman pengguna berstatus menunggu moderasi. Foto baru tampil di galeri publik setelah disetujui admin. Ukuran foto pengguna dibatasi 10 MB.

### Papan juara dan berita

- Buka tab `Juara` untuk melihat berat ikan terbesar, total berat, jumlah ikan, dan foto pemancing.
- Gunakan filter `Hari Ini`, `Per Event`, atau `Bulanan` jika tersedia.
- Buka tab `Berita` untuk membaca pengumuman, aturan, dan informasi kolam.
- Tekan kartu berita untuk membuka isi lengkapnya.

### Profil dan foto profil

1. Buka tab `Akun`.
2. Pilih `Pengaturan akun` untuk mengubah nama, username, atau nomor WhatsApp.
3. Pilih `Tambah/Ganti Foto Profil`.
4. Pilih foto dari galeri perangkat dan periksa pratinjau.
5. Tekan `Simpan Perubahan Profil`.
6. Gunakan `Hapus Foto` jika ingin kembali memakai inisial nama.

Foto profil hanya menerima JPG, PNG, atau WEBP dengan ukuran maksimal 5 MB.

### Panduan, lokasi, dan status kolam

- Buka `Akun > Panduan & Lokasi` untuk membaca aturan memancing, fasilitas, informasi operasional, dan petunjuk lokasi.
- Tekan tombol rute untuk membuka lokasi resmi di Google Maps:
  https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7
- Halaman status menampilkan informasi operasional terbaru dari pengelola.

### Peran admin

Menu admin hanya untuk pengelola yang diberi peran `admin` atau `operator`.

1. Buka `Akun > Panduan & Lokasi > Admin`.
2. Pada penggunaan pertama, buat PIN pengelola minimal 6 angka.
3. Masukkan PIN untuk membuka Dashboard Admin.
4. Gunakan menu yang sesuai:
   - `Kelola Event & Jadwal` untuk membuat, mengubah, menerbitkan, atau mengarsipkan event.
   - `Kelola Galeri` untuk memoderasi foto kiriman pengguna.
   - `Kelola Peringkat` untuk mengelola data papan juara.
   - `Kelola Berita` untuk membuat pengumuman dan artikel.
   - `Kelola Pengguna` untuk melihat akun atau mengubah status akun.
   - `Operasional` untuk memperbarui status dan informasi kolam.
5. Keluar atau kunci kembali dashboard admin setelah selesai.

PIN disimpan sebagai hash di perangkat dan tidak ditulis ke source code. Jangan membagikan PIN kepada pengguna lain.

### Koneksi online dan mode lokal

Jika Supabase sudah dikonfigurasi, login, profil, media, konten publik, dan ketersediaan lapak dapat disinkronkan antarperangkat. Jika koneksi tidak tersedia, aplikasi masih dapat dibuka menggunakan data lokal/cache, tetapi perubahan online mungkin tertunda. Periksa koneksi internet dan konfigurasi `backend_config.json` jika muncul pesan backend belum tersedia.

### Pemecahan masalah pengguna

- **Tidak dapat masuk**: periksa email, password, koneksi internet, dan apakah email sudah dikonfirmasi.
- **Profil belum muncul**: pastikan pendaftaran berhasil dan akun terlihat di Authentication Supabase.
- **Foto tidak muncul di galeri**: pilih ulang foto melalui tombol pemilih gambar Android dan gunakan format JPG/PNG/WEBP.
- **Booking ditolak**: lapak mungkin sudah diambil pengguna lain atau event sudah penuh.
- **Tiket tidak terlihat**: buka `Akun > Pesanan Saya`, pastikan masuk menggunakan akun yang sama, lalu tunggu sinkronisasi selesai.
- **Aplikasi terlihat tidak berubah**: tutup dan buka kembali aplikasi agar cache konten dimuat ulang.

## Menjalankan Aplikasi

Virtual environment Python 3.13 dan Kivy sudah tersedia di proyek ini.

```powershell
.\.venv\Scripts\python.exe app.py
```

Saat menu Admin dibuka pertama kali, aplikasi meminta pembuatan PIN minimal 6 angka. PIN disimpan sebagai hash PBKDF2 dengan salt acak di database privat perangkat, bukan sebagai teks asli atau source code.

Untuk memasang ulang dependensi:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Database otomatis dibuat atau dimigrasikan pada `mvp.db`. Data lama dipertahankan, sedangkan transaksi booking baru memakai penguncian SQLite dan indeks unik untuk mencegah pemesanan ganda pada event dan lapak yang sama.

## Mengelola Konten dari Aplikasi

1. Buka `Akun > Panduan & Lokasi > Admin`.
2. Pada penggunaan pertama, buat dan konfirmasi PIN pengelola minimal 6 angka. Setelah itu, masukkan PIN tersebut untuk membuka Dashboard Admin.
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

Versi 1.3.0 menambahkan pemilih galeri Android berbasis Storage Access Framework, fondasi Supabase terpisah, Auth online, unggah avatar/galeri, sinkronisasi konten publik, dan reservasi lapak atomik. Tanpa `backend_config.json`, aplikasi tetap berjalan sebagai beta lokal. Payment gateway resmi, URL kebijakan privasi publik, dan proyek Supabase Kivy yang sudah dipasang migrasi tetap diperlukan sebelum distribusi Play Store multi-perangkat.

Status kesiapan produksi dan blocker peluncuran publik dijelaskan pada [`LAUNCH_READINESS.md`](LAUNCH_READINESS.md). SQLite tetap dipakai sebagai cache/cadangan perangkat; Supabase menjadi sumber kebenaran untuk akun dan ketersediaan lapak setelah konfigurasi backend dipasang.

## Referensi Wireframe

Empat board wireframe dan pemetaan 16 layar tersedia di [`WIREFRAME.md`](WIREFRAME.md).
