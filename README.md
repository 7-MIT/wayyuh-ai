# Wayyuh AI

Wayyuh AI adalah asisten AI satu file (`index.html`) dengan chat, proyek, memori, alat, cuaca, dan workspace kode. Dulu bernama Sunday.

## Menjalankan

```bash
python3 -m http.server 8080
```

Buka `http://localhost:8080`. Manifest, service worker, dan ikon (`manifest.webmanifest`, `sw.js`, `icons/`) membuatnya bisa dipasang sebagai aplikasi dan terbuka offline.

## Catatan migrasi dari Sunday

- Data lama (`sunday.*` di localStorage) disalin otomatis ke `wayyuh.*` saat pertama dibuka.
- Cadangan JSON dari Sunday masih bisa diimpor.
- Server AI: Supabase Edge Function `intellegence-7mit-public` (lihat `SERVER_URL` di `index.html`).
- Wallpaper kustom (IndexedDB `sunday-kv`) tidak ikut terbawa; pasang ulang dari Pengaturan.

## Foto latar

Latar beranda memakai foto pemandangan dan landmark Indonesia dari Unsplash (Bromo, Rinjani, Raja Ampat, Tegallalang, Padar, Danau Toba, Borobudur, Prambanan, Pura Ulun Danu Bratan, Monas, Masjid Istiqlal, Tugu Yogyakarta, Jam Gadang). Fotonya diacak setiap hari: seluruh daftar diurutkan acak per siklus, jadi semua foto tampil sekali sebelum ada yang berulang, dan tidak pernah sama dua hari berturut-turut. Daftarnya ada di `ID_PHOTOS` di `index.html`. Wallpaper buatan pengguna tetap diutamakan, dan latar mesh beranimasi dipakai bila foto tidak bisa dimuat.

## Trailer

Trailer peluncuran Wayyuh AI (48 detik, 1080p, 24 fps, stereo): AI yang digabung dengan E.B.I.S.I dan intelligence.7mit. Videonya (`wayyuh-ai-trailer.mp4`) sengaja tidak disimpan di git; yang disimpan hanya sumbernya, dan semuanya dibuat dari kode:

- `trailer/trailer.html` adalah linimasa kanvas yang deterministik (`window.draw(t)`).
- `trailer/render.js` merender frame demi frame dengan Playwright (jalankan `python3 -m http.server 8099` di akar repo dulu).
- `trailer/audio.py` mensintesis musiknya dengan numpy saja (detak jantung, riser, dentuman, beat penuh yang pas dengan potongan gambar).
- Gabungkan: `ffmpeg -framerate 24 -i frames/f%05d.jpg -i score.wav -c:v libx264 -crf 24 -pix_fmt yuv420p -c:a aac wayyuh-ai-trailer.mp4`.

## Akun dan sinkronisasi

Akun bersifat opsional (masuk atau daftar dari bagian Profil). Satu akun menyimpan chat, memori, proyek, catatan, tugas, pengaturan, avatar, dan aktivitas di United Wayyuh Server (Supabase), dan data itu ikut ke perangkat mana pun saat masuk.

- Basis data: tabel `public.wayyuh_sync` (satu baris per `user_id` + `key`; kunci `cfg`, `avatar`, `act`, `projects`, `memories`, `notes`, `tasks`, `memAuto`, dan `chat:<id>`). Row level security membatasi tiap akun hanya ke barisnya sendiri; `anon` tidak punya akses.
- Autentikasi: email dan kata sandi lewat Supabase Auth. Kunci publik (`ACC_KEY`) memang aman ada di browser.
- Sinkronisasi memakai hash per baris: hanya baris yang berubah dikirim, penghapusan ikut menyebar, dan keluar dari akun membersihkan data di perangkat setelah tersimpan.
- Wallpaper buatan sendiri, lokasi cuaca, dan status tampilan perangkat tidak ikut disinkronkan.

Pengaturan yang perlu ada di dashboard Supabase supaya pendaftaran dan tautan email berfungsi: **Authentication → URL Configuration** (Site URL dan Redirect URLs berisi alamat produksi, mis. `https://ai.wayyuh.org`) dan **SMTP kustom** agar email konfirmasi terkirim ke alamat siapa pun.

## Halaman hukum

`/terms/` (Ketentuan Layanan) dan `/privacy/` (Kebijakan Privasi) adalah halaman statis di `terms/index.html` dan `privacy/index.html`. Kontak keluhan: halo@7mit.org.
