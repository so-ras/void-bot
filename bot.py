import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID
from modules.admin import AdminModule
from modules.promote import PromoteModule
from modules.locks import LocksModule
from modules.filters import FiltersModule
from modules.welcome import WelcomeModule
from modules.stats import StatsModule
from modules.games import GamesModule
from modules.convert import ConvertModule
from modules.quotes import QuotesModule
from modules.date import DateModule
from modules.rewards import RewardsModule
from modules.subscription import SubscriptionModule
from modules.logger import LoggerModule
from database.db_manager import DBManager
from database.redis_manager import RedisManager
from utils.helpers import is_admin, is_owner

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class VoidBot:
    def __init__(self):
        self.db = DBManager()
        self.redis = RedisManager()
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # ماژول‌ها
        self.admin = AdminModule(self.db, self.redis)
        self.promote = PromoteModule(self.db, self.redis)
        self.locks = LocksModule(self.db, self.redis)
        self.filters = FiltersModule(self.db, self.redis)
        self.welcome = WelcomeModule(self.db, self.redis)
        self.stats = StatsModule(self.db, self.redis)
        self.games = GamesModule()
        self.convert = ConvertModule()
        self.quotes = QuotesModule()
        self.date = DateModule()
        self.rewards = RewardsModule(self.db, self.redis)
        self.subscription = SubscriptionModule(self.db, self.redis)
        self.logger = LoggerModule(self.db)
        
        self.register_handlers()
    
    def register_handlers(self):
        # مدیریت اعضا
        self.app.add_handler(CommandHandler("ban", self.admin.ban_user))
        self.app.add_handler(CommandHandler("sic", self.admin.sic_user))
        self.app.add_handler(CommandHandler("mute", self.admin.mute_user))
        self.app.add_handler(CommandHandler("mute1", self.admin.mute_1h))
        self.app.add_handler(CommandHandler("unmute", self.admin.unmute_user))
        self.app.add_handler(CommandHandler("warn", self.admin.warn_user))
        self.app.add_handler(CommandHandler("unwarn", self.admin.unwarn_user))
        self.app.add_handler(CommandHandler("purge", self.admin.purge_user))
        self.app.add_handler(CommandHandler("del", self.admin.delete_message))
        self.app.add_handler(CommandHandler("pin", self.admin.pin_message))
        self.app.add_handler(CommandHandler("unpin", self.admin.unpin_message))
        
        # ارتقا و عزل
        self.app.add_handler(CommandHandler("promote", self.promote.promote_user))
        self.app.add_handler(CommandHandler("demote", self.promote.demote_user))
        self.app.add_handler(CommandHandler("vip", self.promote.set_vip))
        self.app.add_handler(CommandHandler("vip1", self.promote.set_vip_1h))
        self.app.add_handler(CommandHandler("unvip", self.promote.unset_vip))
        self.app.add_handler(CommandHandler("promoteowner", self.promote.promote_owner))
        
        # قفل‌ها
        self.app.add_handler(CommandHandler("lock", self.locks.lock_group))
        self.app.add_handler(CommandHandler("unlock", self.locks.unlock_group))
        self.app.add_handler(CommandHandler("locklink", self.locks.lock_link))
        self.app.add_handler(CommandHandler("unlocklink", self.locks.unlock_link))
        self.app.add_handler(CommandHandler("lockphoto", self.locks.lock_photo))
        self.app.add_handler(CommandHandler("unlockphoto", self.locks.unlock_photo))
        self.app.add_handler(CommandHandler("lockvideo", self.locks.lock_video))
        self.app.add_handler(CommandHandler("unlockvideo", self.locks.unlock_video))
        self.app.add_handler(CommandHandler("lockfile", self.locks.lock_file))
        self.app.add_handler(CommandHandler("unlockfile", self.locks.unlock_file))
        self.app.add_handler(CommandHandler("locksticker", self.locks.lock_sticker))
        self.app.add_handler(CommandHandler("unlocksticker", self.locks.unlock_sticker))
        self.app.add_handler(CommandHandler("lockvoice", self.locks.lock_voice))
        self.app.add_handler(CommandHandler("unlockvoice", self.locks.unlock_voice))
        self.app.add_handler(CommandHandler("lockmusic", self.locks.lock_music))
        self.app.add_handler(CommandHandler("unlockmusic", self.locks.unlock_music))
        self.app.add_handler(CommandHandler("lockgif", self.locks.lock_gif))
        self.app.add_handler(CommandHandler("unlockgif", self.locks.unlock_gif))
        self.app.add_handler(CommandHandler("lockspam", self.locks.lock_spam))
        self.app.add_handler(CommandHandler("unlockspam", self.locks.unlock_spam))
        self.app.add_handler(CommandHandler("locklocation", self.locks.lock_location))
        self.app.add_handler(CommandHandler("unlocklocation", self.locks.unlock_location))
        self.app.add_handler(CommandHandler("lockcontact", self.locks.lock_contact))
        self.app.add_handler(CommandHandler("unlockcontact", self.locks.unlock_contact))
        self.app.add_handler(CommandHandler("lockvideonote", self.locks.lock_video_note))
        self.app.add_handler(CommandHandler("unlockvideonote", self.locks.unlock_video_note))
        
        # فیلترها
        self.app.add_handler(CommandHandler("filter", self.filters.add_filter))
        self.app.add_handler(CommandHandler("unfilter", self.filters.remove_filter))
        self.app.add_handler(CommandHandler("filters", self.filters.list_filters))
        
        # خوش‌آمد
        self.app.add_handler(CommandHandler("setwelcome", self.welcome.set_welcome))
        self.app.add_handler(CommandHandler("welcome", self.welcome.show_welcome))
        self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome.auto_welcome))
        
        # آمار و اطلاعات
        self.app.add_handler(CommandHandler("stats", self.stats.show_stats))
        self.app.add_handler(CommandHandler("info", self.stats.user_info))
        
        # بازی‌ها
        self.app.add_handler(CommandHandler("dice", self.games.dice_game))
        self.app.add_handler(CommandHandler("dart", self.games.dart_game))
        self.app.add_handler(CommandHandler("football", self.games.football_game))
        self.app.add_handler(CommandHandler("basketball", self.games.basketball_game))
        self.app.add_handler(CommandHandler("bowling", self.games.bowling_game))
        self.app.add_handler(CommandHandler("slot", self.games.slot_game))
        self.app.add_handler(CommandHandler("aim", self.games.aim_game))
        
        # تبدیل
        self.app.add_handler(CommandHandler("tosticker", self.convert.to_sticker))
        self.app.add_handler(CommandHandler("togif", self.convert.to_gif))
        
        # نقل قول و تاریخ
        self.app.add_handler(CommandHandler("quote", self.quotes.quote_message))
        self.app.add_handler(CommandHandler("date", self.date.show_date))
        
        # امتیاز
        self.app.add_handler(CommandHandler("score", self.rewards.show_score))
        self.app.add_handler(CommandHandler("enablescore", self.rewards.enable_score))
        self.app.add_handler(CommandHandler("disablescore", self.rewards.disable_score))
        
        # اشتراک
        self.app.add_handler(CommandHandler("charge", self.subscription.charge_group))
        self.app.add_handler(CommandHandler("status", self.subscription.group_status))
        
        # لیست‌ها
        self.app.add_handler(CommandHandler("ownerslist", self.admin.list_owners))
        self.app.add_handler(CommandHandler("adminslist", self.admin.list_admins))
        self.app.add_handler(CommandHandler("vipslist", self.admin.list_vips))
        self.app.add_handler(CommandHandler("muteslist", self.admin.list_mutes))
        self.app.add_handler(CommandHandler("banslist", self.admin.list_bans))
        
        # پنل شیشه‌ای
        self.app.add_handler(CommandHandler("settings", self.settings_panel))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # هندلر پیام‌ها
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def settings_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await is_admin(update, context):
            return
        keyboard = [
            [InlineKeyboardButton("👥 مدیریت", callback_data="menu_manage")],
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="menu_locks")],
            [InlineKeyboardButton("📊 آمار", callback_data="menu_stats")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🛠 پنل مدیریت گروه", reply_markup=reply_markup)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "menu_manage":
            await self.promote.manage_panel(query)
        elif data == "menu_locks":
            await self.locks.locks_panel(query)
        elif data == "menu_stats":
            await self.stats.stats_panel(query)
        elif data == "menu_settings":
            await self.welcome.settings_panel(query)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await self.locks.is_group_locked(update):
            await update.message.delete()
            return
        if await self.filters.check_filters(update.message.text):
            await update.message.delete()
            await update.message.reply_text("⚠️ پیام شما حاوی کلمه ممنوعه بود!")
    
    def run(self):
        logger.info("🚀 ربات void راه‌اندازی شد!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = VoidBot()
    bot.run()
