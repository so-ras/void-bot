import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import BOT_TOKEN, OWNER_ID, API_ID, API_HASH

logging.basicConfig(level=logging.INFO)

app = Client("void_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("🤖 ربات void فعال است!")

@app.on_message(filters.command("settings") & filters.group)
async def settings(client, message):
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت", callback_data="menu_manage")],
        [InlineKeyboardButton("🔒 قفل‌ها", callback_data="menu_locks")],
        [InlineKeyboardButton("📊 آمار", callback_data="menu_stats")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🛠 پنل مدیریت گروه", reply_markup=reply_markup)

@app.on_callback_query()
async def button_handler(client, callback_query: CallbackQuery):
    await callback_query.answer()
    data = callback_query.data
    
    if data == "menu_manage":
        await callback_query.message.edit_text("👥 بخش مدیریت")
    elif data == "menu_locks":
        await callback_query.message.edit_text("🔒 بخش قفل‌ها")
    elif data == "menu_stats":
        await callback_query.message.edit_text("📊 بخش آمار")
    elif data == "menu_settings":
        await callback_query.message.edit_text("⚙️ بخش تنظیمات")
    else:
        await callback_query.message.edit_text(f"شما روی {data} کلیک کردید!")

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    try:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} بن شد!")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    try:
        await client.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            permissions={"can_send_messages": False}
        )
        await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} سکوت شد!")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    try:
        await client.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            permissions={"can_send_messages": True}
        )
        await message.reply_text(f"✅ سکوت کاربر {message.reply_to_message.from_user.first_name} برداشته شد!")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@app.on_message(filters.command("warn") & filters.group)
async def warn_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    await message.reply_text(f"⚠️ اخطار به {message.reply_to_message.from_user.first_name} داده شد!")

@app.on_message(filters.command("purge") & filters.group)
async def purge_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    await message.reply_text(f"🗑 پیام‌های {message.reply_to_message.from_user.first_name} پاک شد!")

@app.on_message(filters.command("info") & filters.group)
async def user_info(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user = message.reply_to_message.from_user
    text = f"📋 اطلاعات کاربر:\n"
    text += f"نام: {user.first_name}\n"
    text += f"یوزرنیم: @{user.username or 'ندارد'}\n"
    text += f"آیدی: {user.id}"
    await message.reply_text(text)

@app.on_message(filters.command("dice"))
async def dice_game(client, message):
    await message.reply_dice(emoji="🎲")

@app.on_message(filters.command("dart"))
async def dart_game(client, message):
    await message.reply_dice(emoji="🎯")

@app.on_message(filters.command("football"))
async def football_game(client, message):
    await message.reply_dice(emoji="⚽")

@app.on_message(filters.command("basketball"))
async def basketball_game(client, message):
    await message.reply_dice(emoji="🏀")

@app.on_message(filters.command("bowling"))
async def bowling_game(client, message):
    await message.reply_dice(emoji="🎳")

@app.on_message(filters.command("slot"))
async def slot_game(client, message):
    await message.reply_dice(emoji="🎰")

@app.on_message(filters.command("aim"))
async def aim_game(client, message):
    await message.reply_dice(emoji="🎯")

@app.on_message(filters.command("date"))
async def show_date(client, message):
    from datetime import datetime
    import jdatetime
    now = datetime.now()
    jalali = jdatetime.datetime.now()
    text = f"📅 تاریخ امروز:\n"
    text += f"🟢 شمسی: {jalali.year}/{jalali.month}/{jalali.day}\n"
    text += f"🔵 میلادی: {now.year}/{now.month}/{now.day}\n"
    text += f"🕐 ساعت: {now.hour}:{now.minute}"
    await message.reply_text(text)

@app.on_message(filters.command("quote") & filters.group)
async def quote_message(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام مورد نظر ریپلای کنید!")
        return
    msg = message.reply_to_message
    text = f"📝 نقل قول از {msg.from_user.first_name}:\n{msg.text}"
    await message.reply_text(text)

@app.on_message(filters.command("score"))
async def show_score(client, message):
    await message.reply_text("⭐ امتیاز شما: 0")

print("🤖 ربات void روشن شد!")
app.run()
