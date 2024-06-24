import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        with self.connection:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    block INTEGER DEFAULT 0
                )
            ''')

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return bool(len(result.fetchall()))

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def set_block(self, user_id, block):
        with self.connection:
            return self.cursor.execute("UPDATE users SET block = ? WHERE user_id = ?", (block, user_id,))

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id, block FROM users").fetchall()

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    def user_count(self):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM users")
            result = self.cursor.fetchone()
            return result[0]



