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

telebot = install_and_import('pyTelegramBotAPI', 'telebot')
from telebot.async_telebot import AsyncTeleBot

TOKEN = '6716462372:AAFtzj3Yu0R0rdCB-vwGLushyeqxR8RZiIQ'
bot = AsyncTeleBot(TOKEN)
user_states = {} # Состояние для отслеживания ввода
user_refactor_states = {} # Состояния для отслеживания замены