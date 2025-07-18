import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, CHANNEL_ID

DATA_FILE = "media_data.json"

# Load database
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Simpan database
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def start(update: Update, context: CallbackContext):
    args = context.args
    if args:
        key = args[0]
        data = load_data()
        entry = data.get(key)

        if not entry:
            update.message.reply_text("❌ Data tidak ditemukan atau sudah dihapus.")
            return

        file_type = entry["type"]
        file_id = entry["file_id"]

        if file_type == "photo":
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id)
        elif file_type == "video":
            context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)
        elif file_type == "document":
            context.bot.send_document(chat_id=update.effective_chat.id, document=file_id)
        else:
            update.message.reply_text("⚠️ Jenis media tidak dikenali.")
    else:
        update.message.reply_text("Kirim media (foto/video/dokumen) agar kubuatkan link-nya.")

def generate_deeplink(update: Update, context: CallbackContext):
    bot_username = context.bot.username
    data = load_data()

    # Validasi hanya terima media
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        key = f"photo_{file_id}"
        data[key] = {"type": "photo", "file_id": file_id}

    elif update.message.video:
        file_id = update.message.video.file_id
        key = f"video_{file_id}"
        data[key] = {"type": "video", "file_id": file_id}

    elif update.message.document:
        file_id = update.message.document.file_id
        key = f"document_{file_id}"
        data[key] = {"type": "document", "file_id": file_id}

    else:
        update.message.reply_text("⚠️ Hanya kirim media (foto, video, dokumen) untuk generate link!")
        return

    save_data(data)

    # Generate link
    link = f"https://t.me/{bot_username}?start={key}"
    update.message.reply_text(f"🔗 Link kamu:\n{link}")

    # Forward link ke channel (anonim)
    context.bot.send_message(chat_id=CHANNEL_ID, text=f"📤 Anonim mengirim media:\n{link}")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, generate_deeplink))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
        
