import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import filters
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
from utils.helpers import is_admin

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class VoidBot:
    def __init__(self):
        self.db = DBManager()
        self.redis = RedisManager()
        self.updater = Updater(BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
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
        self.dispatcher.add_handler(CommandHandler("ban", self.admin.ban_user))
        self.dispatcher.add_handler(CommandHandler("sic", self.admin.sic_user))
        self.dispatcher.add_handler(CommandHandler("mute", self.admin.mute_user))
        self.dispatcher.add_handler(CommandHandler("unmute", self.admin.unmute_user))
        self.dispatcher.add_handler(CommandHandler("warn", self.admin.warn_user))
        self.dispatcher.add_handler(CommandHandler("unwarn", self.admin.unwarn_user))
        self.dispatcher.add_handler(CommandHandler("purge", self.admin.purge_user))
        self.dispatcher.add_handler(CommandHandler("del", self.admin.delete_message))
        self.dispatcher.add_handler(CommandHandler("pin", self.admin.pin_message))
        self.dispatcher.add_handler(CommandHandler("unpin", self.admin.unpin_message))
        
        # ارتقا و عزل
        self.dispatcher.add_handler(CommandHandler("promote", self.promote.promote_user))
        self.dispatcher.add_handler(CommandHandler("demote", self.promote.demote_user))
        self.dispatcher.add_handler(CommandHandler("vip", self.promote.set_vip))
        self.dispatcher.add_handler(CommandHandler("unvip", self.promote.unset_vip))
        self.dispatcher.add_handler(CommandHandler("promoteowner", self.promote.promote_owner))
        
        # قفل‌ها
        self.dispatcher.add_handler(CommandHandler("lock", self.locks.lock_group))
        self.dispatcher.add_handler(CommandHandler("unlock", self.locks.unlock_group))
        self.dispatcher.add_handler(CommandHandler("locklink", self.locks.lock_link))
        self.dispatcher.add_handler(CommandHandler("unlocklink", self.locks.unlock_link))
        self.dispatcher.add_handler(CommandHandler("lockphoto", self.locks.lock_photo))
        self.dispatcher.add_handler(CommandHandler("unlockphoto", self.locks.unlock_photo))
        self.dispatcher.add_handler(CommandHandler("lockvideo", self.locks.lock_video))
        self.dispatcher.add_handler(CommandHandler("unlockvideo", self.locks.unlock_video))
        self.dispatcher.add_handler(CommandHandler("lockfile", self.locks.lock_file))
        self.dispatcher.add_handler(CommandHandler("unlockfile", self.locks.unlock_file))
        self.dispatcher.add_handler(CommandHandler("locksticker", self.locks.lock_sticker))
        self.dispatcher.add_handler(CommandHandler("unlocksticker", self.locks.unlock_sticker))
        self.dispatcher.add_handler(CommandHandler("lockvoice", self.locks.lock_voice))
        self.dispatcher.add_handler(CommandHandler("unlockvoice", self.locks.unlock_voice))
        self.dispatcher.add_handler(CommandHandler("lockmusic", self.locks.lock_music))
        self.dispatcher.add_handler(CommandHandler("unlockmusic", self.locks.unlock_music))
        self.dispatcher.add_handler(CommandHandler("lockgif", self.locks.lock_gif))
        self.dispatcher.add_handler(CommandHandler("unlockgif", self.locks.unlock_gif))
        self.dispatcher.add_handler(CommandHandler("lockspam", self.locks.lock_spam))
        self.dispatcher.add_handler(CommandHandler("unlockspam", self.locks.unlock_spam))
        self.dispatcher.add_handler(CommandHandler("locklocation", self.locks.lock_location))
        self.dispatcher.add_handler(CommandHandler("unlocklocation", self.locks.unlock_location))
        self.dispatcher.add_handler(CommandHandler("lockcontact", self.locks.lock_contact))
        self.dispatcher.add_handler(CommandHandler("unlockcontact", self.locks.unlock_contact))
        self.dispatcher.add_handler(CommandHandler("lockvideonote", self.locks.lock_video_note))
        self.dispatcher.add_handler(CommandHandler("unlockvideonote", self.locks.unlock_video_note))
        
        # فیلترها
        self.dispatcher.add_handler(CommandHandler("filter", self.filters.add_filter))
        self.dispatcher.add_handler(CommandHandler("unfilter", self.filters.remove_filter))
        self.dispatcher.add_handler(CommandHandler("filters", self.filters.list_filters))
        
        # خوش‌آمد
        self.dispatcher.add_handler(CommandHandler("setwelcome", self.welcome.set_welcome))
        self.dispatcher.add_handler(CommandHandler("welcome", self.welcome.show_welcome))
        self.dispatcher.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome.auto_welcome))
        
        # آمار
        self.dispatcher.add_handler(CommandHandler("stats", self.stats.show_stats))
        self.dispatcher.add_handler(CommandHandler("info", self.stats.user_info))
        
        # بازی‌ها
        self.dispatcher.add_handler(CommandHandler("dice", self.games.dice_game))
        self.dispatcher.add_handler(CommandHandler("dart", self.games.dart_game))
        self.dispatcher.add_handler(CommandHandler("football", self.games.football_game))
        self.dispatcher.add_handler(CommandHandler("basketball", self.games.basketball_game))
        self.dispatcher.add_handler(CommandHandler("bowling", self.games.bowling_game))
        self.dispatcher.add_handler(CommandHandler("slot", self.games.slot_game))
        self.dispatcher.add_handler(CommandHandler("aim", self.games.aim_game))
        
        # تبدیل
        self.dispatcher.add_handler(CommandHandler("tosticker", self.convert.to_sticker))
        self.dispatcher.add_handler(CommandHandler("togif", self.convert.to_gif))
        
        # نقل قول و تاریخ
        self.dispatcher.add_handler(CommandHandler("quote", self.quotes.quote_message))
        self.dispatcher.add_handler(CommandHandler("date", self.date.show_date))
        
        # امتیاز
        self.dispatcher.add_handler(CommandHandler("score", self.rewards.show_score))
        self.dispatcher.add_handler(CommandHandler("enablescore", self.rewards.enable_score))
        self.dispatcher.add_handler(CommandHandler("disablescore", self.rewards.disable_score))
        
        # اشتراک
        self.dispatcher.add_handler(CommandHandler("charge", self.subscription.charge_group))
        self.dispatcher.add_handler(CommandHandler("status", self.subscription.group_status))
        
        # لیست‌ها
        self.dispatcher.add_handler(CommandHandler("ownerslist", self.admin.list_owners))
        self.dispatcher.add_handler(CommandHandler("adminslist", self.admin.list_admins))
        self.dispatcher.add_handler(CommandHandler("vipslist", self.admin.list_vips))
        self.dispatcher.add_handler(CommandHandler("muteslist", self.admin.list_mutes))
        self.dispatcher.add_handler(CommandHandler("banslist", self.admin.list_bans))
        
        # پنل شیشه‌ای
        self.dispatcher.add_handler(CommandHandler("settings", self.settings_panel))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_handler))
        
        # هندلر پیام‌ها
        self.dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    def settings_panel(self, update: Update, context: CallbackContext):
        if not is_admin(update, context):
            return
        keyboard = [
            [InlineKeyboardButton("👥 مدیریت", callback_data="menu_manage")],
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="menu_locks")],
            [InlineKeyboardButton("📊 آمار", callback_data="menu_stats")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🛠 پنل مدیریت گروه", reply_markup=reply_markup)
    
    def button_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        data = query.data
        
        if data == "menu_manage":
            self.promote.manage_panel(query)
        elif data == "menu_locks":
            self.locks.locks_panel(query)
        elif data == "menu_stats":
            self.stats.stats_panel(query)
        elif data == "menu_settings":
            self.welcome.settings_panel(query)
    
    def message_handler(self, update: Update, context: CallbackContext):
        if self.locks.is_group_locked(update):
            update.message.delete()
            return
        if self.filters.check_filters(update.message.text):
            update.message.delete()
            update.message.reply_text("⚠️ پیام شما حاوی کلمه ممنوعه بود!")
    
    def run(self):
        logger.info("🚀 ربات void راه‌اندازی شد!")
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    bot = VoidBot()
    bot.run()
