# 🤖 Telegram Auto-Reply AI Bot (Groq + Pyrogram)

Bot Telegram yang membalas pesan secara otomatis menggunakan AI dari Groq (Mixtral) dan mendukung berbagai mode kepribadian seperti marah, kalem, ngeselin, senja, dll.

---

## 🚀 Fitur Utama

- 🔁 Auto-reply berbasis AI (hanya jika pesan bot di-reply)
- 🔧 Mode karakter: `kalem`, `marah`, `ngeselin`, `drytext`, `jomok`, `senja`
- 🔒 Fitur `on/off` hanya untuk owner
- 🌍 `globalcast`: kirim pesan ke semua grup (hanya untuk owner)
- 🧠 Model AI: `mixtral-8x7b-32768` via [Groq API](https://console.groq.com)

---

## 🛠️ Persiapan

### 1. Buat akun dan ambil data berikut:

- [ ] **BOT_TOKEN** dari [@BotFather](https://t.me/BotFather)
- [ ] **API_ID** dan **API_HASH** dari [my.telegram.org](https://my.telegram.org/)
- [ ] **GROQ_API_KEY** dari [Groq Console](https://console.groq.com)
- [ ] **OWNER_ID** = ID Telegram kamu (bisa cek pakai bot @userinfobot)

---

## ⚙️ Konfigurasi Variabel Lingkungan

Buat file `.env` di direktori utama:

```env
API_ID=123456
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
OWNER_ID=123456789
