# Launch Readiness - Pemancingan Adem Ayem Dlopo

## Status Saat Ini

Versi Kivy 1.2.0 siap digunakan sebagai beta publik lokal, aplikasi operasional, atau kiosk pada satu perangkat. Versi ini belum boleh dipublikasikan sebagai aplikasi multi-pengguna melalui Play Store sebelum blocker eksternal pada bagian berikut diselesaikan.

## Sudah Siap

- Alur event, pemilihan 82 lapak, data peserta, konfirmasi, dan tiket.
- Database SQLite persisten dengan transaksi atomik dan proteksi lapak ganda.
- Pembatalan tiket belum dibayar dan pengembalian inventaris lapak.
- Informasi operasional persisten, audit log, dan backup database.
- Proteksi menu admin melalui environment `ADEM_AYEM_ADMIN_PIN`.
- Akun pengguna dengan password PBKDF2, mode tamu, dan riwayat tiket per akun.
- Profil pengguna yang dapat mengganti username, nama, WhatsApp, dan foto lokal.
- Riwayat login, perubahan password mandiri, status akun, dan reset password admin.
- Halaman privasi dan ketentuan di dalam aplikasi.
- Konfigurasi build Windows dan Android.
- Smoke test UI dan pengujian database terisolasi.
- Carousel Beranda menampilkan seluruh event aktif tanpa batas empat slide.
- Event, galeri, berita, dan leaderboard dapat dikelola dari aplikasi.
- Unggahan galeri pengguna memakai moderasi admin sebelum tampil publik.
- Registrasi membutuhkan persetujuan Privasi & Ketentuan.
- Mode rilis tidak mengizinkan pembayaran digital simulasi; pembayaran di lokasi menjadi pilihan aman.
- Dashboard Admin menampilkan hasil pemeriksaan integritas SQLite dan dapat dikunci kembali.
- Audit rilis dapat dijalankan melalui `release_check.py`.

## Blocker Sebelum Publik Multi-Pengguna

1. Backend pusat berbasis HTTPS dan PostgreSQL agar semua perangkat membaca lapak yang sama.
2. Akun merchant payment gateway resmi untuk QRIS, e-wallet, virtual account, webhook, refund, dan rekonsiliasi.
3. Nomor WhatsApp bisnis, alamat lengkap, kontak privasi, serta kebijakan refund resmi.
4. Domain API, hosting, monitoring, backup off-site, rate limiting, dan rotasi secret.
5. QR tiket yang dapat dipindai serta aplikasi/operator check-in.
6. Pengujian pada perangkat Android nyata, koneksi lambat, proses resume, dan kegagalan pembayaran.
7. Signing key Android, akun Google Play Console, screenshot store, feature graphic, dan URL kebijakan privasi publik.
8. Pemilih foto Android berbasis Storage Access Framework dan pengujian izin media pada Android 13+.

## Konfigurasi Admin Lokal

PowerShell:

```powershell
$env:ADEM_AYEM_ADMIN_PIN="gunakan-pin-minimal-6-digit"
.\.venv\Scripts\python.exe app.py
```

Jangan menuliskan PIN ke source code atau memasukkannya ke Git.

## Build Windows

Pasang PyInstaller pada environment build, kemudian jalankan:

```powershell
pyinstaller --clean --noconfirm adem_ayem.spec
```

## Build Android

Buildozer memerlukan Linux atau WSL2. Dari environment tersebut jalankan:

```bash
buildozer android debug
```

Gunakan `buildozer android release` hanya setelah keystore, package ID final, kebijakan privasi, backend, dan payment gateway siap.

## Audit Otomatis

```powershell
.\.venv\Scripts\python.exe release_check.py
.\.venv\Scripts\python.exe release_check.py --strict-public
```

Perintah pertama memverifikasi kesiapan beta lokal, integritas database, aset wajib, dan konsistensi versi. Mode `--strict-public` juga mewajibkan konfigurasi backend HTTPS, payment gateway, dan URL kebijakan privasi.
