from config import OWNER_ID
from database.db_manager import DBManager

db = DBManager()

async def is_admin(update, context):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return True
    return db.is_admin(update.effective_chat.id, user_id)

async def is_owner(update, context):
    user_id = update.effective_user.id
    return db.is_owner(update.effective_chat.id, user_id)

def get_group_id(update):
    return update.effective_chat.id

def get_user_id(update):
    return update.effective_user.id
