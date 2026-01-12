# 🔌 Panduan Integrasi API Backend (PHP)

Panduan ini menjelaskan cara menghubungkan aplikasi Chatbot Frontend (Next.js) ke Backend Semantic API (PHP).

## 📋 Prasyarat

Sebelum memulai, pastikan Anda memiliki:
1.  **Web Server Local** (XAMPP / Laragon / MAMP) untuk menjalankan PHP & MySQL.
2.  **Database MySQL** yang sudah dibuat.
3.  **File Backend**: `api_market.php` dan `db_connect.php`.

---

## 🚀 Langkah 1: Persiapan Backend

1.  Pastikan `api_market.php` dan `db_connect.php` tersimpan di folder web server Anda (misal: `htdocs/gadgetsemantic/`).
2.  Jalankan server PHP. Pastikan API bisa diakses di browser:
    *   URL: `http://localhost:8000/api_market.php` (Sesuaikan port jika perlu)
3.  Pastikan Database sudah berisi tabel `tb_market_listings` dengan kolom:
    *   `id`
    *   `store_name`
    *   `listing_title`
    *   `price_idr`
    *   `stock`
    *   `item_condition`

---

## 🛠️ Langkah 2: Konfigurasi Frontend

### 1. Buat File Environment
Di dalam folder root `chatbot-ui`, buat file bernama `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
# Ganti URL di atas sesuai alamat backend PHP Anda
```

### 2. Aktifkan Fitur API di Code
Buka file `src/hooks/useChat.ts` dan ubah konstanta konfigurasi:

**Cari baris ini:**
```typescript
const USE_REAL_API = false;
```

**Ubah menjadi:**
```typescript
const USE_REAL_API = true;
```

---

## ✅ Langkah 3: Testing

1.  Pastikan frontend berjalan (`npm run dev`).
2.  Buka aplikasi di browser.
3.  Ketikkan kata kunci produk yang ada di database Anda (contoh: "Samsung" atau nama produk spesifik).
4.  **Berhasil**: Bot akan membalas dengan daftar produk dari database ("🔍 Ditemukan X produk...").
5.  **Gagal**: Bot akan membalas "❌ Gagal menghubungi server" atau "Tidak ditemukan produk".

---

## ⚠️ Troubleshooting

*   **CORS Error**: Jika muncul error CORS di Console browser, tambahkan ini di baris paling atas `api_market.php`:
    ```php
    header("Access-Control-Allow-Origin: *");
    header("Access-Control-Allow-Headers: Content-Type");
    ```
*   **API Not Found**: Pastikan URL di `.env.local` tidak diakhiri dengan garis miring (`/`) jika kode di `api.ts` sudah menambahkannya sendiri.
    *   Benar: `http://localhost:8000`
    *   Salah: `http://localhost:8000/`

Selamat mencoba! 🚀
