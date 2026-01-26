import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def estimate_processor(model_name):
    """Tebak processor berdasarkan nama model"""
    m = model_name.lower()
    if "s24 ultra" in m: return "Snapdragon 8 Gen 3"
    if "s24" in m: return "Exynos 2400"
    if "s23 ultra" in m: return "Snapdragon 8 Gen 2"
    if "s23" in m: return "Snapdragon 8 Gen 2"
    if "iphone 17" in m: return "A19 Pro"
    if "iphone 16 pro" in m: return "A18 Pro"
    if "iphone 16" in m: return "A18"
    if "iphone 15 pro" in m: return "A17 Pro"
    if "iphone 15" in m: return "A16 Bionic"
    if "iphone 14" in m: return "A15 Bionic"
    if "iphone 13" in m: return "A15 Bionic"
    if "pixel 9" in m: return "Tensor G4"
    if "pixel 8" in m: return "Tensor G3"
    if "poco f5" in m: return "Snapdragon 7+ Gen 2"
    if "poco" in m: return "MediaTek Dimensity"
    if "redmi note 14" in m: return "MediaTek Dimensity 7025"
    if "redmi" in m: return "MediaTek Helio"
    if "realme gt" in m: return "Snapdragon 8 Gen 4"
    if "realme 14 pro" in m: return "MediaTek Dimensity 7300"
    if "realme" in m: return "MediaTek Helio G99"
    if "infinix gt" in m: return "MediaTek Dimensity 8200"
    if "infinix" in m: return "MediaTek Helio G88"
    if "tecno camon" in m: return "MediaTek Dimensity 8020"
    if "tecno" in m: return "MediaTek Helio G85"
    if "itel" in m: return "Unisoc SC9863A"
    if "vivo x100" in m: return "MediaTek Dimensity 9300"
    if "vivo v" in m: return "Snapdragon 7 Gen 3"
    if "vivo" in m: return "MediaTek Dimensity"
    if "oppo find x" in m: return "MediaTek Dimensity 9400"
    if "oppo reno" in m: return "MediaTek Dimensity 8100"
    if "oppo" in m: return "Snapdragon 680"
    if "nothing phone" in m: return "Snapdragon 8+ Gen 1"
    if "nothing" in m: return "N/A (Aksesori)"
    if "galaxy z flip" in m: return "Snapdragon 8 Gen 3"
    if "galaxy z fold" in m: return "Snapdragon 8 Gen 3"
    if "galaxy a" in m: return "MediaTek Helio G99"
    if "samsung" in m or "galaxy" in m: return "Exynos / Snapdragon"
    if "macbook m4" in m: return "Apple M4 Pro"
    if "macbook m2" in m: return "Apple M2"
    if "macbook m1" in m: return "Apple M1"
    if "ipad" in m: return "Apple M-Series"
    if "nintendo switch" in m: return "NVIDIA Tegra X1+"
    if "playstation" in m: return "AMD Zen 2 + RDNA 2"
    if "steam deck" in m: return "AMD Zen 2 APU"
    if "rog ally" in m: return "AMD Ryzen Z1 Extreme"
    if "legion go" in m: return "AMD Ryzen Z1 Extreme"
    if "xperia" in m: return "Snapdragon 8 Gen 2"
    return "Unknown"

def estimate_camera(model_name):
    """Tebak kamera MP berdasarkan nama model"""
    m = model_name.lower()
    if "s24 ultra" in m or "s23 ultra" in m: return 200
    if "s24" in m or "s23" in m: return 50
    if "iphone 16 pro" in m or "iphone 15 pro" in m: return 48
    if "iphone" in m: return 12
    if "pixel 9 pro" in m: return 50
    if "pixel" in m: return 50
    if "200mp" in m: return 200
    if "108mp" in m: return 108
    if "64mp" in m: return 64
    if "50mp" in m: return 50
    if "pro" in m or "ultra" in m: return 108
    if "poco" in m: return 64
    if "redmi note" in m: return 108
    if "redmi" in m: return 50
    if "vivo x100" in m: return 50 # Zeiss
    if "oppo find" in m: return 50 # Hasselblad
    if "realme gt" in m: return 50
    if "nothing phone" in m: return 50
    if "ipad" in m or "macbook" in m: return 12
    if "ear" in m or "buds" in m or "watch" in m: return 0 # Aksesori
    return 48 # Default

def migrate_and_update():
    print("🔌 Connecting to Neon...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. Add columns if not exist
    print("➕ Adding columns (processor, camera_mp)...")
    try:
        cur.execute("ALTER TABLE tb_market_listings ADD COLUMN IF NOT EXISTS processor VARCHAR(100)")
        cur.execute("ALTER TABLE tb_market_listings ADD COLUMN IF NOT EXISTS camera_mp INTEGER")
        conn.commit()
        print("✅ Columns added!")
    except Exception as e:
        print(f"⚠️ Column add warning: {e}")
        conn.rollback()

    # 2. Fetch all rows and update
    print("📦 Fetching products...")
    cur.execute("SELECT id, listing_title FROM tb_market_listings")
    rows = cur.fetchall()
    
    print(f"🔄 Updating {len(rows)} products...")
    for row in rows:
        db_id = row[0]
        model_name = row[1]
        
        proc = estimate_processor(model_name)
        cam = estimate_camera(model_name)
        
        cur.execute("UPDATE tb_market_listings SET processor = %s, camera_mp = %s WHERE id = %s", (proc, cam, db_id))
    
    conn.commit()
    print(f"✅ Done! Updated {len(rows)} rows with processor & camera_mp.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_and_update()
