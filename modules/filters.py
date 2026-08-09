from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS

class FiltersModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def add_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        if context.args:
            word = " ".join(context.args)
            self.db.add_filter(update.effective_chat.id, word)
            await update.message.reply_text(f"{SYMBOLS['filter']}کلمه '{word}' فیلتر شد!")
            return
        if update.message.reply_to_message and update.message.reply_to_message.text:
            word = update.message.reply_to_message.text.strip()
            self.db.add_filter(update.effective_chat.id, word)
            await update.message.reply_text(f"{SYMBOLS['filter']}کلمه '{word}' فیلتر شد!")
            return
        await update.message.reply_text(f"{SYMBOLS['warning']}یک کلمه وارد کنید!")
    
    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        if context.args:
            word = " ".join(context.args)
            self.db.remove_filter(update.effective_chat.id, word)
            await update.message.reply_text(f"{SYMBOLS['success']}کلمه '{word}' از فیلتر حذف شد!")
    
    async def list_filters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        filters = self.db.get_filters(update.effective_chat.id)
        if not filters:
            await update.message.reply_text(f"{SYMBOLS['info']}هیچ کلمه‌ای فیلتر نشده است.")
            return
        text = f"{SYMBOLS['filter']}لیست فیلترها:\n"
        for i, word in enumerate(filters, 1):
            text += f"{i}. {word}\n"
        await update.message.reply_text(text)
    
    async def check_filters(self, text):
        # بررسی متن
        pass
    
    async def is_admin(self, update):
        # بررسی دسترسی
        pass
