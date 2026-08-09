from telegram import Update
from telegram.ext import ContextTypes
from config import SYMBOLS

class LocksModule:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
    
    async def lock_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        self.db.set_lock(update.effective_chat.id, "group", True)
        await update.message.reply_text(f"{SYMBOLS['lock']}گروه قفل شد!")
    
    async def unlock_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        self.db.set_lock(update.effective_chat.id, "group", False)
        await update.message.reply_text(f"{SYMBOLS['unlock']}گروه باز شد!")
    
    async def lock_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        self.db.set_lock(update.effective_chat.id, "link", True)
        await update.message.reply_text(f"{SYMBOLS['lock']}لینک قفل شد!")
    
    async def unlock_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.is_admin(update):
            return
        self.db.set_lock(update.effective_chat.id, "link", False)
        await update.message.reply_text(f"{SYMBOLS['unlock']}لینک باز شد!")
    
    # توابع مشابه برای photo, video, file, sticker, voice, music, gif, spam, location, contact, video_note
    # به دلیل طولانی شدن، فقط نام توابع رو می‌نویسم:
    # lock_photo, unlock_photo, lock_video, unlock_video, lock_file, unlock_file, lock_sticker, unlock_sticker
    # lock_voice, unlock_voice, lock_music, unlock_music, lock_gif, unlock_gif, lock_spam, unlock_spam
    # lock_location, unlock_location, lock_contact, unlock_contact, lock_video_note, unlock_video_note
    
    async def is_group_locked(self, update):
        return self.db.get_lock(update.effective_chat.id, "group")
    
    async def is_admin(self, update):
        # بررسی دسترسی
        pass
