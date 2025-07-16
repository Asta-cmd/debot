from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

BOT_TOKEN = os.getenv("BOT2_TOKEN")

def start(update: Update, context: CallbackContext):
    args = context.args
    param = args[0] if args else "tanpa parameter"
    update.message.reply_text(f"Hai! Kamu mengakses bot ini lewat deeplink dengan kode: {param}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()