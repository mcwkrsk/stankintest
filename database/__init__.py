import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'bot.db')

async def init_db():
    """Создаёт все необходимые таблицы и индексы, если они ещё не существуют"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                group_of TEXT,
                role TEXT DEFAULT 'student',
                subscribed INTEGER DEFAULT 0
            )
        ''')
        # Таблица домашних заданий
        await db.execute('''
            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_of TEXT NOT NULL,
                date_of TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        # Индексы для ускорения поиска
        await db.execute('CREATE INDEX IF NOT EXISTS idx_homework_group_date ON homework(group_of, date_of)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        await db.commit()