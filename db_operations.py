import psycopg2
from psycopg2.errors import DuplicateDatabase
from utils.hh_parser import HeadHunterApi

from config import config


class Connector:
    """Класс для создания базы данных и таблиц."""
    def __init__(self) -> None:
        """
        Экземпляр инициализируется params для подключения к postgres.
        """
        self.params = config()

    def create_db(self, database_name: str) -> None:
        """Метод в качестве аргумента принимает название базы данных и создает базу данных."""

        # Подключение к существующей базе данных
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        # Создание новой базы данных
        try:
            cur.execute(f'CREATE DATABASE {database_name}')
        except DuplicateDatabase:
            pass
        finally:
            cur.close()
            conn.close()

    def create_tables(self, database_name: str) -> None:
        """Метод в качестве аргумента принимает название базы данных и создает в ней две таблицы: employers и
        db_vacancies."""

        # Подключение к базе данных
        conn = psycopg2.connect(dbname=database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:

                    # Создание таблицы employers
                    cur.execute("""CREATE TABLE IF NOT EXISTS employers (
                    employers_id SERIAL,
                    company_name VARCHAR,

                    CONSTRAINT pk_employers_employers_id PRIMARY KEY (employers_id)
                    )""")
                with conn.cursor() as cur:

                    # Создание таблицы db_vacancies
                    cur.execute("""CREATE TABLE IF NOT EXISTS db_vacancies (
                    vacancies_id SERIAL,
                    employers_id INT REFERENCES employers (employers_id),
                    vacancy_name VARCHAR,
                    url VARCHAR,
                    salary_from INT,
                    salary_to INT,

                    CONSTRAINT pk_vacancies_vacancies_id PRIMARY KEY (vacancies_id),
                    CONSTRAINT chk_vacancies_salary_from CHECK (salary_from >= 0),
                    CONSTRAINT chk_vacancies_salary_to CHECK (salary_to >= 0),
                    CONSTRAINT fk_db_vacancies_employers FOREIGN KEY (employers_id) REFERENCES employers (employers_id)
                    )""")
        finally:
            conn.close()


class DBManager(Connector):
    """Класс для работы с данными в базе данных."""

    def add_employer_with_vacancies(self, employer: HeadHunterApi, database_name: str) -> None:
        """
        Метод добавляет работодателя в таблицу 'employers' и все вакансии от работодателя в таблицу 'db_vacancies'.
        Наполняемые таблицы находятся в базе данных 'vacancies'.
        """

        # Подключение к базе данных
        conn = psycopg2.connect(dbname=database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:

                    # Добавление работодателя в таблицу employers
                    cur.execute(
                        """
                        INSERT INTO employers (company_name)
                        VALUES (%s)
                        RETURNING employers_id
                        """,
                        (employer.employer_name,))
                    employers_id = cur.fetchone()[0]

                    # Добавление вакансий текущего работодателя в таблицу db_vacancies
                    for elem in employer.db_vacancies[employer.employer_name]:
                        cur.execute(
                            """
                            INSERT INTO db_vacancies (employers_id, vacancy_name, url, salary_from, salary_to)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (employers_id, elem.title, elem.url, elem.salary_from, elem.salary_to)
                        )

        finally:
            conn.close()

    def get_companies_and_vacancies_count(self) -> str:
        """Метод возвращает список всех компаний и количества вакансий у каждой компании."""

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='vacancies', **self.params)
        result = ''
        try:
            with conn:
                with conn.cursor() as cur:

                    # Выборка компаний и количества вакансий
                    cur.execute("""SELECT employers.company_name, COUNT(vacancies_id)
                                   FROM employers INNER JOIN db_vacancies USING (employers_id)
                                   GROUP BY employers.company_name
                                   ORDER BY employers.company_name DESC""")

                    # Запись результатов выборки в result
                    for elem in cur.fetchall():
                        result += f"Компания '{elem[0]}' имеет {elem[1]} вак.\n"

        finally:
            conn.close()
        return result

    def get_all_vacancies(self) -> str:
        """Метод возвращает список всех вакансий с указанием компании, названии вакансии, зарплаты и ссылки."""

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='vacancies', **self.params)
        result = ''
        try:
            with conn:
                with conn.cursor() as cur:

                    # Выборка вакансий
                    cur.execute(
                        """
                        SELECT company_name AS Название_компании, vacancy_name AS Вакансия,
                        (CASE
                            WHEN salary_from = 0 AND salary_to = 0 THEN 0
                            WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                            WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                            ELSE (salary_from + salary_to) / 2
                        END) AS Зарплата, url AS Ссылка
                        FROM employers INNER JOIN db_vacancies USING (employers_id)
                        ORDER BY 3 DESC
                        """)

                    # Запись результатов выборки в result
                    for elem in cur.fetchall():
                        result += f"Компания '{elem[0]}', Вакансия '{elem[1]}', Зарплата {elem[2]}, Ссылка {elem[3]}.\n"
        finally:
            conn.close()
        return result

    def get_avg_salary(self) -> str:
        """Метод возвращает среднюю зарплату по вакансиям."""

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='vacancies', **self.params)
        result = ''
        try:
            with conn:
                with conn.cursor() as cur:

                    # Выборка зарплаты
                    cur.execute("""SELECT ROUND(AVG(CASE
                        WHEN salary_from = 0 AND salary_to = 0 THEN 0
                        WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                        WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                        ELSE (salary_from + salary_to) / 2
                    END), 1) AS Зарплата
                    FROM db_vacancies   
                        WHERE (CASE
                        WHEN salary_from = 0 AND salary_to = 0 THEN 0
                        WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                        WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                    ELSE (salary_from + salary_to) / 2
                    END) <> 0
                        """)

                    # Запись результатов выборки в result
                    result += f'Средняя зарплата по вакансиям - {cur.fetchone()[0]} рублей.'
        finally:
            conn.close()
        return result

    def get_vacancies_with_higher_salary(self) -> str:
        """Метод возвращает список вакансий, у которых зарплата выше средней по вакансиям."""

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='vacancies', **self.params)
        result = ''
        try:
            with conn:
                with conn.cursor() as cur:

                    # Выборка вакансий
                    cur.execute("""WITH get_avg_salary(avg_salary)
                    AS (SELECT AVG(CASE
                                        WHEN salary_from = 0 AND salary_to = 0 THEN 0
                                        WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                                        WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                                        ELSE (salary_from + salary_to) / 2
                                   END)
                        FROM db_vacancies
                        WHERE (CASE
                                    WHEN salary_from = 0 AND salary_to = 0 THEN 0
                                    WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                                    WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                                    ELSE (salary_from + salary_to) / 2
                               END) <> 0
                    )
                    
                    SELECT vacancy_name AS Вакансия, (CASE
                                                          WHEN salary_from = 0 AND salary_to = 0 THEN 0
                                                          WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                                                          WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                                                          ELSE (salary_from + salary_to) / 2
                                                      END) AS Зарплата
                    FROM db_vacancies, get_avg_salary
                    WHERE (CASE
                               WHEN salary_from = 0 AND salary_to = 0 THEN 0
                               WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
                               WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
                               ELSE (salary_from + salary_to) / 2
                           END) > get_avg_salary.avg_salary
                    """)

                    # Запись результатов выборки в result
                    for elem in cur.fetchall():
                        result += f"Вакансия - {elem[0]}, зарплата - {elem[1]}\n"

        finally:
            conn.close()
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> str:
        """Метод возвращает список вакансий по ключевому слову."""

        # Получение ключевого слова в разных регистрах вне зависимости от количества слов в string
        keyword_title = keyword[0].upper() + keyword[1:].lower()
        keyword_lower = keyword.lower()

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='vacancies', **self.params)
        result = ''
        try:
            with conn:
                with conn.cursor() as cur:

                    # Выборка вакансий
                    cur.execute(
                        """
                        SELECT vacancy_name, url
                        FROM db_vacancies
                        WHERE vacancy_name LIKE '%{0}%' OR vacancy_name LIKE '%{1}%'
                        """.format(keyword_title, keyword_lower))

                    # Запись результатов выборки в result
                    for elem in cur.fetchall():
                        result += f"Вакансия - {elem[0]}, ссылка на вакансию - {elem[1]}.\n"
        finally:
            conn.close()
        return result
