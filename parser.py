import time

import requests
from bs4 import BeautifulSoup

import config

url_login = "http://us.gblnet.net/oper/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "action": "login",
    "username": config.loginUS,
    "password": config.pswUS
}

# session_users = requests.Session()
#
#
# def create_users_sessions():
#     while True:
#         try:
#             response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
#             # session_users.post(url_login, data=data_users, headers=HEADERS)
#             print("Сессия Юзера создана 3")
#             return response_users2
#         except ConnectionError:
#             print("Ошибка создания сессии")
#             # TODO функция отправки тут отсутствует
#             # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
#             # time.sleep(300)
#
#
# response_users = create_users_sessions()


# def get_html(session_users, staff_id):
#     link = (f"https://us.gblnet.net/oper/index.php?core_section=task_list&"
#             f"filter_selector0=task_state&task_state0_value=1&"
#             f"filter_selector1=task_type&task_type1_value%5b%5d=31&"
#             f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&"
#             f"filter_selector2=task_staff_wo_division&employee_find_input=&"
#             f"employee_id2={staff_id}&sort=datedo&sort_typer=1")
#
#     try:
#         # session_users = requests.Session()
#         html = session_users.get(link)
#         if html.status_code == 200:
#             soup = BeautifulSoup(html.text, 'lxml')
#             table = soup.find_all('tr', class_="cursor_pointer")
#             print(table)
#         else:
#             print("error")
#     except requests.exceptions.TooManyRedirects as e:
#         print(f'{link} : {e}')


def get_master(session_users, link):
    print(f"parser.get_master Парсим ссылку: {link}")
    try:
        html = session_users.get(link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find_all('div', class_="j_card_div")
            masters_list_id = []  # Тут запишем ид всем назначенных мастеров.
            for tab in table:
                search_masters = tab.find_all('div', class_='div_caption')
                # Выше мы получаем список. В первом элементе ищем нужное нам описание.
                # Ищем слово "Исполнители"
                # В случае нахорждения перебираем весь элемент в поисках ссылок.
                if search_masters[0].text.strip() == 'Исполнители':
                    print("Найдены исполнители.")
                    masters = tab.find_all('a')
                    # Перебираем все ссылки в элементе
                    for m_link in masters:
                        # Делим ссылку по =, ищем show&id, предпоследним элементом.
                        # ид мастера последний элемент.
                        # print(f"m_link.get('href') {m_link.get('href')}")
                        m_lst = m_link.get('href').split("=")
                        try:
                            if m_lst[-2] == "show&id":
                                print("Найдена ссылка на мастера.")
                                masters_list_id.append(m_lst[-1])
                        except IndexError:
                            ...
            print(masters_list_id)
            return masters_list_id

        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{link} : {e}')


def get_address(session_users, link):
    print(f"parser.get_address Парсим ссылку: {link}")
    try:
        html = session_users.get(link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find('table', class_="j_table")
            # Ищем ссылки, адрес хранится в одной из них.
            table_a = table.find_all('a')
            print("Парсим ссылки")
            print(table_a)
            if table_a:
                for i in table_a:
                    if 'Россия' in i.text:  # В адресе всегда есть страна
                        print(f"get_address: {i.text}")
                        # Необходимо вернуть ид дома, он в конце ссылки с адресом.
                        id_link = i.get('href').split("=")
                        print(f"id_link: {id_link}")
                        id_link = id_link[-1]
                        print(f"id_link: {id_link}")
                        # На всякий случай(и для тестов) кроме ид вернем адрес.
                        return id_link, i.text
                return "", ""
            # TODO проверить вывод в случае неподходящей ссылки.
            # TODO пользователю должно возвращаться предупреждение.
            else:
                return "", ""
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{link} : {e}')


# Составим потенциальное расписание на доме.
# TODO необходимо выполнить обработку ошибки, если расписания нет.
# TODO ибо оно может зависнуть в бесконечном цикле в поиске 10 слотов.
def get_shelude(session_users, link):
    print(f"parser.get_shelude Парсим ссылку: {link}")
    try:
        html = session_users.get(link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find('div', id="tableTaskIntervalId")
            # Необсходимо вернуть словарь,
            # где ключ порядковый номер дня недели(с 1),
            # а значение список с доступными часами.
            dict_time_address = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
            # print(table)
            # table_input = table.find_all("input", class_="input_box")
            # Переберем заготовленный словарь, подствляя ключи в ид элемента.
            print("Страничка найдена, начинаем перебор словаря.")
            for k, v in dict_time_address.items():
                # В Юзере у последнего дня используется не 7, а 0.
                if k == 7:
                    k = 0
                print(f"Перебираем: {k}, {v}")
                # Начало расписание от первого значения.
                start_hour = int(table.find('input', {'name': f'start_{k}'}).get('value'))
                finish = int(table.find('input', {'name': f'finish_{k}'}).get('value'))
                print(f"start_hour {start_hour}")
                print(f"finish {finish}")
                # Если стартовый час не 0, то перебираем день.
                if start_hour != 0:
                    print("Стартовый час НЕ равен 0")
                    # Запускает бесконечный цикл добавляя по 2 часа пока последний час не больше стартового.
                    while True:
                        print("Начинаем бесконечный цикл")
                        # Если стартовый час <= последнему часу.
                        if start_hour <= finish:
                            print("Стартовый час меньше последнего.")
                            # Добавляем в список к тому дню, который перебираем.
                            v.append(start_hour)
                            print(f"Список обновлен: {v}")
                            # Добавляем 2 часа.
                            start_hour += 2
                        else:  # Иначе прерываем цикл.
                            print("Прерываем цикл.")
                            break
                # Если стартовый час 0, то пропускаем итерацию.
                else:
                    print("Стартовый час равен 0")
                    continue
                print(f"Составлено расписание для: {k}, вышло: {v}")
                print("№№№№№№№№№№№№№№№№№№№№№№№№")
            print("Итог")
            print(dict_time_address)
            return dict_time_address
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{link} : {e}')
