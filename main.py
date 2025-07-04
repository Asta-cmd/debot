import os
import logging
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from groq import Groq

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

bot = Client("groq_bot", apimport os
import logging
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from groq import Groq

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

bot = Client("groq_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

BOT_STATUS = {"active": True}
BOT_MODE = {"mode": "kalem"}

MODES = ["kalem", "marah", "ngeselin", "drytext", "jomok", "senja"]

SYSTEM_MESSAGES = {
    "kalem": "Balas dengan sopan dan tenang, gunakan bahasa yang ramah.",
    "marah": "Balas dengan nada marah dan kasar. Jangan ramah sama sekali.",
    "ngeselin": "Balas dengan cara menyebalkan, sindir, dan buat kesal lawan bicara.",
    "drytext": "Balas dengan singkat, tanpa ekspresi, tanpa emoji, tanpa basa-basi.",
    "jomok": "Balas seperti orang jomok, gunakan bahasa khas seperti 'cik', 'wak', dan selipkan humor norak.",
    "senja": "Balas dengan puitis dan dalam, seperti orang yang suka senja dan kopi."
}

@bot.on_message(filters.command("on") & filters.user(OWNER_ID))
def turn_on(_, msg: Message):
    BOT_STATUS["active"] = True
    msg.reply("Bot diaktifkan ✅")

@bot.on_message(filters.command("off") & filters.user(OWNER_ID))
def turn_off(_, msg: Message):
    BOT_STATUS["active"] = False
    msg.reply("Bot dinonaktifkan ❌")

@bot.on_message(filters.command("setmode") & filters.user(OWNER_ID))
def set_mode(_, msg: Message):
    if len(msg.command) < 2:
        return msg.reply("Contoh: /setmode marah")
    mode = msg.command[1]
    if mode not in MODES:
        return msg.reply(f"Mode tidak dikenal. Pilih salah satu: {', '.join(MODES)}")
    BOT_MODE["mode"] = mode
    msg.reply(f"Mode diubah ke: {mode}")

@bot.on_message(filters.command("globalcast") & filters.user(OWNER_ID))
async def globalcast_handler(_, msg: Message):
    if not msg.reply_to_message:
        return msg.reply("Balas pesan yang ingin dikirim ke semua grup.")
    text = msg.reply_to_message.text
    sent = 0
    failed = 0
    async for dialog in bot.iter_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await bot.send_message(dialog.chat.id, text)
                sent += 1
            except Exception as e:
                logging.warning(f"Gagal kirim ke {dialog.chat.id}: {e}")
                failed += 1
    await msg.reply(f"✅ Terkirim ke {sent} grup\n❌ Gagal: {failed} grup")

@bot.on_message(filters.text & ~filters.private)
async def ai_reply(_, msg: Message):
    if not BOT_STATUS["active"]:
        return
    if not msg.reply_to_message or msg.reply_to_message.from_user.id != (await bot.get_me()).id:
        return
    prompt = msg.text
    system_message = SYSTEM_MESSAGES.get(BOT_MODE["mode"], SYSTEM_MESSAGES["kalem"])
    try:
        chat_completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        reply_text = chat_completion.choices[0].message.content.strip()
        await msg.reply(reply_text)
    except Exception as e:
        logging.error(f"Error saat membalas: {e}")
        await msg.reply("Maaf, terjadi kesalahan saat menjawab.")

if __name__ == "__main__":
    print("Bot sedang berjalan...")
    bot.run()
i_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

BOT_STATUS = {"active": True}
BOT_MODE = {"mode": "kalem"}

MODES = ["kalem", "marah", "ngeselin", "drytext", "jomok", "senja"]

SYSTEM_MESSAGES = {
    "kalem": "Balas dengan sopan dan tenang, gunakan bahasa yang ramah.",
    "marah": "Balas dengan nada marah dan kasar. Jangan ramah sama sekali.",
    "ngeselin": "Balas dengan cara menyebalkan, sindir, dan buat kesal lawan bicara.",
    "drytext": "Balas dengan singkat, tanpa ekspresi, tanpa emoji, tanpa basa-basi.",
    "jomok": "Balas seperti orang jomok, gunakan bahasa khas seperti 'cik', 'wak', dan selipkan humor norak.",
    "senja": "Balas dengan puitis dan dalam, seperti orang yang suka senja dan kopi."
}

@bot.on_message(filters.command("on") & filters.user(OWNER_ID))
def turn_on(_, msg: Message):
    BOT_STATUS["active"] = True
    msg.reply("Bot diaktifkan ✅")

@bot.on_message(filters.command("off") & filters.user(OWNER_ID))
def turn_off(_, msg: Message):
    BOT_STATUS["active"] = False
    msg.reply("Bot dinonaktifkan ❌")

@bot.on_message(filters.command("setmode") & filters.user(OWNER_ID))
def set_mode(_, msg: Message):
    if len(msg.command) < 2:
        return msg.reply("Contoh: /setmode marah")
    mode = msg.command[1]
    if mode not in MODES:
        return msg.reply(f"Mode tidak dikenal. Pilih salah satu: {', '.join(MODES)}")
    BOT_MODE["mode"] = mode
    msg.reply(f"Mode diubah ke: {mode}")

@bot.on_message(filters.command("globalcast") & filters.user(OWNER_ID))
async def globalcast_handler(_, msg: Message):
    if not msg.reply_to_message:
        return msg.reply("Balas pesan yang ingin dikirim ke semua grup.")
    text = msg.reply_to_message.text
    sent = 0
    failed = 0
    async for dialog in bot.iter_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await bot.send_message(dialog.chat.id, text)
                sent += 1
            except Exception as e:
                logging.warning(f"Gagal kirim ke {dialog.chat.id}: {e}")
                failed += 1
    await msg.reply(f"✅ Terkirim ke {sent} grup\n❌ Gagal: {failed} grup")

@bot.on_message(filters.text & ~filters.private)
async def ai_reply(_, msg: Message):
    if not BOT_STATUS["active"]:
        return
    if not msg.reply_to_message or msg.reply_to_message.from_user.id != (await bot.get_me()).id:
        return
    prompt = msg.text
    system_message = SYSTEM_MESSAGES.get(BOT_MODE["mode"], SYSTEM_MESSAGES["kalem"])
    try:
        chat_completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        reply_text = chat_completion.choices[0].message.content.strip()
        await msg.reply(reply_text)
    except Exception as e:
        logging.error(f"Error saat membalas: {e}")
        await msg.reply("Maaf, terjadi kesalahan saat menjawab.")

if __name__ == "__main__":
    print("Bot sedang berjalan...")
    bot.run()
