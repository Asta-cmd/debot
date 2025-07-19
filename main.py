import os
import sqlite3
import logging
from uuid import uuid4
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # contoh: @namachannel

# Database setup
conn = sqlite3.connect("media.db", check_same_thread=False)
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS media (
        code TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        file_type TEXT NOT NULL
    )
''')
conn.commit()

# Error handler global
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("❌ Exception caught:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Terjadi kesalahan. Silakan coba lagi nanti.")

# Saat user kirim media
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        file_id = None
        file_type = None

        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"
        else:
            await message.reply_text("Kirim foto, video, atau dokumen.")
            return

        code = str(uuid4().hex[:10])
        cur.execute("INSERT INTO media (code, file_id, file_type) VALUES (?, ?, ?)", (code, file_id, file_type))
        conn.commit()

        deeplink = f"https://t.me/{context.bot.username}?start=media_{code}"

        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=f"📎 File baru:\n{deeplink}"
        )

        await message.reply_text("✓File berhasil dikirim")

    except Exception as e:
        logging.error("❌ Gagal memproses media:", exc_info=True)
        await update.message.reply_text("⚠️ Gagal memproses media.")

# Saat user klik deeplink
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args or not args[0].startswith("media_"):
            await update.message.reply_text("Halo! Kirim file ke bot untuk mendapatkan tautan.")
            return

        code = args[0].replace("media_", "")
        cur.execute("SELECT file_id, file_type FROM media WHERE code = ?", (code,))
        row = cur.fetchone()

        if row:
            file_id, file_type = row

            if file_type == "photo":
                await update.message.reply_photo(file_id)
            elif file_type == "video":
                await update.message.reply_video(file_id)
            else:
                await update.message.reply_document(file_id)
        else:
            await update.message.reply_text("⚠️ File tidak ditemukan atau sudah kadaluarsa.")

    except Exception as e:
        logging.error("❌ Gagal memproses start handler:", exc_info=True)
        await update.message.reply_text("⚠️ Terjadi kesalahan saat mengambil file.")

# Jalankan aplikasi
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()
        
