import sqlite3

class Database: 
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
    def init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                username TEXT NOT NULL UNIQUE, 
                password TEXT NOT NULL,
                first_name TEXT NOT NULL, 
                last_name TEXT NOT NULL, 
                bio TEXT,
                profile_picture BLOB,
                wallpaper_picture BLOB
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                user_id INTEGER NOT NULL,
                caption TEXT NOT NULL,
                media_count INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_media(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                post_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                media_blob BLOB NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                liked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS marks(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                marked_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()
    def close(self):
        self.conn.close()
