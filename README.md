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

`trailer/wayyuh-ai-trailer.mp4` (48 detik, 1080p, 24 fps, stereo) adalah trailer peluncuran Wayyuh AI: AI yang digabung dengan E.B.I.S.I dan intelligence.7mit. Semuanya dibuat dari kode:

- `trailer/trailer.html` adalah linimasa kanvas yang deterministik (`window.draw(t)`).
- `trailer/render.js` merender frame demi frame dengan Playwright (jalankan `python3 -m http.server 8099` di akar repo dulu).
- `trailer/audio.py` mensintesis musiknya dengan numpy saja (detak jantung, riser, dentuman, beat penuh yang pas dengan potongan gambar).
- Gabungkan: `ffmpeg -framerate 24 -i frames/f%05d.jpg -i score.wav -c:v libx264 -crf 24 -pix_fmt yuv420p -c:a aac wayyuh-ai-trailer.mp4`.
