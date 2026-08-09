class LoggerModule:
    def __init__(self, db):
        self.db = db
    
    async def log(self, chat_id, action, target_id, actor_id, details=None):
        """ثبت لاگ در دیتابیس"""
        try:
            self.db.log_action(chat_id, action, target_id, actor_id, details)
        except Exception as e:
            print(f"خطا در ثبت لاگ: {e}")
