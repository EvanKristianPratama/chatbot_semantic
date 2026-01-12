<?php
$host = "localhost";
$user = "root";      // Sesuaikan user database Anda
$pass = "";          // Sesuaikan password database Anda
$db   = "gadget_semantic_db";

$conn = mysqli_connect($host, $user, $pass, $db);

if (!$conn) {
    die("Koneksi gagal: " . mysqli_connect_error());
}
?>