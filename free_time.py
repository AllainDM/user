from datetime import datetime, timedelta

import address_and_time


# Для вывода текста в сообщении, для наглядности.
day_weeks_name = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


def free_time(lst, shelude):
    date_now = datetime.now()
    print("Вывод дня недели.")
    print(date_now.weekday())
    date_now_format = date_now.strftime("%d.%m.%Y")

    # Первый вариант с расписаниями сохраненными в этой программе.
    # Теперь передаем готовое расписание вхятое с дома.
    # Составим расписание на свободное время.
    # Найдем расписание в списке.
    # В первую очередь ищем в уникальных значениях.
    # shelude = {}
    # if address in address_and_time.dict_time_address:
    #     print("Уникальное время.")
    #     shelude = address_and_time.dict_time_address[address]
    #     print(f"shelude {shelude}")
    #
    # elif address in address_and_time.list_standart_five:
    #     print("Дом в стандартной пятидневке.")
    #     shelude = address_and_time.dict_time_address["standart_five"]
    #     print(f"shelude {shelude}")
    #
    # elif address in address_and_time.list_standart_seven:
    #     print("Доступ в любое время. Добавить 20:00 ?")
    #     shelude = address_and_time.dict_time_address["standart_seven"]
    #     print(f"shelude {shelude}")

    free_time_lst = []
    print("Вывод расписания.")
    for _, v in shelude.items():
        print(v)

    # while True:
    for _ in range(100):  # TODO временный(а может нет) вариант, обработки ошибки когда расписание пустое.
        print("Идем по циклу.")
        # Начинаем с день + 1, с завтра. Так же на каждой итерации добавляется 1 день.
        date_now = date_now + timedelta(1)
        day_week = date_now.weekday() + 1  # +1 чтобы понедельник был 1, а не 0.
        date_now_format = date_now.strftime("%d.%m.%Y")  # Формат для сравнения с уже существующими заявками.
        print(f"date_now_format {date_now_format}")
        print(f"day_week {day_week}")
        # Соберем дату как в забитом расписании, для удобства сравнения со списком.
        # Но сначала найдем свободный день и время в базовом расписании.
        # Пройдемся по часам в выбранном дне.
        print(f"shelude[day_week] {shelude[day_week]}")
        for t in shelude[day_week]:
            check_time = [date_now_format, str(t)]  # Соберем дату как в забитом расписании.
            print(f"check_time {check_time}")

            if check_time in lst:  # Поиск совпадения в текущем расписании.
                print(f"check_time {check_time} есть в расписании.")
                continue
            else:
                print(f"check_time {check_time} НЕТ в расписании.")
                # Добавим в слот назвавние дня недели.
                check_time.append(day_weeks_name[day_week])
                free_time_lst.append(check_time)
        # Выйдем из цикла после сбора 10 слотов.
        if len(free_time_lst) > 10:
            return free_time_lst


