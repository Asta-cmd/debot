import os
import sqlite3
import logging
from uuid import uuid4
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

# ENV CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")  # format: @namachannel
REQUIRED_GROUP = os.getenv("REQUIRED_GROUP")      # format: -100...

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# SQLite
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

# Cek keanggotaan
async def is_user_member(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# Proses pengiriman file jika sudah join
async def send_file_if_allowed(update, context, code):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    in_channel = await is_user_member(context.bot, REQUIRED_CHANNEL, user_id)
    in_group = await is_user_member(context.bot, REQUIRED_GROUP, user_id)

    if not (in_channel and in_group):
        buttons = [
            [InlineKeyboardButton("JOIN CHANNEL", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")],
            [InlineKeyboardButton("COBA LAGI", callback_data=f"recheck_{code}")]
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text="🚫 Untuk mengakses file ini, kamu harus join channel & grup terlebih dahulu.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    cur.execute("SELECT file_id, file_type FROM media WHERE code = ?", (code,))
    row = cur.fetchone()

    if row:
        file_id, file_type = row
        if file_type == "photo":
            await context.bot.send_photo(chat_id=chat_id, photo=file_id)
        elif file_type == "video":
            await context.bot.send_video(chat_id=chat_id, video=file_id)
        else:
            await context.bot.send_document(chat_id=chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ File tidak ditemukan.")

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].startswith("media_"):
        await update.message.reply_text("Halo! Kirim file ke bot untuk mendapatkan tautan.")
        return

    code = args[0].replace("media_", "")
    await send_file_if_allowed(update, context, code)

# Callback tombol "Saya sudah join"
async def handle_recheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("recheck_"):
        code = query.data.replace("recheck_", "")
        user_id = query.from_user.id
        chat_id = query.message.chat.id

        in_channel = await is_user_member(context.bot, REQUIRED_CHANNEL, user_id)
        in_group = await is_user_member(context.bot, REQUIRED_GROUP, user_id)

        if not (in_channel and in_group):
            await query.message.reply_text("❗ Kamu belum join semuanya.")
            return

        cur.execute("SELECT file_id, file_type FROM media WHERE code = ?", (code,))
        row = cur.fetchone()

        if row:
            file_id, file_type = row
            if file_type == "photo":
                await context.bot.send_photo(chat_id=chat_id, photo=file_id)
            elif file_type == "video":
                await context.bot.send_video(chat_id=chat_id, video=file_id)
            else:
                await context.bot.send_document(chat_id=chat_id, document=file_id)
        else:
            await query.message.reply_text("⚠️ File tidak ditemukan.")

# Terima media (hanya dari DM)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type != "private":
            return

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

        code = uuid4().hex[:10]
        cur.execute("INSERT INTO media (code, file_id, file_type) VALUES (?, ?, ?)", (code, file_id, file_type))
        conn.commit()

        deeplink = f"https://t.me/{context.bot.username}?start=media_{code}"

        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=f"📎 File baru:\n{deeplink}"
        )

        await message.reply_text("✓ File sudah terkirim")

    except Exception as e:
        logging.error("❌ Gagal memproses media:", exc_info=True)
        await update.message.reply_text("⚠️ Gagal memproses media.")

# Error global
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("❌ Exception caught:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Terjadi kesalahan. Silakan coba lagi nanti.")

# Run bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))
    app.add_handler(CallbackQueryHandler(handle_recheck))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()
                                  
