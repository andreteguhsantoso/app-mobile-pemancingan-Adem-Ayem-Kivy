# Backend Supabase khusus aplikasi Kivy

Folder ini adalah sumber skema backend untuk aplikasi Kivy. Proyek Supabase-nya
harus berbeda dari proyek React Native; hanya struktur produk yang sengaja dibuat
setara agar fitur dan aturan bisnis kedua aplikasi konsisten.

## Isi backend

- Supabase Auth untuk akun email/password dan profil pengguna.
- Event, 82 lapak, booking atomik, masa berlaku reservasi, dan riwayat tiket.
- Berita, status kolam, leaderboard, serta pengaturan venue.
- Storage terpisah untuk `avatars`, `gallery`, `content`, dan `payment-proofs`.
- Moderasi foto galeri dan bukti pembayaran yang bersifat privat.
- Row Level Security (RLS): pengguna hanya mengelola datanya sendiri; operator
  dan admin memiliki akses sesuai peran.

## Urutan instalasi pada proyek Supabase baru

Jalankan berkas di `migrations/` melalui SQL Editor sesuai urutan nama. Jangan
menjalankannya pada proyek React Native yang sudah berisi data.

1. `202609180001_initial_schema.sql`
2. `202609240001_account_deletion_requests.sql`
3. `202609240002_capacity_and_media_hardening.sql`
4. `202609290001_community_booking_maturity.sql`
5. `202609290002_booking_manual_payments.sql`

Sesudah semuanya berhasil, salin hanya **Project URL** dan **Publishable key**
ke `backend_config.json` di akar proyek Kivy. Jangan pernah menaruh `secret key`
atau `service_role` di aplikasi/APK.

Format konfigurasi dapat disalin dari `backend_config.example.json`. Berkas
runtime `backend_config.json` sudah diabaikan Git, tetapi tetap ikut ke APK saat
build lokal karena ekstensi JSON diizinkan oleh `buildozer.spec`.

## Membuat admin pertama

1. Daftarkan akun biasa dari aplikasi setelah backend tersambung.
2. Buka `Table Editor > profiles` di dashboard Supabase.
3. Ubah kolom `role` akun tersebut dari `customer` menjadi `admin`.
4. Jangan mengubah `id`; nilainya harus tetap sama dengan pengguna di Auth.

Kunci publishable aman didistribusikan karena seluruh hak akses penting berada
di RLS dan fungsi database. Keamanan tetap bergantung pada migrasi yang berhasil
dipasang seluruhnya.
