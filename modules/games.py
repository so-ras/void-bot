from telegram import Update
from telegram.ext import ContextTypes

class GamesModule:
    async def dice_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🎲")
    
    async def dart_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🎯")
    
    async def football_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="⚽")
    
    async def basketball_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🏀")
    
    async def bowling_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🎳")
    
    async def slot_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🎰")
    
    async def aim_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_dice(emoji="🎯")
