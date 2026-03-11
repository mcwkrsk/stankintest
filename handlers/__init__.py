from telebot import TeleBot
from . import common, homework, club, union, admin

def register_handlers(bot: TeleBot):
    """Регистрация всех обработчиков сообщений"""
    common.register_handlers(bot)
    homework.register_handlers(bot)
    club.register_handlers(bot)
    union.register_handlers(bot)
    admin.register_handlers(bot)