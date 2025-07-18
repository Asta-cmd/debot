from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from config import BOT_TOKEN, CHANNEL_ID
import logging

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# --- FSub Check ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- /start handler ---
@dp.message_handler(commands=['start'])
async def start_cmd(msg: types.Message):
    args = msg.get_args()

    if not await is_subscribed(msg.from_user.id):
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"),
            InlineKeyboardButton("🔄 Coba Lagi", callback_data="retry")
        )
        return await msg.answer("Kamu harus join channel dulu sebelum lanjut!", reply_markup=keyboard)

    if args:
        # --- Baca Menfes dari deeplink ---
        await msg.answer(f"📨 Kamu mendapat pesan anonim:\n\n\"{args}\"")
    else:
        await msg.answer("Ketik pesan anonim yang ingin kamu kirim. Balas pesan ini.")

# --- Menangani pesan biasa (Menfes) ---
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_menfes(msg: types.Message):
    if not await is_subscribed(msg.from_user.id):
        return await msg.reply("Gabung dulu ke channel sebelum bisa mengirim pesan.")

    encoded = msg.text.replace(" ", "_")
    deep_link = f"https://t.me/{(await bot.get_me()).username}?start={encoded}"
    await msg.reply(f"🔗 Bagikan link ini ke targetmu:\n{deep_link}")

# --- Tombol Retry ---
@dp.callback_query_handler(lambda c: c.data == 'retry')
async def retry_check(callback_query: types.CallbackQuery):
    if await is_subscribed(callback_query.from_user.id):
        await callback_query.message.edit_text("✅ Kamu sudah join! Sekarang kamu bisa lanjut.")
    else:
        await callback_query.answer("Kamu belum join!", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp)
    
