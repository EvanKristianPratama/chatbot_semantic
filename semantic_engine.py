import requests
from rdflib import Graph, Namespace

# Konfigurasi
EX = Namespace("http://example.org/gadget#")
FILE_RDF = "knowledge_base.ttl"
URL_API_HARGA = "http://localhost/ws/tubes/api_market.php"

# Load Graph saat import
try:
    g = Graph()
    g.parse(FILE_RDF, format="turtle")
except Exception as e:
    print(f"Error loading RDF: {e}")

def get_harga_terkini():
    try:
        response = requests.get(URL_API_HARGA)
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def cari_rekomendasi(brand_dicari=None, min_ram=0, max_price=0):
    
    # --- 1. SPARQL (Filter Spek Teknis di RDF) ---
    query_str = """
    PREFIX ex: <http://example.org/gadget#>
    SELECT ?sku ?nama ?ram ?prosesor
    WHERE {
        ?hp a ex:Smartphone ;
            ex:hasModel ?nama ;
            ex:hasRAM ?ram ;
            ex:hasProcessor ?prosesor .
        BIND(STRAFTER(STR(?hp), "#") AS ?sku)
    """
    if brand_dicari:
        query_str += f'    ?hp ex:hasBrand "{brand_dicari}" .\n'
    if min_ram > 0:
        query_str += f'    FILTER (?ram >= {min_ram})\n'
    query_str += "}"

    hasil_sparql = g.query(query_str)
    
    kandidat_hp = {}
    for row in hasil_sparql:
        clean_sku = str(row.sku).replace("sku_", "")
        kandidat_hp[clean_sku] = {
            "nama": str(row.nama),
            "ram": str(row.ram),
            "prosesor": str(row.prosesor)
        }
    
    if not kandidat_hp:
        return "❌ Tidak ada HP di database spek yang cocok dengan kriteria teknis tersebut."

    # --- 2. API & Filter Harga ---
    data_pasar = get_harga_terkini()
    hasil_pesan = [] 
    ada_barang = False

    for penawaran in data_pasar:
        if 'sku_ref' in penawaran:
            sku_toko = penawaran['sku_ref']
            
            if sku_toko in kandidat_hp:
                harga_barang = int(penawaran['price_idr'])

                # Filter Harga
                if max_price > 0 and harga_barang > max_price:
                    continue

                ada_barang = True
                info = kandidat_hp[sku_toko]
                harga_fmt = f"Rp {harga_barang:,}"
                
                teks = (f"📱 <b>{info['nama']}</b> ({penawaran['item_condition']})\n"
                        f"⚙️ Spek: RAM {info['ram']}GB, {info['prosesor']}\n"
                        f"💰 Harga: {harga_fmt}\n"
                        f"🏪 Toko: {penawaran['store_name']}\n")
                hasil_pesan.append(teks)

    if not ada_barang:
        if max_price > 0:
            return f"❌ Ditemukan HP sesuai spek, tapi harganya di atas budget Rp {max_price:,}."
        return "❌ Barang ditemukan secara teknis, tapi stok kosong di toko."
    
    header = f"🔍 <b>Hasil Pencarian:</b>\nBrand: {brand_dicari if brand_dicari else 'Semua'}\n"
    if min_ram > 0: header += "Spek: Gaming (High RAM)\n"
    
    # PERBAIKAN DISINI: Mengganti '<' menjadi '&lt;' agar aman dibaca Telegram
    if max_price > 0: header += f"Budget: &lt; Rp {max_price:,}\n"
    
    return header + "\n" + "\n".join(hasil_pesan)