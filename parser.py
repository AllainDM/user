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

session_users = requests.Session()

full_link = ("https://us.gblnet.net/oper/index.php?core_section=task_list&"
             "filter_selector0=task_state&task_state0_value=1&"
             "filter_selector1=task_type&task_type1_value%5b%5d=31&task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&"
             "filter_selector2=task_staff_wo_division&employee_find_input=&employee_id2=855&sort=datedo&sort_typer=1")


def create_users_sessions():
    while True:
        try:
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 3")
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # TODO функция отправки тут отсутствует
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            # time.sleep(300)


response_users = create_users_sessions()

# Коряков 855
# Куропятников 877


def get_html(staff_id):
    link = (f"https://us.gblnet.net/oper/index.php?core_section=task_list&"
            f"filter_selector0=task_state&task_state0_value=1&"
            f"filter_selector1=task_type&task_type1_value%5b%5d=31&"
            f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&"
            f"filter_selector2=task_staff_wo_division&employee_find_input=&"
            f"employee_id2={staff_id}&sort=datedo&sort_typer=1")

    try:
        html = session_users.get(link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find_all('tr', class_="cursor_pointer")
            print(table)
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{link} : {e}')
