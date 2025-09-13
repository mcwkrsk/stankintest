# # # # # # # # # #-Z
# RELEASE 0.0.1a # #Z от 15.11.2024
# # # # # # # # # #-Z
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

# Устанавливаем все необходимые зависимости
logging = install_and_import('logging')
asyncio = install_and_import('asyncio')
aiosqlite = install_and_import('aiosqlite')
aiohttp = install_and_import('aiohttp')  # Добавляем aiohttp
telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot import types  # Добавляем импорт types

# Теперь импортируем остальные модули
import Settings # настройки бота
import Homework # отдельный файл для подбота ДЗ
import Union # отдельный файл для подбота Профсоюза
import Club # отдельный файл для подбота Клуба Станкина
import AdvertisementFile # файл рекламы

logging.basicConfig(level=logging.INFO) # Настройка логирования

@Settings.bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    _item1_ = types.KeyboardButton('Д/З')
    _item2_ = types.KeyboardButton('Профком')
    _item3_ = types.KeyboardButton('Клуб')
    _item4_ = types.KeyboardButton('Подписаться/отписаться от рекламы💜')  # Обновленная кнопка
    _item5_ = types.KeyboardButton('Инструкция по использованию🤓')

    markup.add(_item1_, _item2_, _item3_, _item4_, _item5_)
    await Settings.bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Выбери интересующий тебя раздел бота!',reply_markup=markup)

@Settings.bot.message_handler(content_types=['text'])
async def bot_message(message: types.Message):
    user_id = str(message.from_user.id)  # Убедитесь, что user_id - строка

    if user_id not in Settings.user_states:
        Settings.user_states[user_id] = None  # Инициализируем состояние при первом взаимодействии

    if message.text == 'Д/З':
        await Homework._homework_(message)

    if message.text == 'Профком':
        await Union._union_(message)

    if message.text == 'Клуб':
        await Club._club_(message)

    if message.text == 'Подписаться/отписаться от рекламы💜':
        await AdvertisementFile.toggle_subscription(user_id, message)  # Переключение подписки
    if message.text == 'Проверить свою роль✅':
        await check_role(message)
    if message.text == 'Инструкция по использованию🤓':
        await Settings.bot.reply_to(message, "Хочешь научится пользоваться нашим ботом-помощником? "
                                             "Тогда мы с радостью расскажем как именно его нужно использовать\n\n")
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_role_row = await cursor.fetchone()
                if user_role_row and user_role_row[0] is not None:  # Проверяем, что результат не пустой
                    user_role = user_role_row[0]
                    if user_role == 'elder' or user_role == 'admin':
                        await Settings.bot.reply_to(message, "Нижний текст")
                    else:
                        await Settings.bot.reply_to(message, "Нижний текст")
                else:
                    await Settings.bot.reply_to(message, "Нижний текст")  # Обработка случая, когда пользователь не найден
    if message.text == 'Назад':
        await start(message)

    if message.text == 'НОСОВИЦКИЙЛУЧШИЙПРЕПОДАВАТЕЛЬ':
        user_id = str(message.from_user.id)
        Settings.user_states[user_id] = 'waiting_for_group_for_elder'
        await Settings.bot.reply_to(message, "Какая группа?")

    elif Settings.user_states.get(user_id) == 'waiting_for_group_for_elder':
        group = message.text.upper().strip()  # Приводим к верхнему регистру и убираем пробелы

        # Проверяем, есть ли у пользователя уже роль
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
                existing_role = await cursor.fetchone()

            if existing_role and existing_role[0] in ['admin', 'elder']:
                await Settings.bot.reply_to(message, "У вас уже есть роль администратора или старосты.")
            else:
                # Добавляем или обновляем запись пользователя
                if existing_role:
                    await db.execute("UPDATE users SET group_of = ?, role = 'elder' WHERE id = ?", (group, user_id))
                else:
                    await db.execute("INSERT INTO users (id, group_of, role) VALUES (?, ?, 'elder')", (user_id, group))

                await db.commit()
                await Settings.bot.reply_to(message, f"Теперь вы староста группы {group}!")

        # Сбрасываем состояние
        Settings.user_states[user_id] = None

    if message.text.lower() == 'хохол':
        # Путь к файлу с изображением
        photo_path = 'images/pig.webp'

        try:
            # Открываем и отправляем изображение
            with open(photo_path, 'rb') as photo:
                await Settings.bot.send_photo(message.chat.id, photo)
        except FileNotFoundError:
            await Settings.bot.reply_to(message, "Извините, изображение не найдено.")
        except Exception as e:
            await Settings.bot.reply_to(message, f"Произошла ошибка при отправке изображения: {e}")

    if message.text.lower() == 'лучший':
        # Путь к файлу с изображением
        photo_path = 'images/best.jfif'

        try:
            # Открываем и отправляем изображение
            with open(photo_path, 'rb') as photo:
                await Settings.bot.send_photo(message.chat.id, photo)
        except FileNotFoundError:
            await Settings.bot.reply_to(message, "Извините, изображение не найдено.")
        except Exception as e:
            await Settings.bot.reply_to(message, f"Произошла ошибка при отправке изображения: {e}")


    if message.text == 'Изменить дз':
        await Settings.bot.reply_to(message, 'Д/З изменено')
        await Homework.refactor_homework(message, 'Изменить Д/З')

    if message.text == 'Не менять дз':
        await Settings.bot.reply_to(message, 'Изменений нет')
        await Homework.refactor_homework(message, 'Не изменять Д/З')
    
    if message.text == 'Удалить дз':
        await Settings.bot.reply_to(message, 'Д/З удалено')
        await Homework.refactor_homework(message, 'Удалить Д/З')

    
   
    if message.text == 'Вывести ДЗ🚀':
        Settings.user_states[user_id] = 'получить_Д/З_группа'  # Устанавливаем состояние ожидания ввода группы
        await Settings.bot.reply_to(message, "Введите группу для вывода домашнего задания:")


    elif message.text == 'Добавить дз📝':
        user_id = str(message.from_user.id)
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT group_of, role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
        if user_data:
            group, role = user_data
            if role == 'elder':
                # Для старосты сразу используем группу из базы данных
                Settings.user_states[user_id] = 'добавить_Д/З_дата'
                Settings.user_states[f'group_{user_id}'] = group  # Сохраняем группу из базы
                await Settings.bot.reply_to(message, f"Ваша группа: {group}. Теперь введите дату домашнего задания:")
            elif role == 'admin':
                Settings.user_states[user_id] = 'добавить_Д/З_группа'
                await Settings.bot.reply_to(message, 'Введите группу для добавления дз:')
            else:
                await Settings.bot.reply_to(message, "У вас нет прав для добавления ДЗ.")
        else:
            await Settings.bot.reply_to(message, "У вас нет прав для добавления ДЗ.")


    elif message.text == 'Редактировать дз':
        user_id = str(message.from_user.id)
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT group_of, role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
        if user_data:
            group, role = user_data
            if role == 'elder':
                # Для старосты сразу используем группу из базы данных
                Settings.user_states[user_id] = 'редактировать_Д/З_дата'
                Settings.user_states[f'group_{user_id}'] = group
                await Settings.bot.reply_to(message,
                                            f"Ваша группа: {group}. Теперь введите дату домашнего задания для редактирования:")
            elif role == 'admin':
                # Для администратора запрашиваем группу
                Settings.user_states[user_id] = 'редактировать_Д/З_группа'
                await Settings.bot.reply_to(message, 'Введите группу для редактирования дз:')
            else:
                await Settings.bot.reply_to(message, "У вас нет прав для редактирования ДЗ.")
        else:
            await Settings.bot.reply_to(message, "У вас нет прав для редактирования ДЗ.")

    elif Settings.user_states[user_id] == 'редактировать_Д/З_группа':
        # Для администратора запрашиваем группу
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_role_row = await cursor.fetchone()
                user_role = user_role_row[0] if user_role_row and user_role_row[0] else "student"

                if user_role == 'admin':
                    Settings.user_states[user_id] = 'редактировать_Д/З_дата'
                    Settings.user_states[f'group_{user_id}'] = message.text
                    await Settings.bot.reply_to(message, "Теперь введите дату домашнего задания для редактирования:")
                else:
                    await Settings.bot.reply_to(message, "У вас нет прав для редактирования ДЗ для этой группы.")

    elif Settings.user_states[user_id] == 'редактировать_Д/З_дата':
        Settings.user_states[user_id] = 'редактировать_Д/З_предмет'
        Settings.user_states[f'date_{user_id}'] = message.text
        await Settings.bot.reply_to(message, "Теперь введите название предмета для редактирования:")

    elif Settings.user_states[user_id] == 'редактировать_Д/З_предмет':
        Settings.user_states[user_id] = 'редактировать_Д/З_новое_описание'
        Settings.user_states[f'subject_{user_id}'] = message.text
        await Settings.bot.reply_to(message, "Теперь введите новое описание домашнего задания:")

    elif Settings.user_states[user_id] == 'редактировать_Д/З_новое_описание':
        group = Settings.user_states[f'group_{user_id}']
        date = Settings.user_states[f'date_{user_id}']
        subject = Settings.user_states[f'subject_{user_id}']
        new_description = message.text

        # Обновляем запись в базе данных
        async with aiosqlite.connect('database/datahomework.db') as db:
            await db.execute(
                "UPDATE homework SET description = ? WHERE group_of = ? AND date_of = ? AND subject = ?",
                (new_description, group, date, subject)
            )
            await db.commit()

        await Settings.bot.reply_to(message, "✅ Домашнее задание успешно обновлено!")

        # Сбрасываем состояния
        Settings.user_states[user_id] = None
        for key in ['group', 'date', 'subject']:
            Settings.user_states.pop(f'{key}_{user_id}', None)


    elif Settings.user_states[user_id] == 'получить_Д/З_группа':
        Settings.user_states[user_id] = 'получить_Д/З_дата'  # Переходим на этап ввода даты
        Settings.user_states[f'group_{user_id}'] = message.text  # Сохраняем введённую группу
        await Settings.bot.reply_to(message, "Теперь введите дату, на которую вам нужно узнать дз:")

    elif Settings.user_states[user_id] == 'получить_Д/З_дата':
        group = Settings.user_states[f'group_{user_id}']  # Получаем группу
        date = message.text  # Сохраняем введённую дату
        results = await Homework.search_in_database(group, date)
        if results:
            response = f"Список домашнего задания на дату {date}:\n\n" + "\n".join(f"{i + 1}) {row[1]} - {row[2]}" for i, row in enumerate(results))
        else:
            response = "Ничего не найдено."
        await Settings.bot.reply_to(message, response)
        Settings.user_states[user_id] = None # Сбрасываем состояния
        del Settings.user_states[f'group_{user_id}']


    elif Settings.user_states[user_id] == 'добавить_Д/З_группа':
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_role_row = await cursor.fetchone()
                user_role = user_role_row[0] if user_role_row and user_role_row[0] else "student"
                if user_role == 'admin':
                    Settings.user_states[user_id] = 'добавить_Д/З_дата'
                    Settings.user_states[f'group_{user_id}'] = message.text  # Сохраняем введённую группу
                    await Settings.bot.reply_to(message, "Теперь введите дату домашнего задания:")
                else:
                    await Settings.bot.reply_to(message, "У вас нет прав для добавления ДЗ для этой группы.")

    elif Settings.user_states[user_id] in ('добавить_Д/З_дата'):
        Settings.user_states[user_id] = 'добавить_Д/З_предмет'  # Переходим на этап ввода домашнего задания
        Settings.user_states[f'date_{user_id}'] = message.text  # Сохраняем введённую дату
        await Settings.bot.reply_to(message, "Теперь введите название предмета:")


    elif Settings.user_states[user_id] == 'добавить_Д/З_предмет':
        Settings.user_states[user_id] = 'добавить_Д/З_описание'  # Переходим на этап ввода предмета
        Settings.user_states[f'subject_{user_id}'] = message.text  # Сохраняем введённое домашнее задание
        await Settings.bot.reply_to(message, "Теперь введите описание домашнего задания:")


    elif Settings.user_states[user_id] == 'добавить_Д/З_описание':
        group = Settings.user_states[f'group_{user_id}']
        date = Settings.user_states[f'date_{user_id}']
        subject = Settings.user_states[f'subject_{user_id}']
        homework = message.text
        async with aiosqlite.connect('database/datahomework.db') as db: # Вызываем функцию добавления с передачей message
            async with db.execute("SELECT description FROM homework WHERE group_of =  ? AND date_of = ? AND subject = ?", (group,date,subject)) as cursor:
                if await cursor.fetchone() == None:
                    await db.commit()
                    await Homework.insert_into_database(group, date, homework, subject, user_id,message)  # user_id как идентификатор чата
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(types.KeyboardButton('Изменить дз'), types.KeyboardButton('Не менять дз'), types.KeyboardButton('Удалить дз'))
                    await Settings.bot.reply_to(message, 'Домашнее задание уже существует, вы хотите его изменить на вписанное?', reply_markup = markup)
                    Settings.user_refactor_states[message.from_user.id] = group,date,subject,homework
        Settings.user_states[user_id] = None # Сбрасываем состояния
        for key in ['group', 'date', 'subject']:
            Settings.user_states.pop(f'{key}_{user_id}', None)


async def check_role(message):
    user_id = str(message.from_user.id)
    async with aiosqlite.connect('database/datausers.db') as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user_data = await cursor.fetchall()

    if user_data and len(user_data) > 0:  # Если пользователь найден
        user_record = user_data[0]
        group = user_record[1] if len(user_record) > 1 and user_record[1] is not None else "Не указана"
        role = user_record[2] if len(user_record) > 2 and user_record[2] is not None else "student"

        if role == 'admin':
            text = f"ВАША РОЛЬ - АДМИНИСТРАТОР\nВАША ГРУППА - {group}"
        elif role == 'elder':
            text = f"ВАША РОЛЬ - СТАРОСТА\nВАША ГРУППА - {group}"
        else:
            text = 'ВЫ ОБЫЧНЫЙ СТУДЕНТ'
    else:
        text = 'ВЫ ОБЫЧНЫЙ СТУДЕНТ'

    await Settings.bot.reply_to(message, text)


async def resilient_polling():
    while True:
        try:
            await Settings.bot.polling(non_stop=True)
        except Exception as e:
            print(f"Polling error: {e}. Restarting in 5 seconds...")
            await asyncio.sleep(5)

async def init_database():
    # Создаем папку для базы данных, если она не существует
    if not os.path.exists('database'):
        os.makedirs('database')

    # Инициализируем таблицу homework
    async with aiosqlite.connect('database/datahomework.db') as db:  # Убедитесь, что здесь тоже datahomework.db
        await db.execute('''
            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_of TEXT NOT NULL,
                date_of TEXT NOT NULL,
                description TEXT NOT NULL,
                subject TEXT NOT NULL
            )
        ''')
        await db.commit()

    # Инициализируем таблицу users
    async with aiosqlite.connect('database/datausers.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                group_of TEXT,
                role TEXT
            )
        ''')
        await db.commit()

    # Инициализируем таблицу subscriptions
    async with aiosqlite.connect('database/subscriptions.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id TEXT PRIMARY KEY,
                subscribed INTEGER
            )
        ''')
        await db.commit()


async def main():
    # Инициализируем базу данных
    await init_database()

    # Создаем задачу для отправки рекламы
    ads_task = asyncio.create_task(AdvertisementFile.send_advertisements())

    try:
        # Запускаем polling бота
        await resilient_polling()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    finally:
        # Отменяем задачу отправки рекламы при завершении
        ads_task.cancel()
        try:
            await ads_task
        except asyncio.CancelledError:
            print("Advertisement task cancelled")
        # Закрываем сессию бота
        await Settings.bot.close_session()


if __name__ == '__main__':
    # Используем современный способ запуска asyncio
    asyncio.run(main())