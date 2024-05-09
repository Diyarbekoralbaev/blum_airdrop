import sqlite3 as sql
from hash import custom_hash
from datetime import timezone, timedelta, datetime
import os
import dotenv

dotenv.load_dotenv()


def current_time():
    return datetime.now(timezone.utc)

def parse_time(time):
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f%z")

class Database:
    def __init__(self):
        self.conn = sql.connect('data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            tg_id INTEGER,
            tg_name TEXT,
            tg_username TEXT,
            balance INTEGER DEFAULT 0,
            user_hash TEXT,
            LAST_TIME_MINE TEXT,
            NEXT_TIME_MINE TEXT
        )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals(
                id INTEGER PRIMARY KEY,
                inviter_id INTEGER,
                invited_id INTEGER,
                FOREIGN KEY(inviter_id) REFERENCES users(tg_id)
            )
        """)

        self.conn.autocommit = True

        
    def tg_add_user(self, tg_id, tg_name, tg_username):
        user_hash = custom_hash(tg_id)
        time = current_time()
        self.cursor.execute("INSERT INTO users(tg_id, tg_name, tg_username, user_hash, LAST_TIME_MINE, NEXT_TIME_MINE) VALUES(?, ?, ?, ?, ?, ?)", (tg_id, tg_name, tg_username, user_hash, time, time))
        data = self.cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return data
    
    def regenerate_hash(self, tg_id):
        user_hash = custom_hash(tg_id)
        self.cursor.execute("UPDATE users SET user_hash = ? WHERE tg_id = ?", (user_hash, tg_id))
        data = self.cursor.execute("SELECT user_hash FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return data
    
    def tg_get_user(self, tg_id):
        data = self.cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return data
    
    def tg_get_user_hash(self, tg_id):
        data = self.cursor.execute("SELECT user_hash FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return data
    
    def tg_update_balance(self, tg_id, balance):
        current_balance = self.cursor.execute("SELECT balance FROM users WHERE tg_id = ?", (tg_id,)).fetchone()[0]
        balance += current_balance
        self.cursor.execute("UPDATE users SET balance = ? WHERE tg_id = ?", (balance, tg_id))
        data = self.cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return data
    
    def get_mining_reward(self, usr_hash):
        user = self.cursor.execute("SELECT * FROM users WHERE user_hash = ?", (usr_hash,)).fetchone()
        if parse_time(user[7]) < current_time():
            balance = user[4] + 50000
            last_time = current_time()
            next_time = current_time() + timedelta(hours=6)
            self.cursor.execute("UPDATE users SET balance = ?, LAST_TIME_MINE = ?, NEXT_TIME_MINE = ? WHERE user_hash = ?", (balance, last_time, next_time, usr_hash))
            data = self.cursor.execute("SELECT * FROM users WHERE user_hash = ?", (usr_hash,)).fetchone()
            return data
        return False
    
    def get_user_with_hash(self, usr_hash):
        data = self.cursor.execute("SELECT * FROM users WHERE user_hash = ?", (usr_hash,)).fetchone()
        return data
    
    def get_all_users(self):
        data = self.cursor.execute("SELECT * FROM users").fetchall()
        return data
    
    def users_count(self):
        data = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()
        return data[0]
    
    def add_referral(self, inviter_id, invited_id):
        self.cursor.execute("INSERT INTO referrals(inviter_id, invited_id) VALUES(?, ?)", (inviter_id, invited_id))
        data = self.cursor.execute("SELECT * FROM referrals WHERE inviter_id = ? AND invited_id = ?", (inviter_id, invited_id)).fetchone()
        return data
    
    def get_referrals(self, inviter_id):
        data = self.cursor.execute("SELECT * FROM referrals WHERE inviter_id = ?", (inviter_id,)).fetchall()
        return data
    
    def close(self):     
        self.conn.close()