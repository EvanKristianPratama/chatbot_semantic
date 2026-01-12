<?php
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE");

include 'db_connect.php';

// 1. Cek Metode HTTP apa yang digunakan oleh Client
$method = $_SERVER['REQUEST_METHOD'];

// 2. Ambil Input (Untuk metode POST dan PUT yang mengirim data JSON body)
$inputJSON = file_get_contents('php://input');
$input = json_decode($inputJSON, TRUE); // Ubah JSON jadi Array PHP

switch ($method) {
    
    // --- FITUR READ (Ambil Data) ---
    case 'GET':
        $sql = "SELECT * FROM tb_market_listings";
        
        // Jika ada parameter id (contoh: api_market.php?id=1)
        if (isset($_GET['id'])) {
            $id = mysqli_real_escape_string($conn, $_GET['id']);
            $sql .= " WHERE id = '$id'";
        }

        $result = mysqli_query($conn, $sql);
        $response = [];

        while ($row = mysqli_fetch_assoc($result)) {
            // Casting tipe data agar JSON valid
            $row['price_idr'] = (int)$row['price_idr'];
            $row['stock'] = (int)$row['stock'];
            $response[] = $row;
        }
        
        echo json_encode($response, JSON_PRETTY_PRINT);
        break;

    // --- FITUR CREATE (Tambah Data Baru) ---
    case 'POST':
        // Validasi input sederhana
        if(!isset($input['store_id']) || !isset($input['sku_ref'])) {
            http_response_code(400); // Bad Request
            echo json_encode(["message" => "Data tidak lengkap. store_id dan sku_ref wajib ada."]);
            exit();
        }

        $store_id = mysqli_real_escape_string($conn, $input['store_id']);
        $store_name = mysqli_real_escape_string($conn, $input['store_name']);
        $sku_ref = mysqli_real_escape_string($conn, $input['sku_ref']);
        $title = mysqli_real_escape_string($conn, $input['listing_title']);
        $price = (int)$input['price_idr'];
        $stock = (int)$input['stock'];
        $condition = mysqli_real_escape_string($conn, $input['item_condition']);

        $sql = "INSERT INTO tb_market_listings (store_id, store_name, sku_ref, listing_title, price_idr, stock, item_condition) 
                VALUES ('$store_id', '$store_name', '$sku_ref', '$title', $price, $stock, '$condition')";

        if (mysqli_query($conn, $sql)) {
            http_response_code(201); // Created
            echo json_encode(["message" => "Data berhasil ditambahkan", "id" => mysqli_insert_id($conn)]);
        } else {
            http_response_code(500); // Server Error
            echo json_encode(["message" => "Gagal menambah data: " . mysqli_error($conn)]);
        }
        break;

    // --- FITUR UPDATE (Edit Stok/Harga) ---
    case 'PUT':
        // Update butuh ID di URL (api_market.php?id=1)
        if (!isset($_GET['id'])) {
            http_response_code(400);
            echo json_encode(["message" => "Parameter ID wajib ada di URL untuk edit data."]);
            exit();
        }

        $id = mysqli_real_escape_string($conn, $_GET['id']);
        
        // Ambil data baru
        $price = (int)$input['price_idr'];
        $stock = (int)$input['stock'];
        $title = mysqli_real_escape_string($conn, $input['listing_title']);

        $sql = "UPDATE tb_market_listings SET 
                price_idr = $price, 
                stock = $stock,
                listing_title = '$title'
                WHERE id = '$id'";

        if (mysqli_query($conn, $sql)) {
            echo json_encode(["message" => "Data ID $id berhasil diupdate"]);
        } else {
            http_response_code(500);
            echo json_encode(["message" => "Gagal update: " . mysqli_error($conn)]);
        }
        break;

    // --- FITUR DELETE (Hapus Data) ---
    case 'DELETE':
        if (!isset($_GET['id'])) {
            http_response_code(400);
            echo json_encode(["message" => "Parameter ID wajib ada di URL untuk hapus data."]);
            exit();
        }

        $id = mysqli_real_escape_string($conn, $_GET['id']);
        $sql = "DELETE FROM tb_market_listings WHERE id = '$id'";

        if (mysqli_query($conn, $sql)) {
            echo json_encode(["message" => "Data ID $id berhasil dihapus"]);
        } else {
            http_response_code(500);
            echo json_encode(["message" => "Gagal hapus: " . mysqli_error($conn)]);
        }
        break;
        
    default:
        http_response_code(405); // Method Not Allowed
        echo json_encode(["message" => "Metode HTTP tidak didukung"]);
        break;
}
?>