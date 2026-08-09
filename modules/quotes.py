from telegram import Update
from telegram.ext import ContextTypes

class QuotesModule:
    async def quote_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            return
        msg = update.message.reply_to_message
        text = f"📝 **نقل قول از {msg.from_user.first_name}**:\n{msg.text}"
        await update.message.reply_text(text)
