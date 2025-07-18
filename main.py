from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, CHANNEL_ID

def start(update: Update, context: CallbackContext):
    args = context.args
    if args:
        joined_text = " ".join(args)
        update.message.reply_text(f"📨 Kamu membuka link dengan konten:\n\n\"{joined_text}\"")
    else:
        update.message.reply_text("Kirim foto, video, atau dokumen agar kubuatkan deeplink.")

def generate_deeplink(update: Update, context: CallbackContext):
    bot_username = context.bot.username

    # Hanya izinkan media, tolak teks biasa
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        link = f"https://t.me/{bot_username}?start=photo_{file_id}"
        update.message.reply_text(f"🔗 Link untuk foto:\n{link}")
        context.bot.send_message(chat_id=CHANNEL_ID, text=f"📤 Anonim mengirim foto:\n{link}")

    elif update.message.video:
        file_id = update.message.video.file_id
        link = f"https://t.me/{bot_username}?start=video_{file_id}"
        update.message.reply_text(f"🔗 Link untuk video:\n{link}")
        context.bot.send_message(chat_id=CHANNEL_ID, text=f"📤 Anonim mengirim video:\n{link}")

    elif update.message.document:
        file_id = update.message.document.file_id
        link = f"https://t.me/{bot_username}?start=document_{file_id}"
        update.message.reply_text(f"🔗 Link untuk dokumen:\n{link}")
        context.bot.send_message(chat_id=CHANNEL_ID, text=f"📤 Anonim mengirim dokumen:\n{link}")

    else:
        update.message.reply_text("⚠️ Hanya kirim media (foto, video, atau dokumen) untuk generate link!")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, generate_deeplink))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
