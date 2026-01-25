import requests
import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, RDF, RDFS, Namespace
from rdflib.namespace import XSD

# 1. Konfigurasi Namespace
EX = Namespace("http://example.org/gadget#")
SCHEMA = Namespace("http://schema.org/") 

g = Graph()
g.bind("ex", EX)
g.bind("schema", SCHEMA)

# 2. Ambil Data XML (Sesuaikan URL jika beda folder)
url_xml = "http://localhost/ws/tubes/xml_specs.php" 

print(f"Sedang mengambil data dari {url_xml}...")

try:
    response = requests.get(url_xml)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        
        print("Mulai konversi XML ke RDF...")
        
        for gadget in root.findall('gadget'):
            sku = gadget.get('id') 
            model_name = gadget.find('model').text
            brand_name = gadget.find('brand').text
            
            hp_uri = EX[sku] 
            
            # Type Definition
            g.add((hp_uri, RDF.type, EX.Smartphone))
            g.add((hp_uri, RDF.type, SCHEMA.Product))
            
            # Properties
            g.add((hp_uri, EX.hasModel, Literal(model_name, datatype=XSD.string)))
            g.add((hp_uri, RDFS.label, Literal(model_name))) 
            g.add((hp_uri, EX.hasBrand, Literal(brand_name)))
            
            # Teknis (Perbaikan di sini: 'is not None')
            teknis = gadget.find('teknis')
            if teknis is not None:
                proc = teknis.find('processor').text
                g.add((hp_uri, EX.hasProcessor, Literal(proc)))
                
                ram = teknis.find('ram').text
                g.add((hp_uri, EX.hasRAM, Literal(int(ram), datatype=XSD.integer)))
                
                storage = teknis.find('storage').text
                g.add((hp_uri, EX.hasStorage, Literal(int(storage), datatype=XSD.integer)))
                
                screen = teknis.find('layar').text
                g.add((hp_uri, EX.hasScreenSize, Literal(float(screen), datatype=XSD.float)))

        # 4. Simpan ke File
        output_file = "knowledge_base.ttl"
        g.serialize(destination=output_file, format="turtle")
        print(f"Sukses! Data RDF tersimpan di '{output_file}'")
        print(f"Total Triple: {len(g)}")
        
    else:
        print(f"Gagal mengambil XML. Kode: {response.status_code}")

except Exception as e:
    print(f"Terjadi Error: {e}")