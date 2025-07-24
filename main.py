import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Waktu terakhir restart
start_time = datetime.now()

# Variabel dari .env atau hardcode sementara
BOT_TOKEN = os.getenv("BOT_TOKEN", "ISI_TOKEN_BOT")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
REQUIRED_GROUPS = os.getenv("REQUIRED_GROUPS", "-100123,-100456").split(",")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "-100789")

# Simpan media
MEDIA_DB = {}

def get_deeplink(code: str):
    return f"https://t.me/{os.getenv('BOT_USERNAME', 'YourBotUsername')}?start=media_{code}"

async def is_user_member(bot, user_id: int, chat_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

async def validate_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    bot = context.bot
    not_joined = []

    if REQUIRED_CHANNEL and not await is_user_member(bot, user_id, int(REQUIRED_CHANNEL)):
        not_joined.append(("Join Channel", f"https://t.me/c/{str(REQUIRED_CHANNEL)[4:]}"))

    for group_id in REQUIRED_GROUPS:
        group_id = group_id.strip()
        if group_id and not await is_user_member(bot, user_id, int(group_id)):
            not_joined.append(("Join Grup", f"https://t.me/c/{str(group_id)[4:]}"))

    if not_joined:
        tombol = [[InlineKeyboardButton(nama, url=link)] for nama, link in not_joined]
        tombol.append([InlineKeyboardButton("Coba Lagi", callback_data="check_join")])
        await update.message.reply_text(
            " Untuk membuka media silahkan klik join lalu coba lagi. pastikan sudah join semua.",
            reply_markup=InlineKeyboardMarkup(tombol)
        )
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/start media_"):
        code = update.message.text.split("_")[1]
        if not await validate_membership(update, context):
            return

        if code in MEDIA_DB:
            file_type, file_id, caption = MEDIA_DB[code]
            if file_type == "photo":
                await update.message.reply_photo(photo=file_id, caption=caption)
            elif file_type == "video":
                await update.message.reply_video(video=file_id, caption=caption)
            elif file_type == "document":
                await update.message.reply_document(document=file_id, caption=caption)
        else:
            await update.message.reply_text(" File tidak ditemukan.")
    else:
        await update.message.reply_text(" Halo! Kirim file ke bot ini lewat pesan pribadi.")

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    file_id = None
    file_type = None
    caption = update.message.caption or ""

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_type = "video"
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"

    if file_id and file_type:
        code = str(len(MEDIA_DB) + 1).zfill(6)
        MEDIA_DB[code] = (file_type, file_id, caption)

        deeplink = get_deeplink(code)
        await update.message.reply_text(
            f"✅ File sudah terkirim!\n\n🔗 Link: {deeplink}"
        )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = datetime.now() - start_time
    await update.message.reply_text(f"✅ Bot hidup\n⏱ Uptime: {uptime}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.split(" ", 1)
    if len(text) < 2:
        await update.message.reply_text("Gunakan: /broadcast isi pesan")
        return

    msg = text[1]
    success = 0
    for user_id in set(update.message.bot_data.get("users", [])):
        try:
            await context.bot.send_message(chat_id=user_id, text=msg)
            success += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast terkirim ke {success} user.")

async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        context.bot_data.setdefault("users", set()).add(update.effective_user.id)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(MessageHandler(filters.ALL, save_user))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, media_handler))

    app.run_polling()
    
