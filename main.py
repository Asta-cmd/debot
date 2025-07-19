import os
import sqlite3
import logging
from uuid import uuid4
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Logging agar error terlihat di log Railway/VPS
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Ambil token dan nama channel dari environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # contoh: @namachannel

# Setup database SQLite
conn = sqlite3.connect("media.db", check_same_thread=False)
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS media (
        code TEXT PRIMARY KEY,
        file_id TEXT NOT NULL
    )
''')
conn.commit()

# Error handler global
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("❌ Error saat memproses update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Terjadi kesalahan. Silakan coba lagi nanti.")

# Handler saat user kirim media
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        file_id = None

        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.video:
            file_id = message.video.file_id
        elif message.document:
            file_id = message.document.file_id
        else:
            await message.reply_text("Kirim foto, video, atau dokumen.")
            return

        # Buat kode unik dan simpan ke DB
        code = str(uuid4().hex[:10])
        cur.execute("INSERT INTO media (code, file_id) VALUES (?, ?)", (code, file_id))
        conn.commit()

        deeplink = f"https://t.me/{context.bot.username}?start=media_{code}"

        # Kirim ke channel
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=f"📎 File baru:\n{deeplink}"
        )

        await message.reply_text("✅ File berhasil dikonversi dan dikirim ke channel.")

    except Exception as e:
        logging.error("❌ Gagal menangani media:", exc_info=True)
        await update.message.reply_text("⚠️ Gagal memproses media.")

# Handler saat seseorang klik deeplink
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args or not args[0].startswith("media_"):
            await update.message.reply_text("Halo! Kirim file ke bot untuk mendapatkan tautan.")
            return

        code = args[0].replace("media_", "")
        cur.execute("SELECT file_id FROM media WHERE code = ?", (code,))
        row = cur.fetchone()

        if row:
            file_id = row[0]
            await update.message.reply_document(file_id)
        else:
            await update.message.reply_text("⚠️ File tidak ditemukan atau sudah kadaluarsa.")

    except Exception as e:
        logging.error("❌ Gagal memproses start handler:", exc_info=True)
        await update.message.reply_text("⚠️ Terjadi kesalahan saat mengambil file.")

# Jalankan bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()
        
