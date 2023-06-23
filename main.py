from db_operations import Connector, DBManager
from utils.hh_parser import HeadHunterApi


def main():
    """
    Функция позволяет добавлять работодателей в базу данных и получать вакансии по заданным критериям.
    Реализация функции через взаимодействие с пользователем.
    """
    # Создание экземпляра класса для подключения к postgresql
    database = Connector()

    # Создание базы данных "vacancies"
    database.create_db('vacancies')

    # Создание таблиц "db_vacancies" и "employers" в базе данных "vacancies"
    database.create_tables('vacancies')

    # Список всех работодателей
    employers_list = []

    # Приветственное сообщение
    print("""Данный скрипт вносит в базу данных информацию о вакансиях от интересующих работодателей.
Осуществляет выборку вакансий по заданным критериям.""")
    print("МЕНЮ:")
    print("-----\n1. Добавить в базу данных нового работодателя.\n2. Выбрать интересующие вакансии.\n3. Выход.")

    # Взаимодействие с пользователем
    user_answer = input("Введите выбранный пункт: ")
    while user_answer not in ('1', '2', '3'):
        user_answer = input("Повторно введите выбранный пункт: ")

    # Добавление работодателя в базу данных
    if user_answer == '1':
        while True:

            # Взаимодействие с пользователем
            print("Добавление работодателя:")
            print("------------------------\n1. Добавить.\n2. Выбрать интересующие вакансии.\n3. Выход.")
            user_answer_adder = input("Введите выбранный пункт: ")
            while user_answer_adder not in ('1', '2', '3'):
                user_answer_adder = input("Повторно введите выбранный пункт: ")

            # Добавление работодателя в базу данных
            if user_answer_adder == '1':
                user_company = input("Введите интересующего работодателя: ").title()
                if user_company in employers_list:
                    print('Данный работодатель уже есть в базе данных')
                    continue
                employers_list.append(user_company)
                company = HeadHunterApi(user_company)
                id_company = company.get_employer_id()
                company.get_vacancies_from_employer(id_company)
                dbmanager = DBManager()
                dbmanager.add_employer_with_vacancies(company, 'vacancies')

            # Переход к меню для выбора вакансий по критериями
            elif user_answer_adder == '2':
                user_answer = '2'
                break

            # Выход из программы
            elif user_answer_adder == '3':
                return

    # Выбор вакансий по критериями
    if user_answer == '2':
        while True:

            # Взаимодействие с пользователем
            print("МЕНЮ:")
            print("-----")
            print("1. Получить список всех компаний и количества вакансий у каждой компании.")
            print("2. Получить список вакансий с указанием компании, названии вакансии, зарплаты и ссылки.")
            print("3. Получить среднюю зарплату по вакансиям.")
            print("4. Получить список вакансий, у которых зарплата выше средней по вакансиям.")
            print("5. Получить список вакансий по ключевому слову.")
            print("6. Выход.")
            user_answer_getter = input("Введите выбранный пункт: ")
            db_getter = DBManager()
            while user_answer_getter not in ('1', '2', '3', '4', '5', '6'):
                user_answer_getter = input("Повторно введите выбранный пункт: ")

            # Вывод всех компаний и количества вакансий у каждой компании
            if user_answer_getter == '1':
                if db_getter.get_companies_and_vacancies_count():
                    print(db_getter.get_companies_and_vacancies_count())
                else:
                    print("В базе данных еще нет ни одной компании с вакансиями.")
                    continue

            # Вывод списка вакансий с указанием компании, названии вакансии, зарплаты и ссылки
            elif user_answer_getter == '2':
                if db_getter.get_all_vacancies():
                    print(db_getter.get_all_vacancies())
                else:
                    print("В базе данных еще нет ни одной компании с вакансиями.")
                    continue

            # Вывод средней зарплаты по вакансиям
            elif user_answer_getter == '3':
                if db_getter.get_avg_salary():
                    print(db_getter.get_avg_salary())
                else:
                    print("В базе данных еще нет ни одной компании с вакансиями.")
                    continue

            # Вывод списка вакансий, у которых зарплата выше средней по вакансиям
            elif user_answer_getter == '4':
                if db_getter.get_vacancies_with_higher_salary():
                    print(db_getter.get_vacancies_with_higher_salary())
                else:
                    print("В базе данных еще нет ни одной компании с вакансиями.")
                    continue

            # Вывод списка вакансий по ключевому слову.
            elif user_answer_getter == '5':
                user_keyword = input("Введите ключевое слово: ").lower()
                if db_getter.get_vacancies_with_keyword(user_keyword):
                    print(db_getter.get_vacancies_with_keyword(user_keyword))
                else:
                    print("В базе данных еще нет ни одной компании с вакансиями.")
                    continue

            # Выход из программы
            elif user_answer_getter == '6':
                return

    # Выход из программы
    elif user_answer == '3':
        return


if __name__ == '__main__':
    main()
