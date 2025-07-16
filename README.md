# Deeplink Telegram Bot System

Dua bot Telegram yang saling terhubung dengan deeplink.
- Bot 1 mengirim media + tombol ke channel.
- Bot 2 menerima klik deeplink dan membalas user.

## Struktur Environment Variables (Railway)

### Bot 1:
- `BOT1_TOKEN` = Token Bot 1
- `CHANNEL_ID` = ID Channel tempat kirim media (format: -100xxxxxx)
- `BOT2_USERNAME` = Username bot 2 (tanpa @)

### Bot 2:
- `BOT2_TOKEN` = Token Bot 2

## Deploy di Railway
1. Deploy dua project terpisah di Railway (Bot1 dan Bot2).
2. Tambahkan environment variables sesuai README ini.
3. Jalankan, dan kirim perintah `/start` ke Bot1 untuk uji coba.