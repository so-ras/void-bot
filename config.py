import os
from dotenv import load_dotenv

load_dotenv()

# توکن ربات (از @BotFather بگیر)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8882672601:AAGJos3r1VJPYKiJuoPL9RW5kR3O92iezpA")

# آیدی عددی سازنده (از @userinfobot بگیر)
OWNER_ID = int(os.getenv("OWNER_ID", 1391789851))

# دیتابیس (برای Railway خودکار پر میشه)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")

# Redis (برای Railway خودکار پر میشه)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# تنظیمات پیشفرض
WARN_LIMIT = 3
FLOOD_LIMIT = 5
REWARD_ENABLED = True
DEFAULT_LANG = "fa"

# سمبل‌ها
SYMBOLS = {
    "success": "[+] ",
    "error": "[-] ",
    "warning": "[!] ",
    "info": "[*] ",
    "ban": "✖ ",
    "mute": "⊘ ",
    "warn": "⚠ ",
    "promote": "✦ ",
    "demote": "⬇ ",
    "lock": "☒ ",
    "unlock": "☐ ",
    "filter": "☢ ",
    "stats": "≡ ",
    "info": "ℹ ",
}
