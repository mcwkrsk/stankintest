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

# Устанавливаем и импортируем зависимости
logging = install_and_import('logging')
random = install_and_import('random')
asyncio = install_and_import('asyncio')
aiosqlite = install_and_import('aiosqlite')
telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot import types

import Settings

async def is_subscribed(user_id: str):
    async with aiosqlite.connect('database/subscriptions.db') as db:
        async with db.execute("SELECT subscribed FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] == 1 if row else False

async def subscribe_user(user_id: str):
    async with aiosqlite.connect('database/subscriptions.db') as db:
        await db.execute("INSERT OR REPLACE INTO subscriptions (user_id, subscribed) VALUES (?, 1)", (user_id,))
        await db.commit()

async def unsubscribe_user(user_id: str):
    async with aiosqlite.connect('database/subscriptions.db') as db:
        await db.execute("INSERT OR REPLACE INTO subscriptions (user_id, subscribed) VALUES (?, 0)", (user_id,))
        await db.commit()

async def toggle_subscription(user_id: str, message: types.Message):
    is_subscribed_var = await is_subscribed(user_id)
    if is_subscribed_var:
        await unsubscribe_user(user_id)
        await Settings.bot.reply_to(message, "Вы отписались от автоматической рекламы.")
    else:
        await subscribe_user(user_id)
        await Settings.bot.reply_to(message, "Вы подписаны на автоматическую рекламу!")

async def send_advertisements():
    while True:
        await asyncio.sleep(7200)  # Подождать 2 час
        async with aiosqlite.connect('database/subscriptions.db') as db:
            async with db.execute("SELECT user_id FROM subscriptions WHERE subscribed = 1") as cursor:
                rows = await cursor.fetchall()

                for row in rows:
                    user_id = row[0]
                    z = random.randint(0, 1000) # реализация разных рекламных блоков. Указан номер ЕД
                    if z > 666:
                        ad_text = "🌟 Специально для вас! 🌟\n\n" \
                                  "Не упустите возможность! " \
                                  "Начните свое обучение уже сегодня!\n\n" \
                                  "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34\n" \
                                  "🌐 Посетите наш сайт: www.example.com"
                    elif z >= 333 and z <= 666:
                        ad_text = "🚀 Второй модуль приближается! 🚀\n\n" \
                                  "А вы не готовы?" \
                                  "🌐 Посетите наш сайт: www.example.com\n" \
                                  "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34"
                    elif z < 333:
                        ad_text = "🤓 Новые уроки и информация по безопасности в сфере труда! 🤓\n\n" \
                                  "🌐 Посетите наш сайт: www.example.com\n" \
                                  "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34"
                    try:
                        await Settings.bot.send_message(user_id, ad_text)
                    except Exception as e:
                        logging.error(f"Не удалось отправить рекламу пользователю {user_id}: {e}")