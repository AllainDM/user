import time
from datetime import datetime, timedelta

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

import config
import url
import links
import parser
import free_time


session = requests.Session()

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

url_login = "http://us.gblnet.net/oper/"
# url_login = "https://dev-us.gblnet.net/"


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


def get_html(staff_id, type_req, search_date):
    print("Смотрим ссылку.")
    link2 = (f"https://us.gblnet.net/oper/index.php?core_section=task_list&"
    # link = (f"https://dev-us.gblnet.net//oper/index.php?core_section=task_list&"
            f"filter_selector0=task_state&task_state0_value=1&"
            f"filter_selector1=task_type&task_type1_value%5b%5d=31&"
            f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&"
            f"filter_selector2=task_staff_wo_division&employee_find_input=&"
            f"employee_id2={staff_id}&sort=datedo&sort_typer=1")
    link = (f"https://us.gblnet.net/oper/index.php?core_section=task_list&"
            f"filter_selector0=task_state&task_state0_value=1&"
            f"filter_selector1=task_type&task_type1_value%5B%5D=7&"
            f"task_type1_value%5B%5D=31&task_type1_value%5B%5D=1&"
            f"task_type1_value%5B%5D=41&filter_selector2=task_staff_wo_division&"
            f"employee_find_input=&employee_id2={staff_id}&sort=datedo&sort_typer=1")
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
            # date_start = ""  # День
            # date_arr = ""   # Полный список. Время, адрес, ссылка.
            # date_time = ""  # Время
            # cur_shelude = ""  # Занятое расписание. ! Сохраняется в обычный ответ
            for i in table:  # Цикл по списку всей таблицы
                print("########################")
                # print(i)
                list_a = i.find_all('a')  # Ищем ссылки во всей таблице
                conn_link = ""
                number_conn = ""
                for ii in list_a:  # Цикл по найденным ссылкам
                    if len(ii.text) == 7:  # Ищем похожесть на ид ремонта
                        number_conn = ii.text
                        conn_link = url.url_link_repair + number_conn
                ceil_date = i.find_all('td', class_="div_center")
                # Вырежем слово "просрочено" из даты, если оно есть
                if ceil_date[1].text[-11:-1] == "просрочено":
                    date = ceil_date[1].text[:-11].strip()
                else:
                    date = ceil_date[1].text.strip()
                # Ищем ячейку с адресом
                ceil_id = i.find(id=f"td_{number_conn}_address_full_Id")
                # print(f"ceil_id {ceil_id.text}")
                # print(ceil[1].text)
                address = ceil_id.text.strip()
                address_split = address.split(" ")
                address_arr = []
                # "Удлаляем" с нового списка с адресом пустые элементы
                for s in address_split:
                    if s != '':
                        address_arr.append(s)
                    else:
                        break
                print(address_split)
                print(address_arr)
                # Обьединяем список с адресом в нормальную строку
                address_f = ' '.join(address_arr)
                # for c in ceil: f"{date[:-5]}\n\n"
                #     print(c)
                date_start = date[:-5]
                date_time = date[-5:]
                # Ответ для вывода мастеру = req.
                one_for_req = (f"{date_start}\n\n"
                               f"{date_time}\n\n"
                               f"{address_f}\n\n"
                               f"{conn_link}\n\n")
                # Ответ для составления расписания = shelude.
                # Для составления расписания будем использовать дату без приписки дня(из 2 букв)
                # Для этого разделим по пробелу и возьмем первый элемент.
                date_sh = date_start.split(" ")
                # Для времени возьмем только часы.
                time_hour = date_time.split(":")
                time_hour = time_hour[0]
                # one_for_shelude = [date_sh[0], date_time, address_f, conn_link[:-8]]
                # Сохраним только дату и часы
                one_for_shelude = [date_sh[0], time_hour]
                # Добавления в список нужного ответа.
                if type_req == "req":
                    if search_date:  # Если есть дата, то используем только ее.
                        print(f"Поиск по дате: {search_date[:10]}")
                        print(f"Найденная дата: {date_start[:10]}")
                        if search_date[:10] == date_start[:10]:
                            print(f"Дата совпала {search_date[:10]}")
                            answer.append(one_for_req)
                        else:
                            print("Дата НЕ совпала.")
                    else:  # Если дата пустая, то сохраняем все.
                        answer.append(one_for_req)
                else:
                    answer.append(one_for_shelude)
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


@dp.message_handler(commands=['сегодня', 'завтра', 'послезавтра'])
async def today(message: types.Message):
    # Получим ид пользователя и сравним со списком разрешенных в файле конфига
    user_id = message.from_user.id
    # Получим текущую дату
    date_now = datetime.now()
    start_day = date_now
    # Разделим аргументы на список
    args = message.text.split(" ")
    # Уточним дату
    if args[0] == "/завтра":
        start_day = date_now + timedelta(1)
    elif args[0] == "/послезавтра":
        start_day = date_now + timedelta(2)
    # Приведем дату в нужному формату
    date_now_format = start_day.strftime("%d.%m.%Y")
    print(f"Дата для поиска {date_now_format}")
    if user_id in config.users:
        print("Пользователь авторизован 2.")
        print(args)
        # Второй аргумент у get_html это тип запроса, req = поиск и выдача пользователю
        # Запрос может быть просто для поиска и составления расписания,
        try:
            print(args[1])
            answer = get_html(args[1], "req", date_now_format)
        except IndexError:
            answer = get_html(config.users_id_dict[user_id], "req", date_now_format)
        # Этот вроде бы более логичный вариант почему-то не работает.
        # if args[1]:
        #     print(args[1])
        #     answer = get_html(args[1])
        # else:
        #     answer = get_html(config.users_id_dict[user_id])
        print(config.users_id_dict[user_id])
        # print(config.users_id_dict)
        print(f"answer: {answer}")
        try:
            if answer:
                for a in answer:
                    time.sleep(0.5)
                    await bot.send_message(message.chat.id, a)
            else:
                await bot.send_message(message.chat.id, "Ничего нет.")
        except:
            print(f"{datetime.now()}: Ошибка с получением ответа от парсера")
            await bot.send_message(message.chat.id, f"Ответ: Ошибка с получением ответа от парсера")

        # answer = get_html(855)


@dp.message_handler()
async def echo_mess(message: types.Message):
    # Получим ид пользователя и сравним со списком разрешенных в файле конфига
    user_id = message.from_user.id
    print(f"user_id {user_id}")
    print(f"message.text {message.text}")
    if user_id in config.users:
        print("Пользователь авторизован.")
        # Если сообщение число похожее на ид мастера, то выдадим его подключения.
        if message.text.isdigit() and len(message.text) < 5:
            answer = get_html(message.text, "req", "")
            print(f"answer: {answer}")
            try:
                for a in answer:
                    await bot.send_message(message.chat.id, a)
            except:
                print(f"{datetime.now()}: Ошибка с получением ответа от парсера")
                await bot.send_message(message.chat.id, f"Ответ: Ошибка с получением ответа от парсера")
        # В противоположном случае обрабатываем переносы заявок.
        # Или через ключевое слово "перенести" ответом на ранее выданную заявку мастера.
        # Или ссылку/7-ми значный номер сервисной заявки, для получения расписания перед получением вариантов переноса.
        else:
            print("Не ид.")
            # Проверим сразу три подходящих варианта для переноса заявок.
            # Первые два это ссылка или просто 7-ми значный номер.
            # Для обработки ссылки разделим сообщение по =.
            # Но если отправить просто 7-ми значный номер заявки эффект будет тот же.
            # Последним элементом будет 7-ми значный номер который так же является числом.
            # Третим вариантом является ключевое слово "перенести".
            message_lst = message.text.split("=")
            if len(message_lst[-1]) == 7 and message_lst[-1].isdigit() or message.text.lower() == "перенести":
                # print(f"Тут номер заявки.")
                # print(message_lst)
                # print(message_lst[-1])
                num_service = ""  # Номер заявки.
                address = ""    # Адрес.
                link_service = ""  # Ссылка на заявку.
                # При ключевом слове "перенести" мы уже тыкаем на полученное сообщение от бота с заявкой.
                if message.text.lower() == "перенести":
                    print("Испоьзовано ключевое слово 'перенести'.")
                    # При ключевом слове "перенести" необходимо отвечать на сообщение от бота,
                    # из которого подтянется инфа о заявке.
                    if message.reply_to_message:
                        print("Ключевое слово 'перенести' использовано как ответ на сообщение бота.")
                        text_msg = message.reply_to_message.text
                        # Разделим сообщение по переносу строки.
                        # Адрес будем брать как 4 элемент. А ссылку как 8 элемент.
                        text_msg_list = text_msg.split("\n")
                        print(f"text_msg_list {text_msg_list}")
                        # Достанем номер заявки
                        # ! Только для 7-ми значных сервисов.
                        try:
                            num_service = text_msg_list[-1][-7:]  # Номер заявки
                            address = text_msg_list[4]  # Адрес для ответа боту.
                            link_service = text_msg_list[7]  # Ссылка на заявку.
                        except IndexError:
                            await bot.send_message(message.chat.id, "Произошла ошибка 1.")
                        # TODO необходимо обработать вариант ошибки,
                        #  когда пишут "перенести" в ответ на левое сообщение.
                        print(f"address {address}")
                        print(f"номер заявки: {num_service}")
                        print(f"Ссылка на заявку: {link_service}")
                    else:
                        await bot.send_message(message.chat.id,
                                               "Ключевое слово 'перенести' "
                                               "необходимо использовать ответом на заявку от бота "
                                               "по заранее запрошенным заявка мастера, "
                                               "в виде простого сообщения с ид мастера. "
                                               "Ид некоторых мастеров можно получить командой /help.")
                # Вариант с ссылкой или с 7-ми значным номером заявки.
                elif len(message_lst[-1]) == 7 and message_lst[-1].isdigit():
                    link_service = f"http://us.gblnet.net/oper/?core_section=task&action=show&id={message_lst[-1]}"
                    print(f"link_service: {link_service}")

                # Собираем расписение
                # Получим ид исполнителей
                # Первым аргументом передаем сессию, так как используется отдельный модуль.
                masters = parser.get_master(session, link_service)
                print(f"Получаем ид мастеров: {masters}")
                # Сделаем запрос к заявкам, чтобы составить расписание.
                answer = get_html(config.users_id_dict[user_id], "shelude", "")
                # Поиск свободного времени
                # TODO используем заглушку на номер дома
                free_slots = free_time.free_time(answer, 15517)
                print(f"free_slots {free_slots}")
                print(f"answer {answer}")

                # Х. Тут мы собираем ответ боту.
                main_text = (f"Переносим адрес: \n\n"
                             f"{address} \n\n"
                             f"Выберите время:")
                list_time = [[f"{t[0]} {t[2]} {t[1]}:00", f"{t[1]}:00 {t[0]} {num_service}"] for t in free_slots]
                print(f"list_time: {list_time}")
                markup = types.InlineKeyboardMarkup(row_width=1)
                for text, data1 in list_time:
                    markup.insert(types.InlineKeyboardButton(text=text, callback_data=data1))

                await message.answer(main_text, reply_markup=markup)

    else:
        await bot.send_message(message.chat.id, "Вы не авторизованны")


def change_time_task(task):
    # Дата формата 10:00 20.06.2024, необходимо разделить на 3 элемента, дату, часы, минуты
    # Заменим ":" пробелом и разделим по пробелу
    new_date_lst = task.replace(":", " ")
    new_date_lst = new_date_lst.split(" ")
    datedo = new_date_lst[2]
    timedo = new_date_lst[0]
    timedo1 = new_date_lst[1]
    id_task = new_date_lst[3]
    print(f"datedo {datedo}")
    print(f"datedo {timedo}")
    print(f"datedo {timedo1}")
    print(f"datedo {id_task}")
    data_task_done = {
        "core_section": "task",
        "action": "date_work_save",
        "id": id_task,  # Тут номер заявки
        "datedo": datedo,
        "timedo": timedo,
        "timedo1": timedo1,
    }
    session.post(url_login, data=data_task_done, headers=HEADERS)


@dp.callback_query_handler()
async def time_callback(callback: types.CallbackQuery):
    print(callback.data)
    print(callback.values)  # Тут много разной инфы
    change_time_task(callback.data)
    await bot.send_message(callback.from_user.id, f"Заява перенесена(но это не точно)"
                                                  f" на {callback.data}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
