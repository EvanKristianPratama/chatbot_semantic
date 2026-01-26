import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def estimate_telephoto(model_name):
    """Tebak apakah HP punya telephoto lens (biasanya flagship)"""
    m = model_name.lower()
    # Flagship biasanya punya telephoto
    if any(x in m for x in ["ultra", "pro max", "pro+", "s24", "s23", "s22", "find x", "x100", "pixel 9 pro", "iphone 15 pro", "iphone 16 pro", "iphone 17 pro"]):
        return True
    if any(x in m for x in ["note 14 pro", "poco f5", "poco f6", "realme gt"]):
        return True
    return False

def estimate_refresh_rate(model_name):
    """Tebak refresh rate layar"""
    m = model_name.lower()
    # Flagship biasanya 120Hz
    if any(x in m for x in ["ultra", "pro", "gaming", "rog", "poco f", "realme gt", "s24", "s23", "iphone 16", "iphone 15", "pixel 9", "pixel 8", "nothing phone", "z flip", "z fold"]):
        return 120
    # Mid-range biasanya 90Hz
    if any(x in m for x in ["redmi note", "poco m", "realme", "infinix note", "tecno camon", "vivo v", "oppo reno"]):
        return 90
    # Entry level 60Hz
    return 60

def estimate_suitable_for(model_name, price, battery, telephoto, refresh_rate):
    """Generate semantic tags berdasarkan kombinasi spek"""
    tags = []
    m = model_name.lower()
    
    # OJOL: Baterai besar (>=5000) + Murah (<3jt)
    if battery >= 5000 and price < 3000000:
        tags.append("Ojol")
        
    # CONCERT PHOTOGRAPHY: Punya Telephoto
    if telephoto:
        tags.append("ConcertPhotography")
        
    # GAMING: Refresh Rate tinggi + RAM besar (kita asumsikan dari nama)
    if refresh_rate >= 120 and any(x in m for x in ["gaming", "rog", "poco f", "realme gt", "ultra"]):
        tags.append("Gaming")
        
    # ELDERLY: Murah + Entry level
    if price < 2500000:
        tags.append("Elderly")
        
    # STUDENT: Budget friendly
    if 2000000 <= price <= 5000000:
        tags.append("Student")
        
    # PROFESSIONAL: Flagship
    if price > 15000000:
        tags.append("Professional")
    
    return tags

def migrate_complete():
    print("🔌 Connecting to Neon...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. Add columns if not exist
    print("➕ Adding columns (telephoto, refresh_rate, suitable_for)...")
    try:
        cur.execute("ALTER TABLE tb_market_listings ADD COLUMN IF NOT EXISTS telephoto BOOLEAN DEFAULT FALSE")
        cur.execute("ALTER TABLE tb_market_listings ADD COLUMN IF NOT EXISTS refresh_rate INTEGER DEFAULT 60")
        cur.execute("ALTER TABLE tb_market_listings ADD COLUMN IF NOT EXISTS suitable_for TEXT")
        conn.commit()
        print("✅ Columns added!")
    except Exception as e:
        print(f"⚠️ Column add warning: {e}")
        conn.rollback()

    # 2. Fetch all rows and update
    print("📦 Fetching products...")
    cur.execute("SELECT id, listing_title, price_idr FROM tb_market_listings")
    rows = cur.fetchall()
    
    print(f"🔄 Updating {len(rows)} products with telephoto, refresh_rate, suitable_for...")
    for row in rows:
        db_id = row[0]
        model_name = row[1]
        price = float(row[2]) if row[2] else 0
        battery = 5000  # Default assumption
        
        telephoto = estimate_telephoto(model_name)
        refresh_rate = estimate_refresh_rate(model_name)
        suitable_for_tags = estimate_suitable_for(model_name, price, battery, telephoto, refresh_rate)
        suitable_for_str = ",".join(suitable_for_tags) if suitable_for_tags else ""
        
        cur.execute(
            "UPDATE tb_market_listings SET telephoto = %s, refresh_rate = %s, suitable_for = %s WHERE id = %s", 
            (telephoto, refresh_rate, suitable_for_str, db_id)
        )
    
    conn.commit()
    print(f"✅ Done! Updated {len(rows)} rows with telephoto, refresh_rate, suitable_for.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_complete()
