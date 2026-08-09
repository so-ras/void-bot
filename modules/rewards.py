from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS

class RewardsModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def show_score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        score = self.db.get_score(user.id, update.effective_chat.id)
        await update.message.reply_text(f"{SYMBOLS['info']}امتیاز شما: {score}")
    
    async def enable_score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # فعال‌سازی سیستم امتیاز (فقط مالک اصلی)
        pass
    
    async def disable_score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # غیرفعال‌سازی سیستم امتیاز (فقط مالک اصلی)
        pass
