import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    print(f"🔌 Connecting to: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM tb_market_listings")
    rows = cur.fetchall()
    
    print("\n✅ ISI DATABASE SAAT INI:")
    print("-" * 80)
    print(f"{'ID':<4} | {'Store':<20} | {'Model':<30} | {'Price':<15}")
    print("-" * 80)
    
    for row in rows:
        # row[0]=id, row[1]=store, row[2]=title, row[3]=price
        price_fmt = f"Rp {float(row[3]):,.0f}"
        print(f"{row[0]:<4} | {row[1]:<20} | {row[2]:<30} | {price_fmt:<15}")
        
    print("-" * 80)
    print(f"Total: {len(rows)} produk found.")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
