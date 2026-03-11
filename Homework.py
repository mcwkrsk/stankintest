import logging
from telebot import types
import Settings
from database import homework_dao, users_dao
from utils import is_valid_date, normalize_group

async def search_in_database(group: str, date: str):
    """Поиск ДЗ по группе и дате"""
    try:
        return await homework_dao.get_homework(group, date)
    except Exception as e:
        logging.error(f"Ошибка при поиске ДЗ: {e}")
        return []

async def insert_into_database(group: str, date: str, subject: str, description: str):
    """Добавление ДЗ"""
    try:
        await homework_dao.add_homework(group, date, subject, description)
        return True
    except Exception as e:
        logging.error(f"Ошибка при добавлении ДЗ: {e}")
        return False

async def delete_from_database(group: str, date: str, subject: str):
    """Удаление ДЗ"""
    try:
        await homework_dao.delete_homework(group, date, subject)
        return True
    except Exception as e:
        logging.error(f"Ошибка при удалении ДЗ: {e}")
        return False

async def update_in_database(group: str, date: str, subject: str, new_description: str):
    """Обновление ДЗ"""
    try:
        await homework_dao.update_homework(group, date, subject, new_description)
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении ДЗ: {e}")
        return False

async def homework_exists(group: str, date: str, subject: str) -> bool:
    """Проверка существования ДЗ"""
    try:
        return await homework_dao.homework_exists(group, date, subject)
    except Exception as e:
        logging.error(f"Ошибка при проверке существования ДЗ: {e}")
        return False

async def _homework_(message):
    """Меню раздела ДЗ"""
    from handlers.common import show_main_menu  # чтобы избежать циклических импортов
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_id = str(message.from_user.id)
    user_role = await users_dao.get_user_role(user_id)

    item1 = types.KeyboardButton('Проверить свою роль✅')
    item2 = types.KeyboardButton('Вывести ДЗ🚀')
    item3 = types.KeyboardButton('Назад')

    if user_role in ['elder', 'admin']:
        item4 = types.KeyboardButton('Редактировать дз')
        item5 = types.KeyboardButton('Добавить дз📝')
        markup.add(item1, item2, item4, item5, item3)
    else:
        markup.add(item1, item2, item3)

    await Settings.bot.send_message(message.chat.id, 'Выбери интересующий тебя раздел', reply_markup=markup)

async def refactor_homework(message, button_text):
    """Обработка подтверждения изменения/удаления ДЗ"""
    user_id = message.from_user.id
    if user_id not in Settings.user_refactor_states:
        await Settings.bot.reply_to(message, "Ошибка: данные не найдены. Начните заново.")
        return

    group, date, subject, description = Settings.user_refactor_states[user_id]

    if button_text == 'Изменить Д/З':
        await delete_from_database(group, date, subject)
        success = await insert_into_database(group, date, subject, description)
        if success:
            await Settings.bot.reply_to(message, "✅ ДЗ успешно изменено!")
        else:
            await Settings.bot.reply_to(message, "❌ Ошибка при изменении ДЗ.")

    elif button_text == 'Удалить Д/З':
        success = await delete_from_database(group, date, subject)
        if success:
            await Settings.bot.reply_to(message, "✅ ДЗ удалено.")
        else:
            await Settings.bot.reply_to(message, "❌ Ошибка при удалении ДЗ.")

    # Очистка состояний
    Settings.user_refactor_states.pop(user_id, None)
    await _homework_(message)