from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS

class StatsModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        # دریافت آمار از دیتابیس
        members = update.effective_chat.get_member_count()
        bans = self.db.get_today_bans(update.effective_chat.id)
        mutes = self.db.get_today_mutes(update.effective_chat.id)
        warns = self.db.get_today_warns(update.effective_chat.id)
        purges = self.db.get_today_purges(update.effective_chat.id)
        locks = self.db.get_today_locks(update.effective_chat.id)
        adds = self.db.get_today_adds(update.effective_chat.id)
        chats = self.db.get_today_chats(update.effective_chat.id)
        
        text = f"{SYMBOLS['stats']}آمار روزانه گروه:\n"
        text += f"👥 اعضا: {members}\n"
        text += f"➕ ادد: {adds}\n"
        text += f"💬 پیام‌ها: {chats}\n"
        text += f"✖ بن: {bans}\n"
        text += f"⊘ سکوت: {mutes}\n"
        text += f"⚠ اخطار: {warns}\n"
        text += f"🗑 پاک کردن: {purges}\n"
        text += f"☒ قفل: {locks}\n"
        await update.message.reply_text(text)
    
    async def user_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text(f"{SYMBOLS['warning']}روی پیام کاربر ریپلای کنید!")
            return
        user = update.message.reply_to_message.from_user
        # دریافت اطلاعات از دیتابیس
        info = self.db.get_user_info(user.id, update.effective_chat.id)
        text = f"{SYMBOLS['info']}اطلاعات کاربر:\n"
        text += f"نام: {user.first_name}\n"
        text += f"یوزرنیم: @{user.username or 'ندارد'}\n"
        text += f"آیدی: {user.id}\n"
        text += f"تاریخ عضویت: {info['join_date']}\n"
        text += f"پیام‌های امروز: {info['today_messages']}\n"
        text += f"کل پیام‌ها: {info['total_messages']}\n"
        text += f"دفعات ادد: {info['add_count']}\n"
        await update.message.reply_text(text)
    
    async def is_admin(self, update):
        # بررسی دسترسی
        pass
