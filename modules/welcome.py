from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS

class WelcomeModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def auto_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue
            # استفاده از متغیرها: #اسم, #ساعت, #تاریخ
            welcome_text = self.db.get_welcome(update.effective_chat.id) or "به گروه خوش آمدید"
            # جایگزینی متغیرها
            welcome_text = welcome_text.replace("#اسم", f"[{member.first_name}](tg://user?id={member.id})")
            await update.message.reply_text(welcome_text, parse_mode="Markdown")
    
    async def set_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        text = " ".join(context.args) if context.args else None
        if not text:
            await update.message.reply_text(f"{SYMBOLS['warning']}متن خوش‌آمد را وارد کنید!")
            return
        self.db.set_welcome(update.effective_chat.id, text)
        await update.message.reply_text(f"{SYMBOLS['success']}متن خوش‌آمد تنظیم شد!")
    
    async def show_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = self.db.get_welcome(update.effective_chat.id)
        if welcome:
            await update.message.reply_text(f"{SYMBOLS['info']}متن خوش‌آمد فعلی:\n{welcome}")
        else:
            await update.message.reply_text(f"{SYMBOLS['info']}متن خوش‌آمدی تنظیم نشده است.")
    
    async def is_admin(self, update):
        # بررسی دسترسی
        pass
