from telebot import TeleBot
import Settings
import vuc_data  # вместо vuc_schedule
import datetime

async def club_handler(message):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    week_events = vuc_data.get_events_for_week(monday)

    if not week_events:
        await Settings.bot.send_message(
            message.chat.id,
            f"📅 На неделе от {monday.strftime('%d.%m.%Y')} занятий в ВУЦе нет."
        )
        return

    ru_weekdays = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    lines = []
    for date, events in sorted(week_events.items()):
        day_str = f"{date.strftime('%d.%m.%Y')} ({ru_weekdays[date.weekday()]})"
        group_lines = []
        for group, subjects in events:
            group_lines.append(f"  {group}: {', '.join(subjects)}")
        lines.append(day_str + "\n" + "\n".join(group_lines))

    header = f"📅 Расписание ВУЦа на неделю от {monday.strftime('%d.%m.%Y')}:\n\n"
    full_text = header + "\n\n".join(lines)

    # Разбиваем длинные сообщения
    if len(full_text) > 4096:
        for i in range(0, len(lines), 3):
            part = header + "\n\n".join(lines[i:i+3])
            await Settings.bot.send_message(message.chat.id, part)
    else:
        await Settings.bot.send_message(message.chat.id, full_text)

def register_handlers(bot: TeleBot):
    bot.message_handler(func=lambda msg: msg.text == 'ВУЦ')(club_handler)