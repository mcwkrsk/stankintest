import aiosqlite
from . import DB_PATH

async def get_homework(group: str, date: str) -> list[tuple[str, str]]:
    """Возвращает список (subject, description) для заданной группы и даты"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT subject, description FROM homework WHERE group_of = ? AND date_of = ?',
            (group, date)
        ) as cursor:
            return await cursor.fetchall()

async def add_homework(group: str, date: str, subject: str, description: str) -> bool:
    """Добавляет новую запись ДЗ. Возвращает True при успехе"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                'INSERT INTO homework (group_of, date_of, subject, description) VALUES (?, ?, ?, ?)',
                (group, date, subject, description)
            )
            await db.commit()
            return True
    except Exception:
        return False

async def update_homework(group: str, date: str, subject: str, new_description: str) -> bool:
    """Обновляет описание ДЗ по ключу (group, date, subject). Возвращает True при успехе"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                'UPDATE homework SET description = ? WHERE group_of = ? AND date_of = ? AND subject = ?',
                (new_description, group, date, subject)
            )
            await db.commit()
            return True
    except Exception:
        return False

async def delete_homework(group: str, date: str, subject: str) -> bool:
    """Удаляет запись ДЗ. Возвращает True при успехе"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                'DELETE FROM homework WHERE group_of = ? AND date_of = ? AND subject = ?',
                (group, date, subject)
            )
            await db.commit()
            return True
    except Exception:
        return False

async def homework_exists(group: str, date: str, subject: str) -> bool:
    """Проверяет, существует ли запись с такими ключами"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT 1 FROM homework WHERE group_of = ? AND date_of = ? AND subject = ?',
            (group, date, subject)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None