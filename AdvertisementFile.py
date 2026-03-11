import asyncio
import logging
import random
from database import users_dao
import Settings

async def is_subscribed(user_id: str) -> bool:
    """Проверка подписки пользователя"""
    return await users_dao.is_subscribed(user_id)

async def toggle_subscription(user_id: str, message):
    """Переключение подписки и отправка уведомления"""
    await users_dao.toggle_subscription(user_id)
    subscribed = await is_subscribed(user_id)
    if subscribed:
        await Settings.bot.reply_to(message, "Вы подписаны на автоматическую рекламу!")
    else:
        await Settings.bot.reply_to(message, "Вы отписались от автоматической рекламы.")

def generate_ad() -> str:
    """Генерация случайного рекламного текста"""
    z = random.randint(0, 1000)
    if z > 666:
        return ("🌟 Специально для вас! 🌟\n\n"
                "Не упустите возможность! "
                "Начните свое обучение уже сегодня!\n\n"
                "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34\n"
                "🌐 Посетите наш сайт: www.example.com")
    elif z >= 333:
        return ("🚀 Второй модуль приближается! 🚀\n\n"
                "А вы не готовы?\n"
                "🌐 Посетите наш сайт: www.example.com\n"
                "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34")
    else:
        return ("🤓 Новые уроки и информация по безопасности в сфере труда! 🤓\n\n"
                "🌐 Посетите наш сайт: www.example.com\n"
                "📞 Свяжитесь с нами по номеру: +7 (499) 973-38-34")

async def send_advertisements():
    """Периодическая рассылка рекламы подписчикам (каждые 2 часа)"""
    while True:
        await asyncio.sleep(7200)
        try:
            user_ids = await users_dao.get_subscribed_users()
            if not user_ids:
                continue

            semaphore = asyncio.Semaphore(10)  # ограничение одновременных отправок

            async def send_to_user(uid):
                async with semaphore:
                    try:
                        ad_text = generate_ad()
                        await Settings.bot.send_message(uid, ad_text)
                    except Exception as e:
                        logging.error(f"Не удалось отправить рекламу пользователю {uid}: {e}")

            tasks = [send_to_user(uid) for uid in user_ids]
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Ошибка в рассылке рекламы: {e}")