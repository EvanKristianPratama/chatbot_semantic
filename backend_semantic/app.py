from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from rdflib import Graph, Namespace
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# --- KONFIGURASI ---
app = Flask(__name__)
CORS(app) # Izinkan Frontend Next.js akses kesini

# Ganti dengan API Key Groq Anda atau load dari env
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Debug print to verify key loading
if GROQ_API_KEY.startswith("gsk_"):
    print(f"✅ GROQ_API_KEY loaded: {GROQ_API_KEY[:6]}...******")
else:
    print(f"⚠️ GROQ_API_KEY NOT LOADED CORRECTLY: '{GROQ_API_KEY}'") 

# URL API Toko (PHP Backend) - Pastikan ini jalan!
URL_API_HARGA = "http://localhost:8000/api_market.php"  
FILE_RDF = "knowledge_base.ttl"

# Setup RDF
EX = Namespace("http://example.org/gadget#")
g = Graph()
try:
    g.parse(FILE_RDF, format="turtle")
    print("✅ Knowledge Base Loaded!")
except Exception as e:
    print(f"❌ Error loading RDF: {e}")

# --- LOGIC SEMANTIC (MENGGANTIKAN SEMANTIC_ENGINE.PY LAMA) ---

import psycopg2
from urllib.parse import urlparse

# ... (Previous imports)

# Load Database URL from Environment (Render provides this automatically)
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- DATABASE CONNECTION ---
def get_db_connection():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set!")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return None

# --- LOGIC SEMANTIC ---

# ... (imports)

# --- LOGIC SEMANTIC ---

def get_market_prices(query="", max_price=0):
    """
    Mengambil data harga real-time dari PostgreSQL.
    - query: filter berdasarkan nama produk/toko (ILIKE)
    - max_price: filter berdasarkan harga maksimal (untuk search budget-only)
    """
    products = []
    
    print(f"DEBUG: Connecting to PostgreSQL... (query='{query}', max_price={max_price})")
    conn = get_db_connection()
    if not conn:
        print("❌ DEBUG: Failed to connect to DB")
        return []
        
    try:
        cur = conn.cursor()
        
        # Build dynamic query
        base_sql = "SELECT store_name, listing_title, price_idr, stock, item_condition FROM tb_market_listings WHERE 1=1"
        params = []
        
        if query:
            base_sql += " AND (listing_title ILIKE %s OR store_name ILIKE %s)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
            
        if max_price > 0:
            # Cari yang harganya di bawah budget * 1.2 (toleransi 20%)
            base_sql += " AND price_idr <= %s"
            params.append(max_price * 1.2)
            
        # Jika tidak ada filter sama sekali, batasi 50 item (diurutkan dari murah)
        if not query and max_price == 0:
            base_sql += " ORDER BY price_idr ASC LIMIT 50"
        else:
            base_sql += " ORDER BY price_idr ASC"
            
        print(f"DEBUG: Executing SQL: {base_sql[:100]}...")
        cur.execute(base_sql, tuple(params))
            
        rows = cur.fetchall()
        print(f"DEBUG: DB returned {len(rows)} rows")
        
        for row in rows:
            products.append({
                "store_name": row[0],
                "listing_title": row[1],
                "price_idr": float(row[2]),
                "stock": int(row[3]) if row[3] is not None else 0,
                "item_condition": row[4]
            })
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error query database: {e}")
        
    return products

# --- LOGIC SEMANTIC: QUERY RDF ---
def query_knowledge_graph(brand=None, min_ram=0, feature_concert=False):
    """
    SPARQL Query yang Lebih Pintar!
    Bisa cari berdasarkan Brand, RAM (Gaming), atau Fitur Konser (Zoom).
    """
    print(f"DEBUG: Querying KG for brand={brand}, min_ram={min_ram}, concert={feature_concert}")
    
    query_str = """
    PREFIX ex: <http://example.org/gadget#>
    SELECT ?sku ?nama ?ram ?prosesor ?storage
    WHERE {
        ?hp a ex:Smartphone ;
            ex:hasModel ?nama ;
            ex:hasBrand ?brand ;
            ex:hasRAM ?ram ;
            ex:hasProcessor ?prosesor ;
            ex:hasStorage ?storage .
        BIND(STRAFTER(STR(?hp), "#") AS ?sku)
    """
    
    # 1. Filter Brand (Regex di Property Brand)
    if brand:
        query_str += f'    FILTER (regex(?brand, "{brand}", "i"))\n'
        
    # 2. Filter Gaming (RAM Minimal)
    if min_ram > 0:
        query_str += f'    FILTER (?ram >= {min_ram})\n'
        
    # 3. Filter Konser (Cari yang namanya ada "Ultra" atau "Pro" atau "Pro Max")
    #    Asumsi: HP embel-embel ini punya Telephoto/Zoom bagus.
    if feature_concert:
        query_str += f'    FILTER (regex(?nama, "Ultra|Pro|Max", "i"))\n'
    
    query_str += "}"

    results = g.query(query_str)
    
    candidates = {}
    for row in results:
        clean_sku = str(row.sku).replace("sku_", "")
        candidates[clean_sku] = {
            "model": str(row.nama),
            "ram": int(row.ram),
            "processor": str(row.prosesor),
            "storage": int(row.storage)
        }
    return candidates

# --- LOGIC UTAMA: RAG CONTROLLER ---
def get_augmented_data(user_query):
    print(f"DEBUG: Analyzing intent for: {user_query}")
    user_query = user_query.lower()
    
    # --- 1. INTENT PARSING (Memahami Maunya User) ---
    brand_filter = None
    min_ram = 0
    budget = 0
    is_concert = False
    is_gaming = False
    is_affordable = False
    use_case_tags = []  # List untuk menyimpan konteks use-case
    
    # Keyword Brand
    if "samsung" in user_query: brand_filter = "Samsung"
    if "iphone" in user_query or "apple" in user_query: brand_filter = "Apple"
    if "xiaomi" in user_query or "redmi" in user_query: brand_filter = "Xiaomi"
    if "poco" in user_query: brand_filter = "Poco"
    if "vivo" in user_query: brand_filter = "Vivo"
    if "oppo" in user_query: brand_filter = "OPPO"
    if "realme" in user_query or "narzo" in user_query: brand_filter = "Realme"
    if "infinix" in user_query: brand_filter = "Infinix"
    if "tecno" in user_query: brand_filter = "Tecno"
    if "itel" in user_query: brand_filter = "Itel"
    if "nothing" in user_query: brand_filter = "Nothing"
    if "sony" in user_query or "xperia" in user_query: brand_filter = "Sony"
    if "huawei" in user_query: brand_filter = "Huawei"
    if "zte" in user_query: brand_filter = "ZTE"
    if "nokia" in user_query: brand_filter = "Nokia"
    if "lenovo" in user_query: brand_filter = "Lenovo"
    if "msi" in user_query: brand_filter = "MSI"
    if "acer" in user_query: brand_filter = "Acer"
    if "hp" in user_query and "victus" in user_query: brand_filter = "HP"
    if "nintendo" in user_query: brand_filter = "Nintendo"
    if "playstation" in user_query: brand_filter = "Sony"
    if "steam" in user_query and "deck" in user_query: brand_filter = "Valve"
    
    # Keyword Fitur
    if "gaming" in user_query or "game" in user_query or "pubg" in user_query or "ml" in user_query:
        min_ram = 8 # Gaming minimal RAM 8
        is_gaming = True
        use_case_tags.append("🎮 Gaming")
        
    if "konser" in user_query or "zoom" in user_query:
        is_concert = True # Trigger filter HP flagship (Pro/Ultra)
        use_case_tags.append("📸 Concert Camera")
        
    # --- USE CASE: OJOL (Driver Ojek Online) ---
    # Butuh: Baterai besar, harga murah, tahan lama
    if "ojol" in user_query or "ojek" in user_query or "gojek" in user_query or "grab" in user_query or "driver" in user_query:
        if budget == 0: budget = 3000000 # Max 3 juta
        is_affordable = True
        use_case_tags.append("🚴 Ojol (Baterai Awet)")
        
    # --- USE CASE: KULIAH (Mahasiswa) ---
    # Butuh: Bisa multitasking, kamera lumayan, budget friendly
    if "kuliah" in user_query or "mahasiswa" in user_query or "campus" in user_query or "pelajar" in user_query:
        if budget == 0: budget = 4000000 # Max 4 juta
        min_ram = 6
        is_affordable = True
        use_case_tags.append("📚 Kuliah/Sekolah")
        
    # --- USE CASE: ORANG TUA ---
    # Butuh: Layar besar, mudah digunakan, harga terjangkau
    if "orang tua" in user_query or "lansia" in user_query or "ibu" in user_query or "bapak" in user_query or "ortu" in user_query:
        if budget == 0: budget = 2500000 # Max 2.5 juta
        is_affordable = True
        use_case_tags.append("👴 Orang Tua (User Friendly)")
        
    # --- USE CASE: FOTOGRAFI ---
    if "foto" in user_query or "kamera" in user_query or "photography" in user_query or "selfie" in user_query:
        is_concert = True # HP flagship punya kamera bagus
        use_case_tags.append("📷 Fotografi")
        
    # --- USE CASE: TAHAN AIR / OUTDOOR ---
    if "tahan air" in user_query or "waterproof" in user_query or "ip68" in user_query or "outdoor" in user_query:
        is_concert = True # Flagship biasanya IP68
        use_case_tags.append("💧 Tahan Air (IP Rating)")
        
    # --- USE CASE: VIDEO CALL / WFH ---
    if "video call" in user_query or "zoom meeting" in user_query or "wfh" in user_query or "kerja" in user_query:
        min_ram = 6
        use_case_tags.append("💼 WFH/Video Call")
        
    # --- USE CASE: STREAMING / ENTERTAINMENT ---
    if "streaming" in user_query or "netflix" in user_query or "youtube" in user_query or "nonton" in user_query:
        min_ram = 4
        use_case_tags.append("📺 Streaming")
        
    # --- USE CASE: BISNIS / PROFESIONAL ---
    if "bisnis" in user_query or "profesional" in user_query or "kantor" in user_query or "meeting" in user_query:
        min_ram = 8
        use_case_tags.append("💼 Bisnis/Profesional")
        
    # --- USE CASE: ANAK-ANAK ---
    if "anak" in user_query or "kids" in user_query:
        if budget == 0: budget = 2000000
        is_affordable = True
        use_case_tags.append("👶 Untuk Anak")
        
    # Affordable logic (general)
    if "murah" in user_query or "terjangkau" in user_query or "affordable" in user_query or "budget" in user_query:
        is_affordable = True
        if budget == 0: budget = 5000000 # Set budget implisit 5 juta jika user tidak sebut angka
        
    # Keyword Budget Spesifik (misal "5 juta")
    import re
    price_match = re.search(r'(\d+)\s*juta', user_query)
    if price_match:
        budget = int(price_match.group(1)) * 1000000
    
    print(f"🎯 INTENT: Brand={brand_filter}, Gaming={is_gaming}, Konser={is_concert}, Budget={budget}, Tags={use_case_tags}")

    # --- 2. SEMANTIC SEARCH (Cari Kandidat di Otak) ---
    candidates = query_knowledge_graph(brand_filter, min_ram, is_concert)
    
    if not candidates:
        print("DEBUG: No candidates from KG")
        return []
        
    # --- 3. MARKET CHECK (Cek Harga di Database) ---
    # Fix Keyword Apple
    market_keyword = brand_filter if brand_filter else ""
    if brand_filter == "Apple": market_keyword = "iPhone"
        
    market_data = get_market_prices(market_keyword, max_price=budget)
    
    # --- 4. DATA FUSION (Gabungin Data) ---
    final_facts = []
    
    for sku, specs in candidates.items():
        if market_data:
            for item in market_data:
                # Fuzzy Match (Nama Model vs Judul Listing)
                if specs['model'].lower() in item.get('listing_title', '').lower():
                    price = float(item.get('price_idr', 0))
                    
                    # Logic Filter Budget
                    # Jika user minta "Affordable", kita tolak yang mahal (> 5jt) KECUALI dia sebut budget sendiri
                    if is_affordable and budget == 5000000 and price > 5000000:
                        continue
                        
                    # Jika user set budget spesifik
                    if budget > 0 and price > (budget * 1.2):
                        continue
                        
                    fact = {
                        "model": specs['model'],
                        "specs": specs,
                        "price": price,
                        "store": item.get('store_name'),
                        "condition": item.get('item_condition'),
                        "tags": []
                    }
                    
                    # Kasih Tagging biar AI tau kelebihannya
                    if specs['ram'] >= 12: fact['tags'].append("Gaming Beast 🎮")
                    if "Ultra" in specs['model'] or "Pro" in specs['model']: fact['tags'].append("Pro Camera 📸")
                    if price < 3000000: fact['tags'].append("Budget Friendly 💸")
                    
                    final_facts.append(fact)

    # Sort Harga (Murah ke  Mahal) biar rapi
    final_facts.sort(key=lambda x: x['price'])
    
    return final_facts, use_case_tags

def call_groq_llm(user_message, facts, use_case_tags=None):
    """Kirim context fakta ke Groq untuk dijabarkan"""
    
    if not GROQ_API_KEY:
        return "⚠️ Server Error: GROQ_API_KEY belum diset di backend."
    
    # --- SMART FILTERING: Prioritize products matching user query ---
    import re
    
    # Extract potential model keywords from user message (e.g., "17", "Pro", "Ultra")
    user_query_lower = user_message.lower()
    
    # Find specific model numbers (e.g., 17, 16, 15, SE)
    model_keywords = re.findall(r'\b(17|16|15|14|13|12|11|xr|xs|se|pro|max|ultra|plus)\b', user_query_lower)
    
    if model_keywords and facts:
        # Split into matching and non-matching products
        matching_facts = []
        other_facts = []
        
        for f in facts:
            model_lower = f['model'].lower()
            # Check if any keyword matches the model
            if any(kw in model_lower for kw in model_keywords):
                matching_facts.append(f)
            else:
                other_facts.append(f)
        
        # Combine: matching first, then others (up to 5 total)
        selected_facts = matching_facts[:5]  # Take matching ones first
        if len(selected_facts) < 5:
            selected_facts.extend(other_facts[:5 - len(selected_facts)])
        
        print(f"🎯 Smart Filter: {len(matching_facts)} matching, showing {len(selected_facts)}")
    else:
        # No specific keywords, use original top 5 cheapest
        selected_facts = facts[:5] if facts else []
    
    # Susun System Prompt dengan Data
    system_prompt = """Kamu adalah GadgetBot, asisten penjualan HP yang cerdas dan ramah.
Tugasmu adalah menjawab pertanyaan user BERDASARKAN data fakta yang diberikan di bawah ini.
JANGAN mengarang spesifikasi atau harga sendiri. Gunakan HANYA data yang tersedia.

DATA FAKTA (Dari Knowledge Graph & Database Toko):
"""
    if not selected_facts:
        system_prompt += "Tidak ditemukan produk yang cocok dengan kriteria dalam database kami.\n"
    else:
        for idx, f in enumerate(selected_facts):
            tags_str = ", ".join(f.get('tags', [])) if f.get('tags') else ""
            system_prompt += f"""
{idx+1}. **{f['model']}**
   💰 Harga: Rp {f['price']:,.0f}
   ⚙️ Spek: RAM {f['specs']['ram']}GB, Storage {f['specs']['storage']}GB, {f['specs']['processor']}
   🏪 Toko: {f['store']} ({f['condition']})
   🏷️ Tags: {tags_str}
"""

    # Tambahkan konteks use case jika ada
    use_case_context = ""
    if use_case_tags and len(use_case_tags) > 0:
        use_case_context = f"\nKonteks Kebutuhan User: {', '.join(use_case_tags)}"
    
    system_prompt += f"""
{use_case_context}

INSTRUKSI FORMAT JAWABAN:
Jawab dengan format yang RAPI dan TERSTRUKTUR seperti contoh berikut:

---
📱 **[Nama HP]**
💰 **Harga:** Rp X,XXX,XXX
⚙️ **Spesifikasi:**
   • RAM: X GB
   • Storage: X GB  
   • Processor: [Nama Processor]
   • Kamera: [Info Kamera jika ada]

✅ **Kenapa Cocok untuk [Kebutuhan User]:**
[Jelaskan 2-3 alasan spesifik kenapa HP ini cocok untuk kebutuhan mereka berdasarkan speknya]

🏪 **Tersedia di:** [Nama Toko] ([Kondisi: Baru/Bekas])
---

ATURAN PENTING:
1. Gunakan emoji untuk mempercantik tampilan
2. Jelaskan ALASAN kenapa HP itu cocok untuk kebutuhan user (konser, ojol, gaming, dll)
3. Maksimal rekomendasikan 3 HP saja, pilih yang paling relevan
4. Jika tidak ada data, minta maaf dan tawarkan pencarian lain dengan sopan
5. Selalu sebut toko dan kondisi barang
6. Format harga pakai titik pemisah ribuan (Rp 12.999.000)
"""

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "llama-3.3-70b-versatile", # Correct Model
            "temperature": 0.5
        }
        
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"Error from Groq: {resp.text}"
            
    except Exception as e:
        return f"Error calling AI: {e}"

# --- ROUTE API ---

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Message is empty"}), 400
        
    print(f"📩 Received: {user_message}")
    
    # 1. Semantic Retrieval (RAG)
    facts, use_case_tags = get_augmented_data(user_message)
    print(f"📊 Facts Found: {len(facts)}, Tags: {use_case_tags}")
    
    # 2. LLM Generation
    ai_response = call_groq_llm(user_message, facts, use_case_tags)
    
    return jsonify({
        "response": ai_response,
        "debug_facts": facts # Dikirim buat debug aja kalau mau lihat
    })

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "running",
        "service": "GadgetBot Semantic Backend",
        "endpoints": {
            "/chat": "POST - Main Chat Interface"
        },
        "knowledge_graph": "Loaded" if len(g) > 0 else "Empty",
        "market_api_url": URL_API_HARGA
    })

if __name__ == '__main__':
    # Jalankan server
    print("🚀 Semantic Backend Running on http://localhost:5001")
    app.run(port=5001, debug=True)
