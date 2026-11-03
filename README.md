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
