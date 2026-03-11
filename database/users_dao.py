import aiosqlite
import logging
from . import DB_PATH

async def get_user_role(user_id: str) -> str:
    """Возвращает роль пользователя ('student', 'elder', 'admin') или 'student', если пользователь не найден"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT role FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'student'

async def get_user_role_and_group(user_id: str) -> tuple[str, str | None]:
    """Возвращает (role, group) пользователя. Если пользователя нет, role='student', group=None"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT role, group_of FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return 'student', None

async def set_user_role(user_id: str, role: str, group: str = None):
    """Устанавливает роль и группу пользователя (если group указана)"""
    async with aiosqlite.connect(DB_PATH) as db:
        if group is not None:
            await db.execute('''
                INSERT INTO users (id, role, group_of) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET role=excluded.role, group_of=excluded.group_of
            ''', (user_id, role, group))
        else:
            await db.execute('''
                INSERT INTO users (id, role) VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET role=excluded.role
            ''', (user_id, role))
        await db.commit()

async def is_subscribed(user_id: str) -> bool:
    """Проверяет, подписан ли пользователь на рекламу"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT subscribed FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])

async def toggle_subscription(user_id: str):
    """Переключает подписку пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем текущее состояние
        async with db.execute('SELECT subscribed FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            current = row[0] if row else 0
        new_value = 1 if not current else 0
        await db.execute('''
            INSERT INTO users (id, subscribed) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET subscribed=excluded.subscribed
        ''', (user_id, new_value))
        await db.commit()

async def get_subscribed_users() -> list[str]:
    """Возвращает список user_id всех подписанных пользователей"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id FROM users WHERE subscribed = 1') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]