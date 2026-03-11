import os
import sys
from utils import install_and_import

# Устанавливаем и импортируем python-dotenv
dotenv = install_and_import('python-dotenv', 'dotenv')
load_dotenv = dotenv.load_dotenv

load_dotenv()

# Импортируем асинхронного бота
telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot.async_telebot import AsyncTeleBot

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен не найден! Проверьте файл .env")

bot = AsyncTeleBot(TOKEN)

# Состояния пользователей для многошаговых диалогов
user_states = {}           # основное состояние
user_refactor_states = {}  # данные для подтверждения изменения/удаления ДЗ