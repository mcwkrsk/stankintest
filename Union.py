import Settings

async def _union_(message):
    """Обработчик раздела Профком (заглушка)"""
    await Settings.bot.send_message(
        message.chat.id,
        'К сожалению, данная способность пока не работает. Приносим извинения'
    )