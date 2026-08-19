# -*- coding: utf-8 -*-
"""
ربات استیکرساز حرفه‌ای — نسخه ۴

تغییرات نسبت به نسخه‌ی قبل:
  1) 🌐 انتخاب زبان واقعی: با /start دو دکمه‌ی «🇮🇷 فارسی» و «🇬🇧 English» میاد،
     و بعد از انتخاب، تمام منو/پیام‌ها فقط با همون زبان نشون داده می‌شن
     (نه هر دو زبان با هم). زبان انتخابی توی دیتابیس ذخیره می‌شه.
  2) 🖼 رفع باگ «عکس تبدیل به استیکر نمی‌شه»: خروجی حالا WEBP فشرده‌شده و
     زیر ۵۱۲ کیلوبایته (محدودیت خود تلگرام برای استیکر استاتیک) و خطاهای
     واقعی تلگرام (نه فقط تداخل اسم) مستقیم به کاربر نشون داده می‌شن.
  3) ✨ رفع مشکل «OPENAI_API_KEY ست نشده»: اگه این کلید رو نداشته باشی،
     به‌صورت خودکار از یک سرویس رایگان و بدون نیاز به کلید
     (pollinations.ai) برای ساخت تصویر استفاده می‌شه. اگه OPENAI_API_KEY
     رو ست کنی، کیفیت بهتر OpenAI جایگزینش می‌شه.

پیش‌نیازها:
    pip install "python-telegram-bot==21.4" pillow rembg onnxruntime openai

متغیرهای محیطی:
    BOT_TOKEN        (اجباری)
    OPENAI_API_KEY   (اختیاری - اگه نباشه از سرویس رایگان استفاده می‌شه)
    DB_PATH          (اختیاری)

اجرا (هم برای تست روی Pydroid 3 هم روی Railway از همین یک فایل استفاده می‌شه):
    export BOT_TOKEN="..."
    python sticker_bot_pro_v4.py
"""

import base64
import io
import logging
import os
import random
import re
import sqlite3
import string
import urllib.parse
from typing import List, Optional

import httpx
from PIL import Image

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputSticker,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Sticker,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# تنظیمات
# ---------------------------------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8767515768:AAF3wlo79AMjfjEHlrRkFiwT7PCVw9izR0I")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DB_PATH = os.environ.get("DB_PATH", "sticker_bot.db")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WAITING_TITLE = 1
WAITING_PACK_CHOICE = 2
WAITING_TEXT_PROMPT = 3

CREATE_CHUNK = 50
STICKER_SIZE = 512
MAX_STICKER_BYTES = 512_000  # محدودیت تلگرام برای استیکر استاتیک

DEFAULT_LANG = "fa"

# ---------------------------------------------------------------------------
# متن‌ها و دکمه‌ها به تفکیک زبان
# ---------------------------------------------------------------------------

BUTTONS = {
    "fa": {
        "clone": "📦 کپی پک استیکر",
        "photo": "🖼 استیکر از عکس",
        "ai": "✨ استیکر با هوش مصنوعی",
        "help": "📖 راهنما",
        "cancel": "❌ لغو",
        "lang_switch": "🌐 تغییر زبان",
        "my_packs": "📦 پک‌های ساخته‌شده‌ی من",
    },
    "en": {
        "clone": "📦 Clone Pack",
        "photo": "🖼 Photo → Sticker",
        "ai": "✨ AI Text → Sticker",
        "help": "📖 Help",
        "cancel": "❌ Cancel",
        "lang_switch": "🌐 Change Language",
        "my_packs": "📦 My Created Packs",
    },
}

TEXTS = {
    "fa": {
        "welcome": (
            "سلام! 👋✨ به ربات استیکرساز حرفه‌ای خوش اومدی.\n\n"
            "از دکمه‌های پایین صفحه استفاده کن 👇\n\n"
            "📦 کپی کردن یک پک کامل\n"
            "🖼 ساخت استیکر از روی عکس (حذف خودکار پس‌زمینه)\n"
            "✨ ساخت استیکر با هوش مصنوعی از روی متن\n"
            "📖 راهنمای کامل"
        ),
        "help": (
            "📖 راهنمای کامل\n\n"
            "📦 کپی کردن پک:\n"
            "   دکمه‌ی «کپی پک استیکر» رو بزن، بعد یک استیکر از پکی که می‌خوای "
            "کپی بشه برام بفرست. اسم پک جدید رو می‌پرسم و 🎁 پک کامل رو می‌سازم.\n\n"
            "🖼 ساخت استیکر از عکس:\n"
            "   دکمه‌ی «استیکر از عکس» رو بزن، بعد یه عکس بفرست. پس‌زمینه‌ش رو "
            "خودکار حذف می‌کنم و ✂️ به سایز استاندارد استیکر تبدیلش می‌کنم.\n\n"
            "✨ ساخت استیکر با AI:\n"
            "   دکمه‌ی «استیکر با هوش مصنوعی» رو بزن، بعد توضیح بده چی می‌خوای "
            "(مثلاً: 🐱 یک گربه‌ی کارتونی با عینک آفتابی).\n\n"
            "بعد از ساخت هر استیکر، انتخاب کن برای «پک جدید ➕» باشه یا یکی از "
            "پک‌های قبلی‌ت 📦.\n\n"
            "❌ هر موقع خواستی، دکمه‌ی «لغو» رو بزن."
        ),
        "guide_clone": "📦✨ حالا یه استیکر از پکی که می‌خوای کپی بشه برام بفرست.",
        "guide_photo": "🖼✨ یه عکس (به‌صورت عکس، نه فایل) برام بفرست تا تبدیلش کنم به استیکر.",
        "not_pack_sticker": "🚫 این استیکر متعلق به پکی نیست. یه استیکر دیگه بفرست.",
        "fetching_pack": "⏳📦 در حال دریافت پک «{name}» ...",
        "fetch_pack_failed": "❌ نتونستم پک رو بگیرم: {err}",
        "pack_no_stickers": "🚫 این پک هیچ استیکری نداره.",
        "clone_found": "✅ {n} استیکر پیدا شد 🎉 اسم پک جدید رو بفرست:",
        "processing_photo": "⏳🖼 در حال پردازش عکس ...",
        "photo_failed": "❌ خطا در پردازش عکس: {err}",
        "choose_pack_prompt": "🎯 این استیکر به کدوم پک اضافه بشه؟",
        "new_pack_btn": "➕ پک جدید",
        "ask_new_title": "✏️ اسم پک جدید رو بفرست:",
        "add_error": "❌ خطا در اضافه کردن: {err}",
        "sticker_added": "🎉✅ استیکر اضافه شد!\n\n{link}",
        "ask_more": "🙌 چیز دیگه‌ای می‌خوای بسازی؟",
        "gen_ask_prompt": "✨🖊 توضیح استیکر مورد نظرت رو بنویس (مثلاً: 🐱 یک گربه با عینک آفتابی):",
        "gen_empty_prompt": "🚫 لطفاً یه توضیح متنی بفرست.",
        "gen_generating": "🎨✨ در حال تولید تصویر با AI ...",
        "gen_failed": "❌ خطا در تولید تصویر: {err}",
        "gen_image_process_failed": "❌ خطا در پردازش تصویر: {err}",
        "title_invalid": "🚫 لطفاً یه اسم معتبر بفرست.",
        "title_generic_error": "⚠️ مشکلی پیش اومد.",
        "nothing_to_build": "⚠️ چیزی برای ساخت پک پیدا نشد.",
        "building_pack": "⏳🛠 در حال ساخت پک جدید ...",
        "pack_create_failed": "❌ خطا در ساخت پک: {err}",
        "pack_unique_fail": "❌ نتونستم اسم یکتا پیدا کنم، دوباره امتحان کن.",
        "pack_ready": "🎉🎁 پک آماده شد!\n\n{link}",
        "pack_some_failed": "\n\n⚠️ {n} استیکر اضافه نشدن.",
        "cancelled": "❌ عملیات لغو شد.",
        "choose_lang": "🌐 لطفاً زبانت رو انتخاب کن:",
        "lang_set": "✅ زبان فارسی شد.",
        "my_packs_empty": "🚫 هنوز هیچ پکی نساختی.",
        "my_packs_header": "📦 پک‌های ساخته‌شده‌ی تو:\n\n",
        "my_packs_item": "🔸 {title}\n{link}\n\n",
    },
    "en": {
        "welcome": (
            "Hi! 👋✨ Welcome to the Pro Sticker Maker Bot.\n\n"
            "Use the buttons below 👇\n\n"
            "📦 Clone an entire pack\n"
            "🖼 Make a sticker from a photo (auto background removal)\n"
            "✨ Make a sticker with AI from text\n"
            "📖 Full guide"
        ),
        "help": (
            "📖 Full Guide\n\n"
            "📦 Clone a pack:\n"
            "   Tap \"Clone Pack\", then send one sticker from any pack. I'll "
            "ask for a title and 🎁 build the full pack for you.\n\n"
            "🖼 Sticker from photo:\n"
            "   Tap \"Photo → Sticker\", then send a photo. I'll auto-remove "
            "the background ✂️ and resize it to the sticker standard.\n\n"
            "✨ Sticker with AI:\n"
            "   Tap \"AI Text → Sticker\", then describe what you want "
            "(e.g. 🐱 a cartoon cat wearing sunglasses).\n\n"
            "After any sticker is made, choose \"New pack ➕\" or one of your "
            "existing packs 📦.\n\n"
            "❌ Tap \"Cancel\" any time to stop."
        ),
        "guide_clone": "📦✨ Now send me one sticker from the pack you want to clone.",
        "guide_photo": "🖼✨ Send me a photo (as a photo, not a file) to turn into a sticker.",
        "not_pack_sticker": "🚫 This sticker doesn't belong to a pack. Send another one.",
        "fetching_pack": "⏳📦 Fetching pack «{name}» ...",
        "fetch_pack_failed": "❌ Failed to fetch pack: {err}",
        "pack_no_stickers": "🚫 This pack has no stickers.",
        "clone_found": "✅ Found {n} stickers 🎉 Send the title for the new pack:",
        "processing_photo": "⏳🖼 Processing photo ...",
        "photo_failed": "❌ Image processing failed: {err}",
        "choose_pack_prompt": "🎯 Which pack should this go to?",
        "new_pack_btn": "➕ New pack",
        "ask_new_title": "✏️ Send the title for the new pack:",
        "add_error": "❌ Failed to add: {err}",
        "sticker_added": "🎉✅ Sticker added!\n\n{link}",
        "ask_more": "🙌 Want to make something else?",
        "gen_ask_prompt": "✨🖊 Describe the sticker you want (e.g. 🐱 a cat wearing sunglasses):",
        "gen_empty_prompt": "🚫 Please send a text description.",
        "gen_generating": "🎨✨ Generating image with AI ...",
        "gen_failed": "❌ Image generation failed: {err}",
        "gen_image_process_failed": "❌ Image processing failed: {err}",
        "title_invalid": "🚫 Please send a valid title.",
        "title_generic_error": "⚠️ Something went wrong.",
        "nothing_to_build": "⚠️ Nothing to build the pack from.",
        "building_pack": "⏳🛠 Building the new pack ...",
        "pack_create_failed": "❌ Pack creation failed: {err}",
        "pack_unique_fail": "❌ Couldn't find a unique name, try again.",
        "pack_ready": "🎉🎁 Pack is ready!\n\n{link}",
        "pack_some_failed": "\n\n⚠️ {n} stickers failed to add.",
        "cancelled": "❌ Cancelled.",
        "choose_lang": "🌐 Please choose your language:",
        "lang_set": "✅ Language set to English.",
        "my_packs_empty": "🚫 You haven't created any packs yet.",
        "my_packs_header": "📦 Your created packs:\n\n",
        "my_packs_item": "🔸 {title}\n{link}\n\n",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else DEFAULT_LANG
    text = TEXTS[lang].get(key, TEXTS[DEFAULT_LANG].get(key, key))
    return text.format(**kwargs) if kwargs else text


def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    b = BUTTONS.get(lang, BUTTONS[DEFAULT_LANG])
    return ReplyKeyboardMarkup(
        [
            [b["clone"]],
            [b["photo"]],
            [b["ai"]],
            [b["my_packs"]],
            [b["help"], b["cancel"]],
            [b["lang_switch"]],
        ],
        resize_keyboard=True,
    )


def cancel_only_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """موقع انجام یه عملیات (منتظر عکس/استیکر/عنوان/متن)، منوی کامل بسته
    می‌شه و فقط دکمه‌ی لغو نشون داده می‌شه."""
    b = BUTTONS.get(lang, BUTTONS[DEFAULT_LANG])
    return ReplyKeyboardMarkup([[b["cancel"]]], resize_keyboard=True)


LANG_CHOICE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="LANG_fa"),
            InlineKeyboardButton("🇬🇧 English", callback_data="LANG_en"),
        ]
    ]
)

# دستورات متنی بدون / که مستقل از زبان انتخابی همیشه شناسایی می‌شن
RE_START = re.compile(r"^(شروع|استارت|start)$", re.IGNORECASE)
RE_CANCEL = re.compile(r"^(لغو|کنسل|cancel)$", re.IGNORECASE)
RE_GEN_TRIGGER = re.compile(
    r"^(ساخت با متن|ساخت استیکر با متن|متن به استیکر|generate|gen|text to sticker)$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# دیتابیس: پک‌های کاربر + زبان انتخابی کاربر
# ---------------------------------------------------------------------------

def db_init() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_packs (
            user_id INTEGER NOT NULL,
            set_name TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_lang (
            user_id INTEGER PRIMARY KEY,
            lang TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def db_add_pack(user_id: int, set_name: str, title: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO user_packs (user_id, set_name, title) VALUES (?, ?, ?)",
        (user_id, set_name, title),
    )
    conn.commit()
    conn.close()


def db_get_packs(user_id: int) -> List[tuple]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT set_name, title FROM user_packs WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def db_set_lang(user_id: int, lang: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO user_lang (user_id, lang) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang",
        (user_id, lang),
    )
    conn.commit()
    conn.close()


def db_get_lang(user_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT lang FROM user_lang WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row else None


def get_lang(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    """زبان کاربر رو اول از کش گفتگو، بعد دیتابیس، وگرنه پیش‌فرض می‌گیره."""
    lang = context.user_data.get("lang")
    if lang:
        return lang
    lang = db_get_lang(user_id) or DEFAULT_LANG
    context.user_data["lang"] = lang
    return lang


# ---------------------------------------------------------------------------
# توابع کمکی مشترک
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    ascii_only = ascii_only.strip("_")
    if not ascii_only:
        ascii_only = "pack"
    if not ascii_only[0].isalpha():
        ascii_only = "p_" + ascii_only
    return ascii_only[:20]


def random_suffix(n: int = 5) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def build_set_name(title: str, bot_username: str) -> str:
    base = slugify(title)
    suffix = random_suffix()
    name = f"{base}_{suffix}_by_{bot_username}"
    return name[:64]


def chunk_list(items: List, size: int):
    for i in range(0, len(items), size):
        yield items[i: i + size]


def is_name_conflict_error(msg: str) -> bool:
    """فقط خطاهای مربوط به تداخل/نامعتبربودن اسم پک رو تشخیص می‌ده، نه خطاهای دیگه (مثل حجم تصویر)."""
    msg = msg.lower()
    return (
        "occupied" in msg
        or "already" in msg
        or ("name" in msg and "invalid" in msg)
        or "chosen name" in msg
    )


# ---------------------------------------------------------------------------
# دستورات/دکمه‌های عمومی: شروع، انتخاب زبان، راهنما، لغو
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = db_get_lang(user_id)
    if lang:
        context.user_data["lang"] = lang
        await update.message.reply_text(t(lang, "welcome"), reply_markup=main_keyboard(lang))
    else:
        # هنوز زبان انتخاب نشده - هر دو گزینه رو نشون بده
        await update.message.reply_text(
            "🌐 لطفاً زبانت رو انتخاب کن / Please choose your language:",
            reply_markup=LANG_CHOICE_KEYBOARD,
        )


async def on_lang_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = "fa" if query.data == "LANG_fa" else "en"
    user_id = update.effective_user.id
    db_set_lang(user_id, lang)
    context.user_data["lang"] = lang

    await query.edit_message_text(t(lang, "lang_set"))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t(lang, "welcome"),
        reply_markup=main_keyboard(lang),
    )


async def switch_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🌐 لطفاً زبانت رو انتخاب کن / Please choose your language:",
        reply_markup=LANG_CHOICE_KEYBOARD,
    )


async def cancel_to_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دکمه‌ی لغو وقتی هیچ عملیاتی در حال انجام نیست (بیرون از هر گفتگو):
    منوی پایین بسته می‌شه و صفحه‌ی انتخاب زبان دوباره میاد."""
    lang = get_lang(context, update.effective_user.id)
    context.user_data.pop("mode", None)
    await update.message.reply_text(t(lang, "cancelled"), reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "🌐 لطفاً زبانت رو انتخاب کن / Please choose your language:",
        reply_markup=LANG_CHOICE_KEYBOARD,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(context, update.effective_user.id)
    await update.message.reply_text(t(lang, "help"), reply_markup=main_keyboard(lang))


async def show_my_packs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """📦 لیست پک‌هایی که کاربر تا الان با این ربات ساخته، به همراه لینکشون."""
    lang = get_lang(context, update.effective_user.id)
    user_id = update.effective_user.id
    packs = db_get_packs(user_id)

    if not packs:
        await update.message.reply_text(t(lang, "my_packs_empty"), reply_markup=main_keyboard(lang))
        return

    text = t(lang, "my_packs_header")
    for set_name, title in packs:
        link = f"https://t.me/addstickers/{set_name}"
        text += t(lang, "my_packs_item", title=title, link=link)

    await update.message.reply_text(
        text, reply_markup=main_keyboard(lang), disable_web_page_preview=True
    )


async def show_clone_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(context, update.effective_user.id)
    await update.message.reply_text(t(lang, "guide_clone"), reply_markup=main_keyboard(lang))


async def show_photo_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(context, update.effective_user.id)
    await update.message.reply_text(t(lang, "guide_photo"), reply_markup=main_keyboard(lang))


async def fallback_clone_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("mode", None)
    await show_clone_guide(update, context)
    return ConversationHandler.END


async def fallback_photo_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("mode", None)
    await show_photo_guide(update, context)
    return ConversationHandler.END


async def fallback_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("mode", None)
    await help_cmd(update, context)
    return ConversationHandler.END


async def fallback_my_packs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("mode", None)
    await show_my_packs(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context, update.effective_user.id)
    context.user_data.pop("mode", None)
    await update.message.reply_text(t(lang, "cancelled"), reply_markup=main_keyboard(lang))
    return ConversationHandler.END


# فیلترهای متنی که به هر دو زبان دکمه واکنش نشون بدن
def buttons_for(key: str) -> List[str]:
    return [BUTTONS["fa"][key], BUTTONS["en"][key]]


FILTER_START = filters.Regex(RE_START)
FILTER_LANG_SWITCH = filters.Text(buttons_for("lang_switch"))
FILTER_HELP = filters.Text(buttons_for("help")) | filters.Regex(r"^(راهنما|کمک|help)$")
FILTER_CANCEL = filters.Text(buttons_for("cancel")) | filters.Regex(RE_CANCEL)
FILTER_GEN_TRIGGER = filters.Text(buttons_for("ai")) | filters.Regex(RE_GEN_TRIGGER)
FILTER_CLONE_GUIDE = filters.Text(buttons_for("clone"))
FILTER_PHOTO_GUIDE = filters.Text(buttons_for("photo"))
FILTER_MY_PACKS = filters.Text(buttons_for("my_packs"))
FILTER_ANY_MENU_BUTTON = (
    filters.Text(buttons_for("clone"))
    | 
