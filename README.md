# MVP Pemancingan Nila Kediri

Aplikasi Kivy untuk satu lokasi pemancingan yang seluruh kolam dan eventnya khusus ikan nila.

## Fitur MVP

- Beranda bergaya wireframe dengan carousel empat banner yang berganti otomatis setiap 5 detik
- Daftar dan detail empat paket event khusus nila
- Denah interaktif 82 lapak dengan status tersedia, terisi, dan dipilih
- Empat paket event: 225 kg/Rp100.000, 200 kg/Rp85.000, 150 kg/Rp70.000, dan 100 kg/Rp50.000
- Alur booking bertahap: pilih lapak, isi data, pembayaran, lalu tiket
- Pilihan pembayaran QRIS/e-wallet, transfer bank, atau bayar di lokasi
- Persetujuan aturan umpan sebelum booking dapat dibuat
- Tiket digital dengan visual kode dan kode booking unik
- Penyimpanan booking lokal menggunakan SQLite
- Leaderboard, galeri, berita, status harian, dan riwayat pesanan
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

Untuk memasang ulang dependensi:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Data booking lokal dibuat otomatis pada `mvp.db` saat aplikasi dijalankan.

Titik lokasi resmi yang dipakai aplikasi:

https://maps.app.goo.gl/cQtnrkjTiAvC5JNC7

## Menjalankan Pemeriksaan MVP

```powershell
.\.venv\Scripts\python.exe tests\test_smoke.py
```

Pemeriksaan ini menggunakan database sementara dan menguji alur dari pemilihan lapak sampai penerbitan tiket.

## Status Pengembangan

Pembayaran dan visual kode tiket pada MVP masih berupa simulasi lokal. Integrasi payment gateway, QR yang dapat dipindai, autentikasi admin, data cuaca langsung, dan sinkronisasi backend merupakan tahap produksi berikutnya.

## Referensi Wireframe

Empat board wireframe dan pemetaan 16 layar tersedia di [`WIREFRAME.md`](WIREFRAME.md).
