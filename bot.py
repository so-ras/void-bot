import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import BOT_TOKEN, OWNER_ID, API_ID, API_HASH
from datetime import datetime, timedelta
import jdatetime

logging.basicConfig(level=logging.INFO)

app = Client("void_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# ========== ذخیره‌سازی موقت ==========
user_warns = {}
user_mutes = {}
user_vips = {}
group_locks = {}
group_filters = {}
group_welcome = {}
group_admins = {}
group_owners = {}

# ========== توابع کمکی ==========
def is_admin(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    return group_admins.get(chat_id, {}).get(str(user_id), False)

def is_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    return group_owners.get(chat_id) == user_id

async def get_user_info(user):
    text = f"📋 اطلاعات کاربر:\n"
    text += f"نام: {user.first_name or 'ندارد'}\n"
    text += f"یوزرنیم: @{user.username or 'ندارد'}\n"
    text += f"آیدی: {user.id}\n"
    text += f"آیدی عددی: `{user.id}`"
    return text

def get_welcome_message(chat_id):
    return group_welcome.get(str(chat_id), "به گروه {group_name} خوش آمدید")

def is_group_locked(chat_id):
    return group_locks.get(str(chat_id), False)

def get_filters(chat_id):
    return group_filters.get(str(chat_id), [])

# ========== دستورات مدیریت اعضا ==========

@app.on_message(filters.command(["بن", "ban"]) & filters.group)
async def ban_user(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    try:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} بن شد! 🚫")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@app.on_message(filters.command(["سیک", "sic"]) & filters.group)
async def sic_user(client, message):
    await ban_user(client, message)

@app.on_message(filters.command(["سکوت", "mute"]) & filters.group)
async def mute_user(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    try:
        duration = 1
        if message.command and len(message.command) > 1:
            try:
                duration = int(message.command[1])
            except:
                pass
        await client.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            permissions={"can_send_messages": False},
            until_date=datetime.now() + timedelta(hours=duration)
        )
        user_mutes[str(message.reply_to_message.from_user.id)] = datetime.now() + timedelta(hours=duration)
        await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} به مدت {duration} ساعت سکوت شد! 🔇")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@app.on_message(filters.command(["سکوت ۱", "mute1"]) & filters.group)
async def mute_1h(client, message):
    message.command = ["سکوت", "1"]
    await mute_user(client, message)

@app.on_message(filters.command(["اخطار", "warn"]) & filters.group)
async def warn_user(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user_id = str(message.reply_to_message.from_user.id)
    warns = user_warns.get(user_id, 0) + 1
    user_warns[user_id] = warns
    if warns >= 3:
        try:
            await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} پس از ۳ اخطار بن شد!")
            user_warns[user_id] = 0
        except:
            pass
    else:
        await message.reply_text(f"⚠️ اخطار {warns} از ۳ برای {message.reply_to_message.from_user.first_name}")

# ========== دستورات ارتقا و عزل ==========

@app.on_message(filters.command(["ارتقا به مدیریت", "promote"]) & filters.group)
async def promote_user(client, message):
    if not is_owner(message.chat.id, message.from_user.id) and message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط مالک گروه می‌تواند این کار را انجام دهد!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    if chat_id not in group_admins:
        group_admins[chat_id] = {}
    group_admins[chat_id][str(user.id)] = True
    await message.reply_text(f"✅ کاربر {user.first_name} به مدیریت ارتقا یافت! 👑")

@app.on_message(filters.command(["عزل", "demote"]) & filters.group)
async def demote_user(client, message):
    if not is_owner(message.chat.id, message.from_user.id) and message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط مالک گروه می‌تواند این کار را انجام دهد!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    if chat_id in group_admins:
        group_admins[chat_id].pop(str(user.id), None)
    await message.reply_text(f"✅ کاربر {user.first_name} از مدیریت عزل شد! ⬇️")

@app.on_message(filters.command(["ویژه", "vip"]) & filters.group)
async def set_vip(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    duration = 1
    if message.command and len(message.command) > 1:
        try:
            duration = int(message.command[1])
        except:
            pass
    user_vips[str(message.reply_to_message.from_user.id)] = datetime.now() + timedelta(hours=duration)
    await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.first_name} به مدت {duration} ساعت ویژه شد! ✨")

@app.on_message(filters.command(["ویژه ۱", "vip1"]) & filters.group)
async def set_vip_1h(client, message):
    message.command = ["ویژه", "1"]
    await set_vip(client, message)

@app.on_message(filters.command(["ارتقا به مالک", "promoteowner"]) & filters.group)
async def promote_owner(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط سازنده ربات می‌تواند این کار را انجام دهد!")
        return
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user = message.reply_to_message.from_user
    group_owners[message.chat.id] = user.id
    await message.reply_text(f"✅ کاربر {user.first_name} به مالکیت گروه ارتقا یافت! 👑")

# ========== دستورات قفل ==========

@app.on_message(filters.command(["قفل گروه", "lock"]) & filters.group)
async def lock_group(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    group_locks[str(message.chat.id)] = True
    await message.reply_text("🔒 گروه قفل شد! (فقط چت بسته شد)")

@app.on_message(filters.command(["باز کردن گروه", "unlock"]) & filters.group)
async def unlock_group(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    group_locks[str(message.chat.id)] = False
    await message.reply_text("🔓 گروه باز شد!")

@app.on_message(filters.command(["قفل لینک", "locklink"]) & filters.group)
async def lock_link(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    await message.reply_text("🔗 لینک قفل شد!")

@app.on_message(filters.command(["باز کردن لینک", "unlocklink"]) & filters.group)
async def unlock_link(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    await message.reply_text("🔗 لینک باز شد!")

# ========== دستورات فیلتر ==========

@app.on_message(filters.command(["فیلتر کلمه", "filter"]) & filters.group)
async def add_filter(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    chat_id = str(message.chat.id)
    if chat_id not in group_filters:
        group_filters[chat_id] = []
    if message.reply_to_message and message.reply_to_message.text:
        word = message.reply_to_message.text.strip()
    elif message.command and len(message.command) > 1:
        word = " ".join(message.command[1:])
    else:
        await message.reply_text("⚠️ یک کلمه وارد کنید یا روی کلمه ریپلای کنید!")
        return
    if word not in group_filters[chat_id]:
        group_filters[chat_id].append(word)
    await message.reply_text(f"✅ کلمه '{word}' فیلتر شد! 🚫")

@app.on_message(filters.command(["حذف فیلتر", "unfilter"]) & filters.group)
async def remove_filter(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    chat_id = str(message.chat.id)
    if message.command and len(message.command) > 1:
        word = " ".join(message.command[1:])
        if chat_id in group_filters and word in group_filters[chat_id]:
            group_filters[chat_id].remove(word)
        await message.reply_text(f"✅ کلمه '{word}' از فیلتر حذف شد!")

@app.on_message(filters.command(["لیست فیلترها", "filters"]) & filters.group)
async def list_filters(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    chat_id = str(message.chat.id)
    if chat_id in group_filters and group_filters[chat_id]:
        text = "📋 لیست کلمات فیلتر شده:\n"
        for i, word in enumerate(group_filters[chat_id], 1):
            text += f"{i}. {word}\n"
        await message.reply_text(text)
    else:
        await message.reply_text("📋 هیچ کلمه‌ای فیلتر نشده است.")

# ========== دستورات خوش‌آمد ==========

@app.on_message(filters.command(["تنظیم خوش‌آمد", "setwelcome"]) & filters.group)
async def set_welcome(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    if message.command and len(message.command) > 1:
        text = " ".join(message.command[1:])
        group_welcome[str(message.chat.id)] = text
        await message.reply_text(f"✅ متن خوش‌آمد تنظیم شد!")
    else:
        await message.reply_text("⚠️ متن خوش‌آمد را وارد کنید!")

@app.on_message(filters.command(["مشاهده خوش‌آمد", "welcome"]) & filters.group)
async def show_welcome(client, message):
    chat_id = str(message.chat.id)
    welcome = group_welcome.get(chat_id, "به گروه {group_name} خوش آمدید")
    await message.reply_text(f"📋 متن خوش‌آمد فعلی:\n{welcome}")

@app.on_message(filters.new_chat_members & filters.group)
async def auto_welcome(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            continue
        chat_id = str(message.chat.id)
        welcome_text = group_welcome.get(chat_id, "به گروه {group_name} خوش آمدید")
        welcome_text = welcome_text.replace("{group_name}", message.chat.title)
        welcome_text = welcome_text.replace("#اسم", f"[{member.first_name}](tg://user?id={member.id})")
        welcome_text = welcome_text.replace("#ساعت", datetime.now().strftime("%H:%M"))
        welcome_text = welcome_text.replace("#تاریخ", jdatetime.datetime.now().strftime("%Y/%m/%d"))
        await message.reply_text(welcome_text, parse_mode="Markdown")

# ========== دستورات آمار و اطلاعات ==========

@app.on_message(filters.command(["امار", "stats"]) & filters.group)
async def show_stats(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    try:
        members = await client.get_chat_members_count(message.chat.id)
        text = f"📊 **آمار گروه:**\n"
        text += f"👥 اعضا: {members}\n"
        text += f"👑 مالک: {message.chat.id}\n"
        text += f"📅 تاریخ: {jdatetime.datetime.now().strftime('%Y/%m/%d')}"
        await message.reply_text(text)
    except:
        await message.reply_text("📊 آمار گروه در دسترس نیست.")

@app.on_message(filters.command(["اطلاعات", "info"]) & filters.group)
async def user_info(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام کاربر ریپلای کنید!")
        return
    user = message.reply_to_message.from_user
    text = await get_user_info(user)
    await message.reply_text(text)

# ========== دستورات لیست‌ها ==========

@app.on_message(filters.command(["لیست مدیران", "adminslist"]) & filters.group)
async def list_admins(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    chat_id = str(message.chat.id)
    admins = group_admins.get(chat_id, {})
    if not admins:
        await message.reply_text("📋 هیچ مدیری در این گروه وجود ندارد.")
        return
    text = "📋 **لیست مدیران:**\n"
    for i, admin_id in enumerate(admins.keys(), 1):
        try:
            user = await client.get_users(int(admin_id))
            text += f"{i}. {user.first_name} (ایدی: {admin_id})\n"
        except:
            text += f"{i}. ایدی: {admin_id}\n"
    await message.reply_text(text)

# ========== دستورات بازی‌ها ==========

@app.on_message(filters.command(["تاس", "dice"]))
async def dice_game(client, message):
    await message.reply_dice(emoji="🎲")

@app.on_message(filters.command(["دارت", "dart"]))
async def dart_game(client, message):
    await message.reply_dice(emoji="🎯")

@app.on_message(filters.command(["فوتبال", "football"]))
async def football_game(client, message):
    await message.reply_dice(emoji="⚽")

@app.on_message(filters.command(["بسکتبال", "basketball"]))
async def basketball_game(client, message):
    await message.reply_dice(emoji="🏀")

@app.on_message(filters.command(["بولینگ", "bowling"]))
async def bowling_game(client, message):
    await message.reply_dice(emoji="🎳")

@app.on_message(filters.command(["اسلات", "slot"]))
async def slot_game(client, message):
    await message.reply_dice(emoji="🎰")

@app.on_message(filters.command(["تیراندازی", "aim"]))
async def aim_game(client, message):
    await message.reply_dice(emoji="🎯")

# ========== دستورات تبدیل ==========

@app.on_message(filters.command(["به استیکر", "tosticker"]))
async def to_sticker(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی عکس/گیف ریپلای کنید!")
        return
    if message.reply_to_message.photo:
        await message.reply_text("🎨 تبدیل به استیکر (آماده نیست)")
    else:
        await message.reply_text("⚠️ لطفاً روی عکس ریپلای کنید!")

@app.on_message(filters.command(["به گیف", "togif"]))
async def to_gif(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی عکس/استیکر ریپلای کنید!")
        return
    await message.reply_text("🎬 تبدیل به گیف (آماده نیست)")

# ========== دستورات نقل قول و تاریخ ==========

@app.on_message(filters.command(["نقل قول", "quote"]) & filters.group)
async def quote_message(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ روی پیام مورد نظر ریپلای کنید!")
        return
    msg = message.reply_to_message
    text = f"📝 **نقل قول از {msg.from_user.first_name}**:\n{msg.text}"
    await message.reply_text(text)

@app.on_message(filters.command(["تاریخ", "date"]))
async def show_date(client, message):
    now = datetime.now()
    jalali = jdatetime.datetime.now()
    text = f"📅 **تاریخ امروز:**\n"
    text += f"🟢 شمسی: {jalali.year}/{jalali.month}/{jalali.day}\n"
    text += f"🔵 میلادی: {now.year}/{now.month}/{now.day}\n"
    text += f"🕐 ساعت: {now.hour}:{now.minute:02d}"
    await message.reply_text(text)

# ========== دستورات امتیاز ==========

@app.on_message(filters.command(["امتیاز", "score"]))
async def show_score(client, message):
    await message.reply_text("⭐ امتیاز شما: 0")

@app.on_message(filters.command(["فعال کردن امتیاز", "enablescore"]))
async def enable_score(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط سازنده ربات می‌تواند این کار را انجام دهد!")
        return
    await message.reply_text("✅ سیستم امتیاز فعال شد!")

@app.on_message(filters.command(["غیرفعال کردن امتیاز", "disablescore"]))
async def disable_score(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط سازنده ربات می‌تواند این کار را انجام دهد!")
        return
    await message.reply_text("❌ سیستم امتیاز غیرفعال شد!")

# ========== دستورات اشتراک ==========

@app.on_message(filters.command(["شارژ", "charge"]))
async def charge_group(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط سازنده ربات می‌تواند این کار را انجام دهد!")
        return
    if message.command and len(message.command) > 1:
        duration = message.command[1]
        await message.reply_text(f"✅ گروه به مدت {duration} روز شارژ شد!")
    else:
        await message.reply_text("⚠️ مدت زمان را وارد کنید. مثال: شارژ 30")

@app.on_message(filters.command(["وضعیت", "status"]))
async def group_status(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ فقط سازنده ربات می‌تواند این کار را انجام دهد!")
        return
    await message.reply_text("📋 وضعیت گروه: فعال ✅")

# ========== پنل شیشه‌ای ==========

@app.on_message(filters.command(["تنظیمات", "settings"]) & filters.group)
async def settings_panel(client, message):
    if not is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("⛔ شما دسترسی به این دستور ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت", callback_data="menu_manage")],
        [InlineKeyboardButton("🔒 قفل‌ها", callback_data="menu_locks")],
        [InlineKeyboardButton("📊 آمار", callback_data="menu_stats")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🛠 **پنل مدیریت گروه**", reply_markup=reply_markup)

@app.on_callback_query()
async def button_handler(client, callback_query: CallbackQuery):
    await callback_query.answer()
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    if not is_admin(chat_id, user_id):
        await callback_query.message.edit_text("⛔ شما دسترسی به این بخش ندارید!")
        return
    
    if data == "menu_manage":
        text = "👥 **بخش مدیریت**\n\n"
        text += "دستورات:\n"
        text += "• بن / سیک\n"
        text += "• سکوت / سکوت ۱\n"
        text += "• اخطار\n"
        text += "• ارتقا به مدیریت / عزل\n"
        text += "• ویژه / ویژه ۱\n"
        text += "• ارتقا به مالک"
        await callback_query.message.edit_text(text)
    elif data == "menu_locks":
        text = "🔒 **بخش قفل‌ها**\n\n"
        text += "• قفل گروه / باز کردن گروه\n"
        text += "• قفل لینک / باز کردن لینک"
        await callback_query.message.edit_text(text)
    elif data == "menu_stats":
        text = "📊 **بخش آمار**\n\n"
        text += "دستورات:\n"
        text += "• امار\n"
        text += "• اطلاعات (با ریپلای)"
        await callback_query.message.edit_text(text)
    elif data == "menu_settings":
        text = "⚙️ **بخش تنظیمات**\n\n"
        text += "دستورات:\n"
        text += "• تنظیم خوش‌آمد\n"
        text += "• فیلتر کلمه / حذف فیلتر / لیست فیلترها\n"
        text += "• شارژ / وضعیت"
        await callback_query.message.edit_text(text)

@app.on_message(filters.text & filters.group)
async def message_handler(client, message):
    chat_id = str(message.chat.id)
    if group_locks.get(chat_id, False):
        await message.delete()
        await message.reply_text("🔒 گروه قفل است!")
        return
    for word in get_filters(chat_id):
        if word in message.text.lower():
            await message.delete()
            await message.reply_text(f"⚠️ پیام شما حاوی کلمه فیلتر شده '{word}' بود!")
            return

print("🤖 ربات void با موفقیت راه‌اندازی شد!")
app.run()
