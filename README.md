# Проект — database_vacancies_HH

database_vacancies_HH — это проект, который с помощью API обращается к серверам HeadHunters, получает id желаемого
работодателя и список всех его вакансий. Данные сохраняются в базу данных Postgres. Скрипт позволяет получать вакансии
по заданным критериям. Выборка вакансий реализована через взаимодействие с пользователем. </br>
В коде используются библиотеки: `time`, `requests`, `psycopg2`, `os`, `json`, `config`.

# Клонирование репозитория

В проекте для управления зависимостями используется [poetry](https://python-poetry.org/). </br>
Выполните в консоли: </br>

Для Windows: </br>
```
git clone git@github.com:DmitriiParfenov/database_vacancies_HH.git
python -m venv venv
venv\Scripts\activate
pip install poetry
poetry install
```

Для Linux: </br>
```
git clone git@github.com:DmitriiParfenov/database_vacancies_HH.git
cd database_vacancies_HH
python3 -m venv venv
source venv/bin/activate
curl -sSL https://install.python-poetry.org | python3
poetry install
```

# Получение ключей API

- Получите ключ API для поиска вакансий на сайте [dev.hh.ru](https://dev.hh.ru/admin).
- Установите ключ API в переменную окружения: `HH_API_KEY`.

# Работа с базой данной PostgreSQL

- Установите пароль для работы с базой данных в переменную окружения: `password`.
- В директории проекта создайте файл `database.ini`. Пример содержимого файла:
    ```
    [postgresql]
    HOST=localhost
    USER=postgres
    PASSWORD=password
    POSTGRES_PORT=5432
    ```
- В результате выполнения скрипта будет создана база данных `vacancies`. В ней будут следующие таблицы:
  - `employers` - содержит названия компаний;
  - `db_vacancies` - содержит названия вакансий, id компаний, зарплату и ссылку на вакансию.

# Запуск
- Зайдите в директорию `database_vacancies_HH/main.py` и запустите скрипт.
- Следуйте инструкциям, которые выводятся в терминале.