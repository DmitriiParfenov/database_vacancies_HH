import os
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql') -> dict:
    """Метод для парсинга файла с настройками для подключения к postgresql."""

    # Создание парсера
    parser = ConfigParser()

    # Чтение парсера
    parser.read(filename)
    db = {'password': os.getenv('password')}

    # Запись данных в парсер
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'section {section} is not found in the file {filename}')
    return db
