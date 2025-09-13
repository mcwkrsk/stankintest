import os
import sys

def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        return __import__(import_name)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")
        return __import__(import_name)

aiosqlite = install_and_import('aiosqlite')
telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot import types

import Settings
async def search_in_database(value_1: str, value_2: str):
    try:
        async with aiosqlite.connect('database/datahomework.db') as db:
            async with db.execute("SELECT * FROM homework WHERE group_of = ? AND date_of = ?", (value_1, value_2)) as cursor:
                rows = await cursor.fetchall()
        return rows
    except aiosqlite.OperationalError as e:
        if "no such table" in str(e):
            # Таблица не существует, нужно инициализировать базу
            await init_database()
            return []
        else:
            raise


async def insert_into_database(group_of: str, date_of: str, homework: str, subject: str, user_id: str,message: str):
    async with aiosqlite.connect('database/datahomework.db') as db:
        await db.execute(
            "INSERT INTO homework (group_of, date_of, description, subject) VALUES (?, ?, ?, ?)",
            (group_of, date_of, homework, subject)
        )
        await db.commit()
        await Settings.bot.reply_to(message, "🥰 Данные успешно добавлены! 🥰")  # Предполагается, что user_id - это id чата

async def delete_row_into_database(group: str, date: str, subject: str, message: types.Message):
    async with aiosqlite.connect('database/datahomework.db') as db:
        await db.execute('DELETE FROM homework WHERE group_of = ? AND subject = ? AND date_of = ?',(group, subject, date))
        await db.commit()


async def refactor_homework(message: types.Message, button_text: str):
    group = Settings.user_refactor_states[message.from_user.id][0]
    date = Settings.user_refactor_states[message.from_user.id][1]
    subject = Settings.user_refactor_states[message.from_user.id][2]
    homework = Settings.user_refactor_states[message.from_user.id][3]

    if button_text == 'Изменить Д/З':
        await delete_row_into_database(group, subject, date)
        await insert_into_database(group, date, homework, subject, message.from_user.id, message)

    elif button_text == 'Удалить Д/З':
        await delete_row_into_database(group, subject, date, message)

    Settings.user_refactor_states[message.from_user.id] = {}
    await _homework_(message)


async def _homework_(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_id = str(message.from_user.id)

    async with aiosqlite.connect('database/datausers.db') as db:
        async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
            user_role_row = await cursor.fetchone()
            # Добавлена явная проверка на None и преобразование в строку
            user_role = str(user_role_row[0]) if user_role_row and user_role_row[0] is not None else "student"

            item1 = types.KeyboardButton('Проверить свою роль✅')
            item2 = types.KeyboardButton('Вывести ДЗ🚀')
            item3 = types.KeyboardButton('Назад')

            # Добавление дополнительных кнопок для администраторов или старост
            if user_role in ['elder', 'admin']:  # Теперь user_role гарантированно строка
                item4 = types.KeyboardButton('Редактировать дз')
                item5 = types.KeyboardButton('Добавить дз📝')
                markup.add(item1, item2, item4, item5, item3)
            else:
                markup.add(item1, item2, item3)

            await Settings.bot.send_message(message.chat.id, 'Выбери интересующий тебя раздел', reply_markup=markup)