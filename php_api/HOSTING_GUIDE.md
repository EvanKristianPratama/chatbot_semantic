# 🌐 Panduan Hosting ke InfinityFree

Panduan ini untuk meng-online-kan bagian **Database Toko (PHP & MySQL)** ke InfinityFree.

## 1. Siapkan Database di InfinityFree
1.  Login ke [InfinityFree](https://www.infinityfree.net/).
2.  Masuk ke **Control Panel** (cPanel).
3.  Cari menu **MySQL Databases**.
4.  Buat database baru, misal: `epiz_12345_gadget_db`.
    *   *Catat:* **MySQL Hostname** (biasanya `sql123.infinityfree.com`).
    *   *Catat:* **MySQL Username** (misal `epiz_12345`).
    *   *Catat:* **MySQL Password** (password akun Vesta/CPanel Anda).

## 2. Import Data (phpMyAdmin)
1.  Di Control Panel, klik **phpMyAdmin**.
2.  Pilih database yang baru dibuat di sebelah kiri.
3.  Klik tab **Import** di atas.
4.  Upload file `setup.sql` dari folder `php_api` komputer Anda.
5.  Klik **Go/Kirim**.
    *   *Hasil:* Tabel `tb_market_listings` akan muncul.

## 3. Update Koneksi PHP
Sebelum upload, Anda harus mengedit file `db_connect.php` agar sesuai dengan server InfinityFree.

Buka `db_connect.php` dan ubah bagian ini:
```php
$host = 'sql123.infinityfree.com'; // LIHAT DI INFINITYFREE
$db_name = 'epiz_xxxx_gadget_db';  // NAMA DB BARU
$username = 'epiz_xxxx';           // USERNAME DB
$password = 'password_anda';       // PASSWORD AKUN
```

## 4. Upload File (File Manager)
1.  Buka **Online File Manager** (ada di Client Area InfinityFree).
2.  Masuk ke folder `htdocs`.
3.  Upload 2 file ini:
    *   `api_market.php`
    *   `db_connect.php` (yang sudah diedit tadi)
4.  *Hapus* file index.html atau default.php bawaan jika ada.

## 5. Test & Update Python
1.  Coba akses URL API baru Anda di browser, misal:
    `http://nama-domain-anda.rf.gd/api_market.php`
2.  Jika muncul JSON Data, copy URL tersebut.
3.  Buka file `backend_semantic/app.py` di komputer Anda.
4.  Update baris `URL_API_HARGA`:
    ```python
    URL_API_HARGA = "http://nama-domain-anda.rf.gd/api_market.php"
    ```
5.  Restart Python (`app.py`).

Selesai! Sekarang Bot Python Anda di komputer akan mengambil harga dari Internet. 🌍
