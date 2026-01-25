<?php
// Header agar browser membaca ini sebagai XML, bukan HTML biasa
header("Content-Type: text/xml; charset=UTF-8");

include 'db_connect.php';

$query = "SELECT * FROM tb_specs";
$result = mysqli_query($conn, $query);

// 1. Root Element
echo "<?xml version='1.0' encoding='UTF-8'?>";
echo "<katalog_gadget>";

while ($row = mysqli_fetch_assoc($result)) {
    // Membersihkan karakter aneh agar tidak merusak XML
    $model = htmlspecialchars($row['model']);
    
    // 2. Memulai Item Gadget
    echo "<gadget id='sku_" . $row['sku'] . "'>";
        echo "<model>" . $model . "</model>";
        echo "<brand>" . $row['brand'] . "</brand>";
        
        // 3. Nested Element (Struktur Bertingkat)
        echo "<teknis>";
            // Menambahkan Attribute 'satuan'
            echo "<processor>" . $row['processor'] . "</processor>";
            echo "<ram satuan='GB'>" . $row['ram_gb'] . "</ram>";
            echo "<storage satuan='GB'>" . $row['storage_gb'] . "</storage>";
            echo "<baterai satuan='mAh'>" . $row['battery_mah'] . "</baterai>";
            echo "<layar tipe='" . $row['screen_type'] . "'>" . $row['screen_size'] . "</layar>";
        echo "</teknis>";
        
        echo "<fitur>";
            echo "<nfc>" . $row['nfc_support'] . "</nfc>";
            echo "<jaringan>" . $row['network_type'] . "</jaringan>";
        echo "</fitur>";
        
    echo "</gadget>";
}

// 4. Tutup Root Element
echo "</katalog_gadget>";
?>