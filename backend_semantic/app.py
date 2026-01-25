from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from rdflib import Graph, Namespace
import os

# --- KONFIGURASI ---
app = Flask(__name__)
CORS(app) # Izinkan Frontend Next.js akses kesini

# Ganti dengan API Key Groq Anda atau load dari env
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "") 

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

def get_market_prices(query=""):
    """Mengambil data harga real-time dari PostgreSQL"""
    products = []
    
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        if query:
            # PostgreSQL ILIKE is case-insensitive
            search_term = f"%{query}%"
            cur.execute("SELECT store_name, listing_title, price_idr, stock, item_condition FROM tb_market_listings WHERE listing_title ILIKE %s OR store_name ILIKE %s", (search_term, search_term))
        else:
            cur.execute("SELECT store_name, listing_title, price_idr, stock, item_condition FROM tb_market_listings LIMIT 20")
            
        rows = cur.fetchall()
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

def query_knowledge_graph(brand=None, min_ram=0):
    """Query SPARQL ke RDF File untuk cari kandidat HP berdasarkan spek"""
    query_str = """
    PREFIX ex: <http://example.org/gadget#>
    SELECT ?sku ?nama ?ram ?prosesor ?storage
    WHERE {
        ?hp a ex:Smartphone ;
            ex:hasModel ?nama ;
            ex:hasRAM ?ram ;
            ex:hasProcessor ?prosesor ;
            ex:hasStorage ?storage .
        BIND(STRAFTER(STR(?hp), "#") AS ?sku)
    """
    if brand:
        # Case insensitive regex filter karena RDF case sensitive
        query_str += f'    FILTER (regex(?nama, "{brand}", "i"))\n'
    if min_ram > 0:
        query_str += f'    FILTER (?ram >= {min_ram})\n'
    
    query_str += "}"

    results = g.query(query_str)
    candidates = {}
    for row in results:
        # Bersihkan ID (misal: sku_samsung_s24)
        clean_sku = str(row.sku).replace("sku_", "")
        candidates[clean_sku] = {
            "model": str(row.nama),
            "ram": int(row.ram),
            "processor": str(row.prosesor),
            "storage": int(row.storage)
        }
    return candidates

def get_augmented_data(user_query):
    """
    Inti dari RAG:
    1. Parse Intent sederhana (bisa diganti AI juga)
    2. Cari Candidates di KG (Spec)
    3. Cek Harga di Market API (Price)
    4. Gabungkan jadi Fakta
    """
    user_query = user_query.lower()
    
    # 1. Simple Intent Parsing (Logic sederhana dulu)
    brand_filter = None
    min_ram = 0
    budget = 0
    
    if "samsung" in user_query: brand_filter = "Samsung"
    if "iphone" in user_query or "apple" in user_query: brand_filter = "Apple"
    if "xiaomi" in user_query: brand_filter = "Xiaomi"
    if "poco" in user_query: brand_filter = "Poco"
    
    if "gaming" in user_query: min_ram = 8
    
    # Deteksi budget (sangat sederhana: cari angka + "juta")
    import re
    price_match = re.search(r'(\d+)\s*juta', user_query)
    if price_match:
        budget = int(price_match.group(1)) * 1000000
    
    # 2. Ambil Candidates dari KG
    candidates = query_knowledge_graph(brand_filter, min_ram)
    if not candidates:
        return [] # Tidak ada di knowledge base
        
    # 3. Ambil Harga & Stok Real-time
    #    Kita ambil semua data pasar (atau difilter per brand jika API PHP support)
    market_data = get_market_prices(brand_filter if brand_filter else "")
    
    # 4. Join Data (KG + Market)
    final_facts = []
    
    # Mapping market data ke dictionary biar cepat lookup by SKU/Nama
    # Asumsi: API Market return list object dengan field yang bisa dicocokkan
    # Karena kita gak punya SKU yang konsisten antara RDF dan DB (karena dummy),
    # kita coba match berdasarkan Nama Modalnya (fuzzy match logic)
    
    for sku, specs in candidates.items():
        found_in_market = False
        if market_data and isinstance(market_data, list):
            for item in market_data:
                # Simple logic: cek jika nama model ada di title listing
                if specs['model'].lower() in item.get('listing_title', '').lower():
                    price = float(item.get('price_idr', 0))
                    
                    # Filter Budget
                    if budget > 0 and price > budget:
                        continue
                        
                    fact = {
                        "model": specs['model'],
                        "specs": specs,
                        "price": price,
                        "store": item.get('store_name'),
                        "condition": item.get('item_condition'),
                        "stock": item.get('stock')
                    }
                    final_facts.append(fact)
                    found_in_market = True
        
        # Jika tidak ketemu di market, tapi ada di KG, bisa tetap dimasukkan sbg info (stok habis)
        if not found_in_market and budget == 0:
             # Opsional: Masukkan tapi tandai stok tidak diketahui
             pass

    return final_facts

def call_groq_llm(user_message, facts):
    """Kirim context fakta ke Groq untuk dijabarkan"""
    
    if not GROQ_API_KEY:
        return "⚠️ Server Error: GROQ_API_KEY belum diset di backend."

    # Susun System Prompt dengan Data
    system_prompt = """Kamu adalah GadgetBot, asisten penjualan HP yang cerdas.
Tugasmu adalah menjawab pertanyaan user BERDASARKAN data fakta yang diberikan di bawah ini.
JANGAN mengarang spesifikasi atau harga sendiri. Gunakan hanya data yang tersedia.

DATA FAKTA (Dari Knowledge Graph & Database Toko):
"""
    if not facts:
        system_prompt += "Tidak ditemukan produk yang cocok dengan kriteria dalam database kami.\n"
    else:
        for idx, f in enumerate(facts):
            system_prompt += f"{idx+1}. {f['model']} - Rp {f['price']:,}\n"
            system_prompt += f"   - Spek: RAM {f['specs']['ram']}GB, Processor {f['specs']['processor']}\n"
            system_prompt += f"   - Toko: {f['store']} (Kondisi: {f['condition']})\n"

    system_prompt += """
Instruksi:
- Jawab dengan ramah dan membantu.
- Jika ada produk yang cocok, rekomendasikan dan jelaskan kenapa bagus (dari speknya).
- Jika data kosong, minta maaf dan tawarkan pencarian lain.
- Format harga dalam Rupiah.
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
            "model": "qwen-2.5-32b", # Model Groq
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
    facts = get_augmented_data(user_message)
    print(f"📊 Facts Found: {len(facts)}")
    
    # 2. LLM Generation
    ai_response = call_groq_llm(user_message, facts)
    
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
