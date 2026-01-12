<?php
// Header agar browser/aplikasi lain tahu ini data JSON
header("Content-Type: application/json; charset=UTF-8");

include 'db_connect.php';

// Query data
$query = "SELECT * FROM tb_market_listings";
$result = mysqli_query($conn, $query);

$response = array();

if (mysqli_num_rows($result) > 0) {
    // Loop data database
    while ($row = mysqli_fetch_assoc($result)) {
        // Konversi tipe data string angka menjadi integer sungguhan agar JSON rapi
        $item = array(
            'listing_id' => $row['id'],
            'store_info' => array( // Membuat nested JSON
                'id' => $row['store_id'],
                'name' => $row['store_name']
            ),
            'product' => array(
                'sku_ref' => $row['sku_ref'],
                'title' => $row['listing_title'],
                'condition' => $row['item_condition']
            ),
            'pricing' => array(
                'currency' => 'IDR',
                'amount' => (int)$row['price_idr'], // Casting ke integer
                'stock_available' => (int)$row['stock']
            )
        );
        
        // Masukkan item ke array utama
        array_push($response, $item);
    }
}

// Cetak array menjadi format JSON
// JSON_PRETTY_PRINT agar tampilan enak dibaca manusia
echo json_encode($response, JSON_PRETTY_PRINT);
?>