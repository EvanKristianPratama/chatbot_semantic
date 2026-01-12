from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
# Import logika semantik kita
import semantic_engine 

# --- GANTI TOKEN DI SINI ---
BOT_TOKEN = '8532630010:AAHHhX3ZjAA8lsu7PxHQfvGAxcxaKUAXYCE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya Assistant Gadget Semantik.\n\n"
        "Coba cari HP dengan format:\n"
        "- Ketik 'Samsung' untuk cari brand Samsung\n"
        "- Ketik 'Gaming' untuk cari HP RAM besar (diatas 8GB)\n"
        "- Ketik 'Murah' untuk cari HP dibawah 10 Juta (Contoh Logic)\n"
        "\nSilakan ketik kata kunci..."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan_user = update.message.text.lower() # Ubah ke huruf kecil semua
    
    # PERBAIKAN: Menghapus param 'quote=True' yang bikin error
    await update.message.reply_text("🔍 Menganalisis permintaan Anda...")
    
    # --- 1. DEFINISI KATA KUNCI (LOGIKA CERDAS) ---
    # Default parameters (kosong)
    param_brand = None
    param_ram = 0
    param_price = 0
    
    # Deteksi Brand (Bisa ditambah jika ada brand baru)
    if "samsung" in pesan_user:
        param_brand = "Samsung"
    elif "apple" in pesan_user or "iphone" in pesan_user:
        param_brand = "Apple"
    elif "xiaomi" in pesan_user or "poco" in pesan_user:
        param_brand = "Xiaomi"
    # Jika tidak ada brand disebut, param_brand tetap None (Artinya "Semua Brand")

    # Deteksi Kebutuhan Spek
    if "gaming" in pesan_user or "berat" in pesan_user or "kencang" in pesan_user:
        param_ram = 12 # Standar gaming kita: RAM min 12GB
    elif "standar" in pesan_user:
        param_ram = 4
    
    # Deteksi Kebutuhan Harga
    if "murah" in pesan_user or "budget" in pesan_user:
        param_price = 7000000 # Definisi "Murah" = dibawah 7 Juta (Bisa diatur)
    elif "flagship" in pesan_user or "mahal" in pesan_user:
        # Kalau cari flagship, kita tidak set batas harga
        pass 

    # --- 2. PANGGIL OTAK SEMANTIK ---
    # Kita kirim semua parameter yang berhasil diekstrak
    jawaban = semantic_engine.cari_rekomendasi(
        brand_dicari=param_brand, 
        min_ram=param_ram, 
        max_price=param_price
    )

    # Kirim Balasan
    await update.message.reply_text(jawaban, parse_mode='HTML')

if __name__ == '__main__':
    print("Bot sedang berjalan...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()