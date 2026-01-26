import psycopg2
import os
from dotenv import load_dotenv
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, RDFS

# Load environment variables
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
OUTPUT_FILE = "knowledge_base.ttl"

# Namespaces
EX = Namespace("http://example.org/gadget#")
SCHEMA = Namespace("http://schema.org/")

def clean_string(text):
    """Membersihkan string untuk jadi URI yang valid"""
    return str(text).replace(" ", "_").replace("/", "-").replace("(", "").replace(")", "").replace("+", "plus").lower()

def estimate_location(store_name):
    """Tebak lokasi berdasarkan nama toko"""
    store = store_name.lower()
    if "batam" in store: return "Batam"
    if "jakarta" in store or "jkt" in store or "ibox" in store or "digimap" in store or "erafone" in store: return "Jakarta"
    if "surabaya" in store: return "Surabaya"
    if "promo" in store or "official" in store: return "Online (Indonesia)"
    if "roxy" in store: return "Jakarta Pusat (Roxy)"
    if "mangga dua" in store: return "Jakarta Utara"
    return "Indonesia"

def estimate_brand(model_name):
    """Tebak brand dari nama model"""
    m = model_name.lower()
    if "samsung" in m or "galaxy" in m: return "Samsung"
    elif "iphone" in m or "apple" in m or "ipad" in m or "macbook" in m: return "Apple"
    elif "xiaomi" in m or "redmi" in m: return "Xiaomi"
    elif "poco" in m: return "Poco"
    elif "oppo" in m: return "OPPO"
    elif "vivo" in m: return "Vivo"
    elif "infinix" in m: return "Infinix"
    elif "pixel" in m: return "Google"
    elif "asus" in m or "rog" in m: return "Asus"
    elif "realme" in m or "narzo" in m: return "Realme"
    elif "tecno" in m: return "Tecno"
    elif "itel" in m: return "Itel"
    elif "nothing" in m: return "Nothing"
    elif "sony" in m or "xperia" in m: return "Sony"
    elif "huawei" in m or "matepad" in m: return "Huawei"
    elif "zte" in m or "blade" in m: return "ZTE"
    elif "nokia" in m: return "Nokia"
    elif "lenovo" in m: return "Lenovo"
    elif "msi" in m: return "MSI"
    elif "nintendo" in m: return "Nintendo"
    elif "playstation" in m or "ps5" in m: return "Sony"
    elif "steam deck" in m: return "Valve"
    return "Unknown"

def estimate_ram_storage(model_name):
    """Tebak RAM & Storage dari nama model"""
    import re
    m = model_name.lower()
    ram = 8
    storage = 128
    
    # Pattern: 8/256 or 8GB
    ram_match = re.search(r'(\d+)\s*(?:gb|/)\s*', m)
    if ram_match:
        val = int(ram_match.group(1))
        if val < 64:
            ram = val
    
    storage_match = re.search(r'(?:/|)(\d+)\s*gb', m)
    if storage_match:
        val = int(storage_match.group(1))
        if val > 16:
            storage = val
            
    return ram, storage

def generate_rdf():
    print(f"🔌 Connecting to DB to fetch products...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # FETCH SEMUA KOLOM LENGKAP
        cur.execute("""
            SELECT id, listing_title, store_name, price_idr, 
                   processor, camera_mp, telephoto, refresh_rate, suitable_for
            FROM tb_market_listings
        """)
        rows = cur.fetchall()
        
        # Init Graph
        g = Graph()
        g.bind("ex", EX)
        g.bind("schema", SCHEMA)
        
        # Definisi Ontology Lengkap
        g.add((EX.Smartphone, RDF.type, RDFS.Class))
        g.add((EX.hasModel, RDF.type, RDF.Property))
        g.add((EX.hasBrand, RDF.type, RDF.Property))
        g.add((EX.hasRAM, RDF.type, RDF.Property))
        g.add((EX.hasStorage, RDF.type, RDF.Property))
        g.add((EX.hasProcessor, RDF.type, RDF.Property))
        g.add((EX.hasMainCamera, RDF.type, RDF.Property))
        g.add((EX.hasTelephoto, RDF.type, RDF.Property))      # NEW
        g.add((EX.hasRefreshRate, RDF.type, RDF.Property))    # NEW
        g.add((EX.suitableFor, RDF.type, RDF.Property))       # NEW
        g.add((EX.batteryCapacity, RDF.type, RDF.Property))
        g.add((EX.soldBy, RDF.type, RDF.Property))
        g.add((EX.locatedIn, RDF.type, RDF.Property))
        g.add((EX.hasPrice, RDF.type, RDF.Property))

        print(f"🔄 Processing {len(rows)} products...")
        
        count = 0
        for row in rows:
            db_id = row[0]
            model_name = row[1]
            store_name = row[2] if row[2] else "Unknown Store"
            price = float(row[3]) if row[3] else 0
            db_processor = row[4] if row[4] else "Unknown"
            db_camera = row[5] if row[5] else 0
            db_telephoto = row[6] if row[6] is not None else False
            db_refresh_rate = row[7] if row[7] else 60
            db_suitable_for = row[8] if row[8] else ""
            
            # Buat Subject URI
            clean_id = clean_string(model_name)
            subject = EX[f"sku_{clean_id}"]
            
            # Estimate yang tidak ada di DB
            brand = estimate_brand(model_name)
            location = estimate_location(store_name)
            ram, storage = estimate_ram_storage(model_name)
            
            # Tambahkan Triples (LENGKAP)
            g.add((subject, RDF.type, EX.Smartphone))
            g.add((subject, RDFS.label, Literal(model_name)))
            g.add((subject, EX.hasModel, Literal(model_name)))
            g.add((subject, EX.hasBrand, Literal(brand)))
            g.add((subject, EX.hasPrice, Literal(int(price), datatype=XSD.integer)))
            g.add((subject, EX.soldBy, Literal(store_name)))
            g.add((subject, EX.locatedIn, Literal(location)))
            g.add((subject, EX.hasRAM, Literal(ram, datatype=XSD.integer)))
            g.add((subject, EX.hasStorage, Literal(storage, datatype=XSD.integer)))
            g.add((subject, EX.hasProcessor, Literal(db_processor)))
            g.add((subject, EX.hasMainCamera, Literal(db_camera, datatype=XSD.integer)))
            g.add((subject, EX.hasTelephoto, Literal(db_telephoto)))
            g.add((subject, EX.hasRefreshRate, Literal(db_refresh_rate, datatype=XSD.integer)))
            g.add((subject, EX.batteryCapacity, Literal(5000, datatype=XSD.integer)))  # Default
            
            # Add suitableFor tags (multiple values possible)
            if db_suitable_for:
                for tag in db_suitable_for.split(","):
                    if tag.strip():
                        g.add((subject, EX.suitableFor, Literal(tag.strip())))
            
            count += 1

        # Save to file
        g.serialize(destination=OUTPUT_FILE, format="turtle")
        print(f"✅ Success! Generated {count} items into '{OUTPUT_FILE}'")
        print("💡 Restart your backend app (`python app.py`) to load these changes.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_rdf()
