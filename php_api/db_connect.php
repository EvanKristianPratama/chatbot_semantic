<?php
// Konfigurasi Database
$host = 'localhost';
$db_name = 'gadget_db';
$username = 'root'; // Default XAMPP/MAMP usually 'root'
$password = 'Himalaya44';     // Default XAMPP empty, MAMP usually 'root'

try {
    $conn = new PDO("mysql:host=$host;dbname=$db_name", $username, $password);
    // Set Error Mode ke Exception agar gampang debug
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // echo "Connected successfully"; 
} catch(PDOException $e) {
    // Jika gagal connect, return JSON error
    header('Content-Type: application/json');
    echo json_encode(["success" => false, "message" => "DB Connection Failed: " . $e->getMessage()]);
    exit();
}
?>
