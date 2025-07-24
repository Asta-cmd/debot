import os
import json
import time
from uuid import uuid4
from dotenv import load_dotenv
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_GROUP = os.getenv("REQUIRED_GROUP", "").split()
CHANNEL_TARGET = os.getenv("CHANNEL_TARGET")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

DATA_FILE = "database.json"
start_time = time.time()

# Load database
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        file_db = json.load(f)
else:
    file_db = {}

async def save_database():
    with open(DATA_FILE, "w") as f:
        json.dump(file_db, f)

def generate_code():
    return str(uuid4())[:8]

def build_fsub_keyboard():
    buttons = [
        [InlineKeyboardButton("Join Sekarang", url=f"https://t.me/{group.lstrip('-100')}")]
        for group in REQUIRED_GROUP
    ]
    buttons.append([InlineKeyboardButton("CobaLagi", callback_data="check_fsub")])
    return InlineKeyboardMarkup(buttons)

async def check_user_joined(bot: Bot, user_id: int) -> bool:
    for group_id in REQUIRED_GROUP:
        try:
            member = await bot.get_chat_member(group_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if not args or not args[0].startswith("media_"):
        await update.message.reply_text("Kirim file ke bot ini secara private.")
        return

    code = args[0].split("_", 1)[1]
    if code not in file_db:
        await update.message.reply_text("❌ File tidak ditemukan.")
        return

    if not await check_user_joined(context.bot, user.id):
        await update.message.reply_text("Silakan join channel/grup terlebih dahulu:", reply_markup=build_fsub_keyboard())
        return

    file_info = file_db[code]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")

    if file_info["type"] == "photo":
        await update.message.reply_photo(file_info["file_id"], caption=file_info["caption"])
    elif file_info["type"] == "video":
        await update.message.reply_video(file_info["file_id"], caption=file_info["caption"])
    else:
        await update.message.reply_document(file_info["file_id"], caption=file_info["caption"])

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    media = update.message
    file = None
    media_type = ""
    caption = media.caption or ""

    if media.photo:
        file = media.photo[-1]
        media_type = "photo"
    elif media.video:
        file = media.video
        media_type = "video"
    elif media.document:
        file = media.document
        media_type = "document"

    if not file:
        await update.message.reply_text("File tidak dikenali.")
        return

    code = generate_code()
    file_db[code] = {
        "file_id": file.file_id,
        "type": media_type,
        "caption": caption
    }
    await save_database()

    deeplink = f"https://t.me/{context.bot.username}?start=media_{code}"

    await context.bot.send_message(
        chat_id=CHANNEL_TARGET,
        text=f"{caption}\n\n🔗 {deeplink}"
    )

    await update.message.reply_text(f"Tautan file kamu:\n{deeplink}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_fsub":
        if await check_user_joined(context.bot, query.from_user.id):
            await query.edit_message_text("Verifikasi berhasil! Klik ulang link.")
        else:
            await query.edit_message_text("Kamu belum join semua grup/channel.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - start_time
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)
    await update.message.reply_text(
        f"✅ Bot aktif\n⏱ Uptime: {hours}h {minutes}m {seconds}s"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Ga usah nakal, Lu siapa?.")

    text = update.message.text.split(" ", 1)
    if len(text) < 2:
        return await update.message.reply_text("Kirimkan pesan seperti:\n`/broadcast Halo semua`", parse_mode="Markdown")

    msg = text[1]
    success, failed = 0, 0

    for user_id in set(update.chat_data.get("users", [])):
        try:
            await context.bot.send_message(chat_id=user_id, text=msg)
            success += 1
        except:
            failed += 1

    await update.message.reply_text(f"📢 Terkirim: {success}, Gagal: {failed}")

async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user and update.effective_chat.type == "private":
        chat_data = context.chat_data
        chat_data.setdefault("users", set()).add(update.effective_user.id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.ALL, track_user), group=1)
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
