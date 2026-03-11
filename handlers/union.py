from telebot import TeleBot
import Settings

async def union_handler(message):
    await Settings.bot.send_message(
        message.chat.id,
        'К сожалению, данная способность пока не работает. Приносим извинения'
    )

def register_handlers(bot: TeleBot):
    bot.message_handler(func=lambda msg: msg.text == 'Профком')(union_handler)