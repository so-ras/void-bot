import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class VoidBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.register_handlers()
    
    def register_handlers(self):
        @self.app.add_handler(CommandHandler("start"))
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("🤖 ربات void فعال است!")
        
        @self.app.add_handler(CommandHandler("settings"))
        async def settings_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
            keyboard = [
                [InlineKeyboardButton("⚙️ مدیریت", callback_data="menu_manage")],
                [InlineKeyboardButton("🔒 قفل‌ها", callback_data="menu_locks")],
                [InlineKeyboardButton("📊 آمار", callback_data="menu_stats")],
                [InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🛠 پنل مدیریت گروه", reply_markup=reply_markup)
        
        @self.app.add_handler(CallbackQueryHandler())
        async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(f"✅ شما روی {query.data} کلیک کردید!")
    
    def run(self):
        logger.info("🚀 ربات void راه‌اندازی شد!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = VoidBot()
    bot.run()
