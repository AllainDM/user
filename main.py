import time
from datetime import datetime, timedelta

import requests
from aiogram import Bot, Dispatcher, executor, types
from bs4 import BeautifulSoup

import config


session_users = requests.Session()

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

url_login = "http://us.gblnet.net/oper/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "action": "login",
    "username": config.loginUS,
    "password": config.pswUS
}


def create_users_sessions():
    while True:
        try:
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            time.sleep(300)


def create_sessions():
    global data_users
    global session_users

    # По бесконечному циклу запустим создание сессий
    while True:
        try:
            response_users = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")

            break
        except:
            print("Ошибка создания сессии")
            time.sleep(600)


# Тестовая функция для проверки даты
@dp.message_handler(commands=['0'])
async def echo_mess(message: types.Message):
    await bot.send_message(message.chat.id, f"test")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
