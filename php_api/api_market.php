<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");

include_once 'db_connect.php';

// Ambil keyword pencarian dari URL parameter ?search=...
$search = isset($_GET['search']) ? $_GET['search'] : '';

try {
    if (!empty($search)) {
        // Query Sederhana: Cari di title atau store name
        // Menggunakan prepared statement untuk mencegah SQL Injection
        $query = "SELECT * FROM tb_market_listings 
                  WHERE listing_title LIKE :search 
                  OR store_name LIKE :search 
                  ORDER BY price_idr ASC";
        
        $stmt = $conn->prepare($query);
        $searchTerm = "%{$search}%";
        $stmt->bindParam(':search', $searchTerm);
    } else {
        // Jika tidak ada search, ambil semua (limit 20)
        $query = "SELECT * FROM tb_market_listings ORDER BY id DESC LIMIT 20";
        $stmt = $conn->prepare($query);
    }

    $stmt->execute();
    $products = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Pastikan harga jadi integer/float (kadang string dari DB)
    foreach ($products as &$product) {
        $product['price_idr'] = (float)$product['price_idr'];
        $product['stock'] = (int)$product['stock'];
    }

    echo json_encode($products); // Return Array of objects langsung biar gampang diambil Python

} catch (Exception $e) {
    echo json_encode(["error" => $e->getMessage()]);
}
?>
