from telebot import types, TeleBot
import Settings
from database import homework_dao, users_dao
from utils import is_valid_date, normalize_group

async def handle_homework_menu(message):
    user_id = str(message.from_user.id)
    role = await users_dao.get_user_role(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Проверить свою роль✅'),
        types.KeyboardButton('Вывести ДЗ🚀'),
        types.KeyboardButton('Назад')
    )
    if role in ('elder', 'admin'):
        markup.add(
            types.KeyboardButton('Редактировать дз'),
            types.KeyboardButton('Добавить дз📝')
        )
    await Settings.bot.send_message(message.chat.id, 'Выбери действие в разделе Д/З', reply_markup=markup)

# ---- ПРОСМОТР ДЗ ----
async def start_get_homework(message):
    user_id = str(message.from_user.id)
    Settings.user_states[user_id] = 'get_homework_group'
    await Settings.bot.reply_to(message, "Введите группу для вывода домашнего задания:")

async def process_get_homework_group(message):
    user_id = str(message.from_user.id)
    group = normalize_group(message.text)
    Settings.user_states[f'group_{user_id}'] = group
    Settings.user_states[user_id] = 'get_homework_date'
    await Settings.bot.reply_to(message, "Теперь введите дату (ДД.ММ.ГГГГ):")

async def process_get_homework_date(message):
    user_id = str(message.from_user.id)
    date = message.text.strip()
    if not is_valid_date(date):
        await Settings.bot.reply_to(message, "Неверный формат даты. Введите ДД.ММ.ГГГГ")
        return
    group = Settings.user_states.get(f'group_{user_id}')
    if not group:
        await Settings.bot.reply_to(message, "Ошибка: группа не найдена.")
        Settings.user_states[user_id] = None
        return
    results = await homework_dao.get_homework(group, date)
    if results:
        response = f"Список домашнего задания на {date} (группа {group}):\n\n"
        for i, (subject, desc) in enumerate(results, 1):
            response += f"{i}) {subject} – {desc}\n"
    else:
        response = "Ничего не найдено."
    await Settings.bot.reply_to(message, response)
    Settings.user_states[user_id] = None
    Settings.user_states.pop(f'group_{user_id}', None)

# ---- ДОБАВЛЕНИЕ ДЗ ----
async def start_add_homework(message):
    user_id = str(message.from_user.id)
    role, group = await users_dao.get_user_role_and_group(user_id)
    if role == 'elder' and group:
        Settings.user_states[user_id] = 'add_homework_date'
        Settings.user_states[f'group_{user_id}'] = group
        await Settings.bot.reply_to(message, f"Ваша группа: {group}. Введите дату (ДД.ММ.ГГГГ):")
    elif role == 'admin':
        Settings.user_states[user_id] = 'add_homework_group'
        await Settings.bot.reply_to(message, "Введите группу для добавления ДЗ:")
    else:
        await Settings.bot.reply_to(message, "У вас нет прав для добавления ДЗ.")

async def process_add_homework_group(message):
    user_id = str(message.from_user.id)
    group = normalize_group(message.text)
    Settings.user_states[f'group_{user_id}'] = group
    Settings.user_states[user_id] = 'add_homework_date'
    await Settings.bot.reply_to(message, "Введите дату (ДД.ММ.ГГГГ):")

async def process_add_homework_date(message):
    user_id = str(message.from_user.id)
    date = message.text.strip()
    if not is_valid_date(date):
        await Settings.bot.reply_to(message, "Неверный формат даты.")
        return
    Settings.user_states[f'date_{user_id}'] = date
    Settings.user_states[user_id] = 'add_homework_subject'
    await Settings.bot.reply_to(message, "Введите название предмета:")

async def process_add_homework_subject(message):
    user_id = str(message.from_user.id)
    subject = message.text.strip()
    Settings.user_states[f'subject_{user_id}'] = subject
    Settings.user_states[user_id] = 'add_homework_description'
    await Settings.bot.reply_to(message, "Введите описание домашнего задания:")

async def process_add_homework_description(message):
    user_id = str(message.from_user.id)
    description = message.text.strip()
    group = Settings.user_states.get(f'group_{user_id}')
    date = Settings.user_states.get(f'date_{user_id}')
    subject = Settings.user_states.get(f'subject_{user_id}')

    if not all([group, date, subject]):
        await Settings.bot.reply_to(message, "Ошибка: данные не полны. Начните заново.")
        Settings.user_states[user_id] = None
        return

    exists = await homework_dao.homework_exists(group, date, subject)
    if exists:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Изменить дз', 'Не менять дз', 'Удалить дз')
        await Settings.bot.reply_to(
            message,
            'Домашнее задание уже существует. Что сделать?',
            reply_markup=markup
        )
        Settings.user_refactor_states[message.from_user.id] = (group, date, subject, description)
        Settings.user_states[user_id] = None
        for key in [f'group_{user_id}', f'date_{user_id}', f'subject_{user_id}']:
            Settings.user_states.pop(key, None)
        return

    success = await homework_dao.add_homework(group, date, subject, description)
    if success:
        await Settings.bot.reply_to(message, "🥰 Данные успешно добавлены! 🥰")
    else:
        await Settings.bot.reply_to(message, "❌ Ошибка при добавлении ДЗ.")

    Settings.user_states[user_id] = None
    for key in [f'group_{user_id}', f'date_{user_id}', f'subject_{user_id}']:
        Settings.user_states.pop(key, None)

# ---- РЕДАКТИРОВАНИЕ ДЗ ----
async def start_edit_homework(message):
    user_id = str(message.from_user.id)
    role, group = await users_dao.get_user_role_and_group(user_id)
    if role == 'elder' and group:
        Settings.user_states[user_id] = 'edit_homework_date'
        Settings.user_states[f'group_{user_id}'] = group
        await Settings.bot.reply_to(message, f"Ваша группа: {group}. Введите дату (ДД.ММ.ГГГГ):")
    elif role == 'admin':
        Settings.user_states[user_id] = 'edit_homework_group'
        await Settings.bot.reply_to(message, "Введите группу для редактирования ДЗ:")
    else:
        await Settings.bot.reply_to(message, "У вас нет прав для редактирования ДЗ.")

async def process_edit_homework_group(message):
    user_id = str(message.from_user.id)
    group = normalize_group(message.text)
    Settings.user_states[f'group_{user_id}'] = group
    Settings.user_states[user_id] = 'edit_homework_date'
    await Settings.bot.reply_to(message, "Введите дату (ДД.ММ.ГГГГ):")

async def process_edit_homework_date(message):
    user_id = str(message.from_user.id)
    date = message.text.strip()
    if not is_valid_date(date):
        await Settings.bot.reply_to(message, "Неверный формат даты.")
        return
    Settings.user_states[f'date_{user_id}'] = date
    Settings.user_states[user_id] = 'edit_homework_subject'
    await Settings.bot.reply_to(message, "Введите название предмета:")

async def process_edit_homework_subject(message):
    user_id = str(message.from_user.id)
    subject = message.text.strip()
    Settings.user_states[f'subject_{user_id}'] = subject
    Settings.user_states[user_id] = 'edit_homework_new_description'
    await Settings.bot.reply_to(message, "Введите новое описание домашнего задания:")

async def process_edit_homework_new_description(message):
    user_id = str(message.from_user.id)
    new_description = message.text.strip()
    group = Settings.user_states.get(f'group_{user_id}')
    date = Settings.user_states.get(f'date_{user_id}')
    subject = Settings.user_states.get(f'subject_{user_id}')

    if not all([group, date, subject]):
        await Settings.bot.reply_to(message, "Ошибка: данные не полны. Начните заново.")
        Settings.user_states[user_id] = None
        return

    exists = await homework_dao.homework_exists(group, date, subject)
    if not exists:
        await Settings.bot.reply_to(message, "Запись не найдена.")
        Settings.user_states[user_id] = None
        return

    success = await homework_dao.update_homework(group, date, subject, new_description)
    if success:
        await Settings.bot.reply_to(message, "✅ Домашнее задание обновлено!")
    else:
        await Settings.bot.reply_to(message, "❌ Ошибка при обновлении.")

    Settings.user_states[user_id] = None
    for key in [f'group_{user_id}', f'date_{user_id}', f'subject_{user_id}']:
        Settings.user_states.pop(key, None)

# ---- ОБРАБОТКА ПОДТВЕРЖДЕНИЯ ----
async def process_refactor_choice(message):
    user_id = message.from_user.id
    if user_id not in Settings.user_refactor_states:
        await Settings.bot.reply_to(message, "Ошибка: нет данных.")
        return
    group, date, subject, description = Settings.user_refactor_states[user_id]
    text = message.text

    if text == 'Изменить дз':
        await homework_dao.delete_homework(group, date, subject)
        success = await homework_dao.add_homework(group, date, subject, description)
        await Settings.bot.reply_to(message, "✅ ДЗ изменено!" if success else "❌ Ошибка.")
    elif text == 'Не менять дз':
        await Settings.bot.reply_to(message, "Изменений не внесено.")
    elif text == 'Удалить дз':
        success = await homework_dao.delete_homework(group, date, subject)
        await Settings.bot.reply_to(message, "✅ ДЗ удалено." if success else "❌ Ошибка.")
    else:
        return

    Settings.user_refactor_states.pop(user_id, None)
    await handle_homework_menu(message)

def register_handlers(bot: TeleBot):
    bot.message_handler(func=lambda msg: msg.text == 'Д/З')(handle_homework_menu)

    bot.message_handler(func=lambda msg: msg.text == 'Вывести ДЗ🚀')(start_get_homework)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'get_homework_group')(process_get_homework_group)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'get_homework_date')(process_get_homework_date)

    bot.message_handler(func=lambda msg: msg.text == 'Добавить дз📝')(start_add_homework)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'add_homework_group')(process_add_homework_group)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'add_homework_date')(process_add_homework_date)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'add_homework_subject')(process_add_homework_subject)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'add_homework_description')(process_add_homework_description)

    bot.message_handler(func=lambda msg: msg.text == 'Редактировать дз')(start_edit_homework)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'edit_homework_group')(process_edit_homework_group)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'edit_homework_date')(process_edit_homework_date)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'edit_homework_subject')(process_edit_homework_subject)
    bot.message_handler(func=lambda msg: Settings.user_states.get(str(msg.from_user.id)) == 'edit_homework_new_description')(process_edit_homework_new_description)

    bot.message_handler(func=lambda msg: msg.text in ('Изменить дз', 'Не менять дз', 'Удалить дз'))(process_refactor_choice)