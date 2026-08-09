from telegram import Update
from telegram.ext import ContextTypes

class ConvertModule:
    async def to_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # تبدیل عکس/گیف به استیکر
        pass
    
    async def to_gif(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # تبدیل عکس/استیکر به گیف
        pass
