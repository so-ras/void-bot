from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS, OWNER_ID
from datetime import datetime, timedelta

class SubscriptionModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def charge_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("شما دسترسی به این دستور ندارید!")
            return
        
        if not context.args:
            await update.message.reply_text("مدت زمان را وارد کنید. مثال: charge 30")
            return
        
        try:
            duration = int(context.args[0])
            expiry = datetime.now() + timedelta(days=duration)
            await update.message.reply_text(f"گروه به مدت {duration} روز شارژ شد!")
        except ValueError:
            await update.message.reply_text("عدد معتبر وارد کنید!")
    
    async def group_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("شما دسترسی به این دستور ندارید!")
            return
        
        await update.message.reply_text("وضعیت گروه: فعال")
