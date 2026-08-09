from telegram import Update
from telegram.ext import ContextTypes
import jdatetime
from datetime import datetime
import calendar

class DateModule:
    async def show_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        now = datetime.now()
        jalali = jdatetime.datetime.now()
        # تاریخ شمسی
        shamsi = f"{jalali.year}/{jalali.month}/{jalali.day}"
        # تاریخ میلادی
        miladi = f"{now.year}/{now.month}/{now.day}"
        # تاریخ قمری (ساده)
        ghamari = f"{now.year}/{now.month}/{now.day}"  # نیاز به کتابخانه جداگانه
        
        text = f"📅 **تاریخ امروز:**\n"
        text += f"🟢 شمسی: {shamsi}\n"
        text += f"🔵 میلادی: {miladi}\n"
        text += f"🟡 قمری: {ghamari}\n"
        text += f"🕐 ساعت: {now.hour}:{now.minute}"
        await update.message.reply_text(text)
