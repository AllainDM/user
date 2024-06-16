import time
from datetime import datetime, timedelta

import requests
from aiogram import Bot, Dispatcher, executor, types
from bs4 import BeautifulSoup

import config
import url
# import parser


session = requests.Session()

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

url_login = "http://us.gblnet.net/oper/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data = {
    "action": "login",
    "username": config.loginUS,
    "password": config.pswUS
}


try:
    response = session.post(url_login, data=data, headers=HEADERS).text
    print("Сессия Юзера создана 1")
except:
    print("Ошибка создания сессии, перезапустите программу")


def create_sessions():
    global data
    global response
    # По бесконечному циклу запустим создание сессий
    while True:
        try:
            response = session.post(url_login, data=data, headers=HEADERS).text
            print("Сессия Юзера создана 2")
            break
        # except ConnectionError:
        except:
            print("Ошибка создания сессии")
            time.sleep(60)


# Тестовая функция
@dp.message_handler(commands=['0'])
async def echo_mess(message: types.Message):
    await bot.send_message(message.chat.id, f"test")


# Тестовая функция
@dp.message_handler(commands=['help'])
async def echo_mess(message: types.Message):
    await bot.send_message(message.chat.id, f"{config.users_dict}")


def get_html(staff_id):
    print("Смотрим ссылку.")
    link = (f"https://us.gblnet.net/oper/index.php?core_section=task_list&"
            f"filter_selector0=task_state&task_state0_value=1&"
            f"filter_selector1=task_type&task_type1_value%5b%5d=31&"
            f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&"
            f"filter_selector2=task_staff_wo_division&employee_find_input=&"
            f"employee_id2={staff_id}&sort=datedo&sort_typer=1")
    print(link)

    try:
        print("Проверяем сессию.")
        html = session.get(link)
        if html.status_code == 200:
            print("Код ответа 200")
            soup = BeautifulSoup(html.text, 'lxml')
            # print(f"soup {soup}")
            table = soup.find_all('tr', class_="cursor_pointer")
            # print(table)
            answer = []
            date_start = ""
            date_arr = ""
            date_time = ""
            for i in table:  # Цикл по списку всей таблицы
                print("########################")
                # print(i)
                list_a = i.find_all('a')  # Ищем ссылки во всей таблице
                conn_link = ""
                number_conn = ""
                for ii in list_a:  # Цикл по найденным ссылкам
                    # print(ii)
                    if len(ii.text) == 7:  # Ищем похожесть на ид ремонта
                        # print(ii.text)
                        number_conn = ii.text
                        conn_link = url.url_link_repair + number_conn
                ceil_date = i.find_all('td', class_="div_center")
                if ceil_date[1].text[-11:-1] == "просрочено":
                    date = ceil_date[1].text[:-11].strip()
                    # print(ceil_date[1].text[:-11])
                else:
                    # print(ceil_date[1].text)
                    date = ceil_date[1].text.strip()
                # ceil = i.find_all('td', class_="")
                ceil_id = i.find(id=f"td_{number_conn}_address_full_Id")
                # print(f"ceil_id {ceil_id.text}")
                # print(ceil[1].text)
                address = ceil_id.text.strip()
                address_split = address.split(" ")
                address_arr = []
                for s in address_split:
                    if s != '':
                        address_arr.append(s)
                    else:
                        break
                print(address_split)
                print(address_arr)
                address_f = ' '.join(address_arr)
                # for c in ceil: f"{date[:-5]}\n\n"
                #     print(c)
                if date_time == date[-5:]:
                    date_time = "!!! Внимание, есть другая заявка на: " + date_time
                else:
                    date_time = date[-5:]
                one = (f"{date_time}\n\n"
                       f"{address_f}\n\n"
                       f"{conn_link}\n\n"
                       f"###########################\n\n")
                if date_start == date[:-5]:  # Тот же день
                    print("Дата совпала")
                    date_arr += one
                else:
                    if date_arr != "":
                        answer.append(date_arr)
                    date_start = date[:-5]
                    date_arr = f"{date[:-5]}\n\n"
                    date_arr += one
                # print(date_arr)
            return answer
        else:
            print("error")
            return "нет"
    except:
        create_sessions()
        return ["Произошла ошибка сессии, бот залогинится снова, "
                "попробуйте выполнить запрос позже, возможно программа даже не сломалась."]
    # except requests.exceptions.TooManyRedirects as e:
    #     print(f'{e}: {link}')


@dp.message_handler()
async def echo_mess(message: types.Message):
    # Получим ид пользователя и сравним со списком разрешенных в файле конфига
    user_id = message.from_user.id
    print(f"user_id {user_id}")
    if user_id in config.users:
        print("Пользователь авторизован.")
        # answer = get_html(855)
        if message.text.isdigit():
            answer = get_html(message.text)
            print(f"answer: {answer}")
            try:
                for a in answer:
                    await bot.send_message(message.chat.id, a)
            except:
                print(f"{datetime.now()}: Ошибка с получением ответа от парсера")
                await bot.send_message(message.chat.id, f"Ответ: Ошибка с получением ответа от парсера")
        else:
            print("Не число")
            if message.text.lower() == "перенести":
                text_msg = message.reply_to_message.text
                # Разделим сообщение по переносу строки
                # Адрес будем брать как 4 элемент. А ссылку как 8 элемент.
                text_msg_list = text_msg.split("\n")
                print(f"text_msg: {text_msg}")
                print(f"text_msg_list: {text_msg_list}")
                print(f"text_msg_list: {text_msg_list[4]}")
                print(f"text_msg_list: {text_msg_list[7]}")
                await bot.send_message(message.chat.id,
                                       f"Переносим адрес: \n\n"
                                       f"{text_msg_list[4]} \n\n"
                                       f"Выберите время:")

    else:
        await bot.send_message(message.chat.id, "Вы не авторизованны")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    # get_html(855)


