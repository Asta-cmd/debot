import os
import sqlite3
from uuid import uuid4
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

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

# Saat user kirim media
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # Simpan file_id ke database
    code = str(uuid4().hex[:10])
    cur.execute("INSERT INTO media (code, file_id) VALUES (?, ?)", (code, file_id))
    conn.commit()

    deeplink = f"https://t.me/{context.bot.username}?start=media_{code}"

    # Kirim link ke channel
    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=f"📎 File baru:\n{deeplink}"
    )

    await message.reply_text("✅ File berhasil dikonversi dan dikirim ke channel.")

# Saat link deeplink diklik
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Langsung jalankan polling (tanpa asyncio.run)
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))

    print("Bot is running...")
    app.run_polling()
    
