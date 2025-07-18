from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN

def start(update: Update, context: CallbackContext):
    args = context.args
    if args:
        joined_text = " ".join(args)
        update.message.reply_text(f"📨 Kamu membuka link dengan pesan:\n\n\"{joined_text}\"")
    else:
        update.message.reply_text("Kirim aku pesan biasa, nanti kubuatkan link deeplink-nya!")

def generate_link(update: Update, context: CallbackContext):
    text = update.message.text
    encoded = text.replace(" ", "_")
    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={encoded}"
    update.message.reply_text(f"🔗 Ini link deeplink-mu:\n{link}")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_link))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
