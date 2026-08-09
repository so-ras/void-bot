import psycopg2
from datetime import datetime
from config import DATABASE_URL

class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                today_messages INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                add_count INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id BIGINT PRIMARY KEY,
                welcome_message TEXT DEFAULT 'به گروه خوش آمدید',
                rules TEXT DEFAULT '',
                locks JSONB DEFAULT '{}',
                filters TEXT[] DEFAULT '{}',
                is_active BOOLEAN DEFAULT TRUE,
                expiry_date TIMESTAMP DEFAULT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                chat_id BIGINT,
                user_id BIGINT,
                is_owner BOOLEAN DEFAULT FALSE,
                is_vip BOOLEAN DEFAULT FALSE,
                vip_expiry TIMESTAMP DEFAULT NULL,
                permissions JSONB DEFAULT '{}',
                title TEXT DEFAULT '',
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                action TEXT,
                target_id BIGINT,
                actor_id BIGINT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        cursor.close()
    
    def add_user(self, user_id, first_name, username):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, first_name, username, add_count)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                username = EXCLUDED.username,
                add_count = users.add_count + 1
        """, (user_id, first_name, username))
        self.conn.commit()
        cursor.close()
    
    def log_action(self, chat_id, action, target_id, actor_id, details=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO logs (chat_id, action, target_id, actor_id, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (chat_id, action, target_id, actor_id, details))
        self.conn.commit()
        cursor.close()
    
    def set_lock(self, chat_id, lock_type, value):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE group_settings SET locks = jsonb_set(
                COALESCE(locks, '{}'::jsonb),
                %s,
                %s::jsonb
            ) WHERE chat_id = %s
        """, (f"{{{lock_type}}}", str(value).lower(), chat_id))
        self.conn.commit()
        cursor.close()
    
    def get_lock(self, chat_id, lock_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT locks->%s FROM group_settings WHERE chat_id = %s", (lock_type, chat_id))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and result[0] is not None else False
    
    def add_filter(self, chat_id, word):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE group_settings SET filters = array_append(
                COALESCE(filters, '{}'), %s
            ) WHERE chat_id = %s
        """, (word, chat_id))
        self.conn.commit()
        cursor.close()
    
    def remove_filter(self, chat_id, word):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE group_settings SET filters = array_remove(
                COALESCE(filters, '{}'), %s
            ) WHERE chat_id = %s
        """, (word, chat_id))
        self.conn.commit()
        cursor.close()
    
    def get_filters(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT filters FROM group_settings WHERE chat_id = %s", (chat_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and result[0] else []
    
    def get_welcome(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT welcome_message FROM group_settings WHERE chat_id = %s", (chat_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def set_welcome(self, chat_id, message):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO group_settings (chat_id, welcome_message)
            VALUES (%s, %s)
            ON CONFLICT (chat_id) DO UPDATE SET welcome_message = EXCLUDED.welcome_message
        """, (chat_id, message))
        self.conn.commit()
        cursor.close()
    
    def get_today_stats(self, chat_id):
        # دریافت آمار امروز (ساده شده)
        return {"bans": 0, "mutes": 0, "warns": 0, "purges": 0, "locks": 0, "adds": 0, "chats": 0}
    
    def is_admin(self, chat_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE chat_id = %s AND user_id = %s", (chat_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def is_owner(self, chat_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE chat_id = %s AND user_id = %s AND is_owner = TRUE", (chat_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
