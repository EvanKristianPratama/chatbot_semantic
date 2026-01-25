-- 1. Buat Tabel Market Listings (PostgreSQL Compatible)
CREATE TABLE IF NOT EXISTS tb_market_listings (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(100),
    listing_title VARCHAR(255),
    price_idr NUMERIC(15, 2),
    stock TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Note: Stock biasanya INT, tapi saya lihat di code sebelumnya INT. Biarkan INT.
    item_condition VARCHAR(50), 
    sku_ref VARCHAR(100)
);

-- Koreksi tipe data stock kembali ke INT (jika salah ketik diatas)
ALTER TABLE tb_market_listings ALTER COLUMN stock TYPE INTEGER USING stock::integer; 
-- Atau drop create ulang biar bersih:
DROP TABLE IF EXISTS tb_market_listings;
CREATE TABLE tb_market_listings (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(100),
    listing_title VARCHAR(255),
    price_idr NUMERIC(15, 2),
    stock INTEGER,
    item_condition VARCHAR(50),
    sku_ref VARCHAR(100)
);

-- 2. Masukkan Data Dummy (Samsung)
INSERT INTO tb_market_listings (store_name, listing_title, price_idr, stock, item_condition, sku_ref) VALUES
('Samsung Official', 'Samsung Galaxy S24 8/256GB Black', 12999000, 50, 'Baru', 'samsung_s24'),
('Gadget Murah Jkt', 'Samsung S23 Ultra Cream 12/512GB Garansi Sein', 15450000, 2, 'Bekas', 'samsung_s23ultra'),
('Cellular World', 'Samsung Galaxy A05s Light Green', 1899000, 100, 'Baru', 'samsung_a05s');

-- 3. Masukkan Data Dummy (Apple)
INSERT INTO tb_market_listings (store_name, listing_title, price_idr, stock, item_condition, sku_ref) VALUES
('iBox', 'iPhone 15 Pro Titanium 256GB', 20999000, 15, 'Baru', 'iphone_15_pro'),
('Renan Store', 'iPhone 15 Pro 256GB Ex Inter Mulus', 18500000, 1, 'Bekas', 'iphone_15_pro');

-- 4. Masukkan Data Dummy (Xiaomi/Poco)
INSERT INTO tb_market_listings (store_name, listing_title, price_idr, stock, item_condition, sku_ref) VALUES
('Poco Official', 'POCO F5 12/256GB White', 5299000, 0, 'Baru', 'poco_f5'),
('Mi Store', 'Redmi Note 13 Pro 5G', 4599000, 25, 'Baru', 'redmi_note_13');
