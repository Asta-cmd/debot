import os
import logging
import random
import string
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from datetime import datetime

load_dotenv()

# === Konfigurasi dari .env ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_TARGET = os.getenv("CHANNEL_TARGET")  # @username channel tujuan
REQUIRED_GROUPS = os.getenv("REQUIRED_GROUPS", "").split(",")  # 2 grup dan 1 channel
OWNER_ID = int(os.getenv("OWNER_ID"))

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Penyimpanan media ===
media_storage = {}
start_time = datetime.now()


# === Fungsi Helper ===
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def is_user_joined(chat_id: str, user_id: int, context: CallbackContext) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def check_subscription(user_id: int, context: CallbackContext) -> bool:
    for group in REQUIRED_GROUPS:
        if not await is_user_joined(group.strip(), user_id, context):
            return False
    return True


def build_fsub_keyboard():
    buttons = [
        [InlineKeyboardButton("JOIN CHANNEL", url=f"https://t.me/{REQUIRED_GROUPS[0].replace('@','')}")],
        [InlineKeyboardButton("JOIN GRUP ", url=f"https://t.me/{REQUIRED_GROUPS[1].replace('@','')}")],
        [InlineKeyboardButton("JOIN GRUP ", url=f"https://t.me/{REQUIRED_GROUPS[2].replace('@','')}")],
        [InlineKeyboardButton("COBA LAGI", callback_data="check_subs")]
    ]
    return InlineKeyboardMarkup(buttons)


# === Handler ===
async def start(update: Update, context: CallbackContext):
    args = context.args
    if args and args[0].startswith("media_"):
        code = args[0][6:]
        media = media_storage.get(code)
        user_id = update.effective_user.id

        if not media:
            await update.message.reply_text("❌ File tidak ditemukan.")
            return

        if not await check_subscription(user_id, context):
            await update.message.reply_text("👋 Untuk mengakses file ini, kamu harus join semua grup & channel dulu.", reply_markup=build_fsub_keyboard())
            return

        try:
            await context.bot.send_document(
                chat_id=user_id,
                document=media['file_id'],
                caption=media['caption'],
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error("❌ Gagal mengirim file:", exc_info=e)
            await update.message.reply_text("Terjadi kesalahan saat mengirim file.")

    else:
        await update.message.reply_text("👋 Halo! Kirimkan media (file/foto/video) lewat sini untuk membuat tautan unduhan.")


async def handle_media(update: Update, context: CallbackContext):
    message = update.effective_message
    user_id = update.effective_user.id

    if update.effective_chat.type != "private":
        return  # Hanya izinkan kirim media lewat private chat

    file = None
    file_id = None
    file_type = None

    if message.document:
        file = message.document
        file_id = file.file_id
        file_type = "document"
    elif message.photo:
        file = message.photo[-1]
        file_id = file.file_id
        file_type = "photo"
    elif message.video:
        file = message.video
        file_id = file.file_id
        file_type = "video"

    if not file_id:
        await update.message.reply_text("❌ File tidak dikenali.")
        return

    code = generate_code()
    media_storage[code] = {
        "file_id": file_id,
        "caption": message.caption or "",
        "file_type": file_type
    }

    # Kirim ke channel
    caption = f"{message.caption or 'Berikut adalah file Anda'}\n\n📎 Link: https://t.me/{context.bot.username}?start=media_{code}"
    try:
        await context.bot.send_document(
            chat_id=CHANNEL_TARGET,
            document=file_id,
            caption=caption
        )
        await update.message.reply_text(f"File berhasil diproses.\nLink: https://t.me/{context.bot.username}?start=media_{code}")
    except Exception as e:
        logger.error("❌ Gagal kirim ke channel:", exc_info=e)
        await update.message.reply_text("Terjadi kesalahan saat mengirim ke channel.")


async def check_subs_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if await check_subscription(user_id, context):
        await query.edit_message_text("Kamu sudah join semua grup & channel, silakan ulangi klik link-nya.")
    else:
        await query.edit_message_text("Sepertinya kamu belum join?.", reply_markup=build_fsub_keyboard())


async def ping(update: Update, context: CallbackContext):
    uptime = datetime.now() - start_time
    await update.message.reply_text(f"✅ Bot hidup\n🕒 Uptime: {uptime}")


async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Lu siapa anjir?.")

    text = update.message.text.split(" ", 1)
    if len(text) < 2:
        return await update.message.reply_text("Kirim seperti: /broadcast isi pesannya")

    message = text[1]
    success = 0
    failed = 0
    for user_id in set(media_storage.keys()):
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            success += 1
        except:
            failed += 1

    await update.message.reply_text(f"Broadcast selesai. ✅ {success}, ❌ {failed}")


async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error("Unhandled error:", exc_info=context.error)


# === Jalankan Bot ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(check_subs_callback, pattern="check_subs"))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, handle_media))

    app.add_error_handler(error_handler)
    app.run_polling()
