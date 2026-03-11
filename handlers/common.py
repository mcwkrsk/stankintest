from telebot import types, TeleBot
import Settings
from database import users_dao
from utils import create_main_keyboard
import AdvertisementFile

async def show_main_menu(message):
    """Показывает главное меню"""
    markup = create_main_keyboard()
    await Settings.bot.send_message(
        message.chat.id,
        f'Привет, {message.from_user.first_name}! Выбери интересующий тебя раздел бота!',
        reply_markup=markup
    )

async def cmd_start(message):
    await show_main_menu(message)

async def cmd_help(message):
    help_text = (
        "🤖 Бот-помощник студента\n\n"
        "Команды:\n"
        "/start - главное меню\n"
        "/cancel - отменить текущее действие\n"
        "/help - это сообщение\n\n"
        "Основные разделы:\n"
        "• Д/З – просмотр и добавление домашки\n"
        "• Профком – информация профкома\n"
        "• ВУЦ – расписание ВУЦ\n"
        "• Подписка на рекламу\n"
        "• Инструкция – подробное описание"
    )
    await Settings.bot.reply_to(message, help_text)

async def cmd_cancel(message):
    user_id = str(message.from_user.id)
    if user_id in Settings.user_states:
        Settings.user_states[user_id] = None
        # Очистить временные данные с суффиксами
        keys_to_delete = [k for k in Settings.user_states if k.endswith(f'_{user_id}')]
        for k in keys_to_delete:
            del Settings.user_states[k]
    await Settings.bot.reply_to(message, "Действие отменено. Возврат в главное меню.")
    await show_main_menu(message)

async def check_role(message):
    user_id = str(message.from_user.id)
    role, group = await users_dao.get_user_role_and_group(user_id)
    if role == 'admin':
        text = f"ВАША РОЛЬ - АДМИНИСТРАТОР\nВАША ГРУППА - {group if group else 'Не указана'}"
    elif role == 'elder':
        text = f"ВАША РОЛЬ - СТАРОСТА\nВАША ГРУППА - {group if group else 'Не указана'}"
    else:
        text = 'ВЫ ОБЫЧНЫЙ СТУДЕНТ'
    await Settings.bot.reply_to(message, text)

async def instruction(message):
    await Settings.bot.reply_to(
        message,
        "Хочешь научиться пользоваться нашим ботом-помощником?\n"
        "Тогда мы с радостью расскажем как именно его нужно использовать\n\n"
        "Бот позволяет:\n"
        "- Просматривать домашние задания по группам и датам\n"
        "- Добавлять/редактировать/удалять ДЗ (для старост и админов)\n"
        "- Узнавать расписание ВУЦ на неделю\n"
        "- Подписываться на полезную рекламу\n\n"
        "Используй кнопки меню для навигации."
    )

async def handle_subscription(message):
    """Обработчик кнопки подписки на рекламу"""
    user_id = str(message.from_user.id)
    await AdvertisementFile.toggle_subscription(user_id, message)

def register_handlers(bot: TeleBot):
    bot.message_handler(commands=['start'])(cmd_start)
    bot.message_handler(commands=['help'])(cmd_help)
    bot.message_handler(commands=['cancel'])(cmd_cancel)
    bot.message_handler(func=lambda msg: msg.text == 'Проверить свою роль✅')(check_role)
    bot.message_handler(func=lambda msg: msg.text == 'Инструкция по использованию🤓')(instruction)
    bot.message_handler(func=lambda msg: msg.text == 'Назад')(show_main_menu)
    bot.message_handler(func=lambda msg: msg.text == 'Подписаться/отписаться от рекламы💜')(handle_subscription)  # <-- добавить эту строку