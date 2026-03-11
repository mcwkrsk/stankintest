import os
from telebot import TeleBot
import Settings
from database import users_dao
from utils import normalize_group

ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'НОСОВИЦКИЙЛУЧШИЙПРЕПОДАВАТЕЛЬ')

async def handle_secret_code(message):
    if message.text != ADMIN_SECRET:
        return
    user_id = str(message.from_user.id)
    Settings.user_states[user_id] = 'waiting_for_group_for_elder'
    await Settings.bot.reply_to(message, "Какая группа?")

async def process_set_elder_group(message):
    user_id = str(message.from_user.id)
    group = normalize_group(message.text)
    role = await users_dao.get_user_role(user_id)
    if role in ('admin', 'elder'):
        await Settings.bot.reply_to(message, "У вас уже есть роль администратора или старосты.")
    else:
        await users_dao.set_user_role(user_id, 'elder', group)
        await Settings.bot.reply_to(message, f"Теперь вы староста группы {group}!")
    Settings.user_states[user_id] = None

async def handle_photo_commands(message):
    text_lower = message.text.lower()
    if text_lower == 'хохол':
        path = 'images/pig.webp'
    elif text_lower == 'лучший':
        path = 'images/best.jfif'
    else:
        return
    try:
        with open(path, 'rb') as photo:
            await Settings.bot.send_photo(message.chat.id, photo)
    except FileNotFoundError:
        await Settings.bot.reply_to(message, "Извините, изображение не найдено.")
    except Exception as e:
        await Settings.bot.reply_to(message, f"Ошибка: {e}")

def register_handlers(bot: TeleBot):
    bot.message_handler(func=lambda msg: msg.text == ADMIN_SECRET)(handle_secret_code)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'waiting_for_group_for_elder')(process_set_elder_group)
    bot.message_handler(func=lambda msg: msg.text.lower() in ('хохол', 'лучший'))(handle_photo_commands)