from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Updater, CommandHandler
import os

BOT_TOKEN = os.getenv("BOT1_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT2_USERNAME = os.getenv("BOT2_USERNAME")  # tanpa @

def start(update, context):
    button = InlineKeyboardButton("COBA SEKARANG", url=f"https://t.me/{BOT2_USERNAME}?start=media123")
    markup = InlineKeyboardMarkup([[button]])

    context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo="https://placekitten.com/600/400",
        caption="Klik tombol di bawah untuk melanjutkan.",
        reply_markup=markup
    )

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()