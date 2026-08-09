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
            await update.message.reply_text(f"{SYMBOLS['error']}شما دسترسی به این دستور ندارید!")
            return
        
        if not context.args:
            await update.message.reply_text(f"{SYMBOLS['warning']}مدت زمان را وارد کنید. مثال: charge 30")
            return
        
        try:
            duration = int(context.args[0])
            expiry = datetime.now() + timedelta(days=duration)
            self.db.set_expiry(update.effective_chat.id, expiry)
            await update.message.reply_text(f"{SYMBOLS['success']}گروه به مدت {duration} روز شارژ شد!")
        except ValueError:
            await update.message.reply_text(f"{SYMBOLS['error']}عدد معتبر وارد کنید!")
    
    async def group_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text(f"{SYMBOLS['error']}شما دسترسی به این دستور ندارید!")
            return
        
        expiry = self.db.get_expiry(update.effective_chat.id)
        if expiry:
            remaining = (expiry - datetime.now()).days
            await update.message.reply_text(f"{SYMBOLS['info']}زمان باقیمانده: {remaining} روز")
        else:
            await update.message.reply_text(f"{SYMBOLS['info']}این گروه شارژ نشده است.")
