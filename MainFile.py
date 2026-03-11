import os
import sys
import asyncio
import logging

# Добавляем путь к проекту для корректных импортов
sys.path.append(os.path.dirname(__file__))

from utils import install_and_import

# Устанавливаем зависимости при необходимости
logging = install_and_import('logging')
asyncio = install_and_import('asyncio')
aiosqlite = install_and_import('aiosqlite')
telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot import types

import Settings
from database import init_db
from handlers import register_handlers
import AdvertisementFile

logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация базы данных
    await init_db()
    logging.info("База данных инициализирована")

    # Регистрация обработчиков
    register_handlers(Settings.bot)

    # Запуск фоновой задачи рассылки рекламы
    asyncio.create_task(AdvertisementFile.send_advertisements())

    # Запуск бота с обработкой ошибок
    try:
        await Settings.bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка polling: {e}")
    finally:
        await Settings.bot.close_session()

if __name__ == '__main__':
    asyncio.run(main())