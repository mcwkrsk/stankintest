import os
import sys
import re
from datetime import datetime

def install_and_import(package, import_name=None):
    """Устанавливает пакет при необходимости и импортирует его"""
    if import_name is None:
        import_name = package
    try:
        return __import__(import_name)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")
        return __import__(import_name)

def is_valid_date(date_str: str) -> bool:
    """Проверяет, соответствует ли строка формату ДД.ММ.ГГГГ и является ли датой"""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, date_str):
        return False
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def normalize_group(group: str) -> str:
    """Приводит название группы к верхнему регистру и убирает лишние пробелы"""
    return group.strip().upper()

def create_main_keyboard():
    """Создаёт основную клавиатуру главного меню (с автоустановкой telebot при необходимости)"""
    telebot = install_and_import('pyTelegramBotAPI', 'telebot')
    from telebot import types
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Д/З'),
        types.KeyboardButton('Профком'),
        types.KeyboardButton('ВУЦ'),
        types.KeyboardButton('Подписаться/отписаться от рекламы💜'),
        types.KeyboardButton('Инструкция по использованию🤓')
    )
    return markup