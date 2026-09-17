# Launch Readiness - Pemancingan Adem Ayem Dlopo

## Status Saat Ini

Versi Kivy 1.1.0 siap digunakan sebagai aplikasi operasional lokal atau kiosk pada satu perangkat. Versi ini belum boleh dipublikasikan sebagai aplikasi multi-pengguna melalui Play Store sebelum blocker eksternal pada bagian berikut diselesaikan.

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

## Blocker Sebelum Publik Multi-Pengguna

1. Backend pusat berbasis HTTPS dan PostgreSQL agar semua perangkat membaca lapak yang sama.
2. Akun merchant payment gateway resmi untuk QRIS, e-wallet, virtual account, webhook, refund, dan rekonsiliasi.
3. Nomor WhatsApp bisnis, alamat lengkap, kontak privasi, serta kebijakan refund resmi.
4. Domain API, hosting, monitoring, backup off-site, rate limiting, dan rotasi secret.
5. QR tiket yang dapat dipindai serta aplikasi/operator check-in.
6. Pengujian pada perangkat Android nyata, koneksi lambat, proses resume, dan kegagalan pembayaran.
7. Signing key Android, akun Google Play Console, screenshot store, feature graphic, dan URL kebijakan privasi publik.

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
