import sqlite3
import json
from datetime import datetime
from config import DATABASE_URL

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('void_bot.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
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
                chat_id INTEGER PRIMARY KEY,
                welcome_message TEXT DEFAULT 'به گروه خوش آمدید',
                rules TEXT DEFAULT '',
                locks TEXT DEFAULT '{}',
                filters TEXT DEFAULT '[]',
                is_active INTEGER DEFAULT 1,
                expiry_date TIMESTAMP DEFAULT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER,
                user_id INTEGER,
                is_owner INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                vip_expiry TIMESTAMP DEFAULT NULL,
                permissions TEXT DEFAULT '{}',
                title TEXT DEFAULT '',
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                action TEXT,
                target_id INTEGER,
                actor_id INTEGER,
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
            VALUES (?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                first_name = excluded.first_name,
                username = excluded.username,
                add_count = add_count + 1
        """, (user_id, first_name, username))
        self.conn.commit()
        cursor.close()
    
    def log_action(self, chat_id, action, target_id, actor_id, details=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO logs (chat_id, action, target_id, actor_id, details)
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, action, target_id, actor_id, details))
        self.conn.commit()
        cursor.close()
    
    def set_lock(self, chat_id, lock_type, value):
        cursor = self.conn.cursor()
        cursor.execute("SELECT locks FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        locks = json.loads(row[0]) if row and row[0] else {}
        locks[lock_type] = value
        cursor.execute("""
            INSERT INTO group_settings (chat_id, locks)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET locks = excluded.locks
        """, (chat_id, json.dumps(locks)))
        self.conn.commit()
        cursor.close()
    
    def get_lock(self, chat_id, lock_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT locks FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        if row and row[0]:
            locks = json.loads(row[0])
            return locks.get(lock_type, False)
        return False
    
    def add_filter(self, chat_id, word):
        cursor = self.conn.cursor()
        cursor.execute("SELECT filters FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        filters = json.loads(row[0]) if row and row[0] else []
        if word not in filters:
            filters.append(word)
        cursor.execute("""
            INSERT INTO group_settings (chat_id, filters)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET filters = excluded.filters
        """, (chat_id, json.dumps(filters)))
        self.conn.commit()
        cursor.close()
    
    def remove_filter(self, chat_id, word):
        cursor = self.conn.cursor()
        cursor.execute("SELECT filters FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        if row and row[0]:
            filters = json.loads(row[0])
            if word in filters:
                filters.remove(word)
            cursor.execute("""
                INSERT INTO group_settings (chat_id, filters)
                VALUES (?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET filters = excluded.filters
            """, (chat_id, json.dumps(filters)))
            self.conn.commit()
        cursor.close()
    
    def get_filters(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT filters FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row and row[0] else []
    
    def get_welcome(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT welcome_message FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def set_welcome(self, chat_id, message):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO group_settings (chat_id, welcome_message)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET welcome_message = excluded.welcome_message
        """, (chat_id, message))
        self.conn.commit()
        cursor.close()
    
    def is_admin(self, chat_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        return cursor.fetchone() is not None
    
    def is_owner(self, chat_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE chat_id = ? AND user_id = ? AND is_owner = 1", (chat_id, user_id))
        return cursor.fetchone() is not None
    
    def get_today_stats(self, chat_id):
        return {"bans": 0, "mutes": 0, "warns": 0, "purges": 0, "locks": 0, "adds": 0, "chats": 0}
