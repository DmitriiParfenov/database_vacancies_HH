import json
import os
import time
from abc import ABC, abstractmethod

import requests

from utils.class_operations import Vacancy


class Parser(ABC):
    """Абстрактный класс для работы с API серверов с вакансиями."""

    @abstractmethod
    def get_vacancies_from_employer(self, employer_id):
        """Абстрактный метод для получения вакансий от работодателя."""
        pass

    @abstractmethod
    def get_employer_id(self):
        """Абстрактный метод для получения id работодателя."""
        pass


class HeadHunterApi(Parser):
    """Класс для работы с API HeadHunter."""

    def __init__(self, keyword: str) -> None:
        """
        Экземпляр инициализируется keyword, url_emp, url_vac, hh_apikey, header, param для создания запроса
        на сервер HeadHunter. Название компании записывается в employer_name, id компании в employer_id, данные для
        записи будут подтягиваться по API. В ответ на запрос искомые вакансии в виде экземпляров класса Vacancy
        будут храниться в db_vacancies.
        """
        self.keyword = keyword
        self.__url_emp = 'https://api.hh.ru/employers'
        self.__url_vac = 'https://api.hh.ru/vacancies'
        self.__hh_apikey = os.getenv('HH_API_KEY')
        self.__header = {'client_id': self.__hh_apikey}
        self.__param = {}
        self.__employer_name = ''
        self.__employer_id = ''
        self.__db_vacancies = {}

    @property
    def employer_name(self) -> str:
        """Метод возвращает название компании."""
        return self.__employer_name

    @property
    def employer_id(self) -> str:
        """Метод возвращает id компании."""
        return self.__employer_id

    @property
    def db_vacancies(self) -> dict:
        """Метод возвращает словарь, где ключ - это название компании, а значение - это список вакансий
        текущего работодателя в виде экземпляров класса Vacancy."""
        return self.__db_vacancies

    def get_employer_id(self) -> str:
        """Метод возвращает id компании."""

        # Объявление параметров запроса
        self.__param = {'text': self.keyword, 'only_with_vacancies': True}

        # Запрос на сервер
        request = requests.get(self.__url_emp, headers=self.__header, params=self.__param)

        # Получение данных с сервера
        if request.ok:
            response = request.content.decode()
            request.close()
            data = json.loads(response)
            if data['items']:
                self.__employer_name = data.get('items')[0].get('name')
                self.__employer_id = data.get('items')[0].get('id')
                self.__db_vacancies[self.__employer_name] = []
            else:
                raise Exception(f'Работодатель по ключевому слову {self.keyword} не найден.')
        return self.__employer_id

    def get_vacancies_from_employer(self, employer_id: str) -> dict:
        """Метод по id работодателя получает список всех вакансий в количестве до 1000 штук. Возвращает словарь, где
        ключ - это название компании, а значение - это список вакансий текущего работодателя в виде экземпляров
        класса Vacancy."""

        # Цикл для выборки вакансий до 1000 штук
        for i in range(0, 10):

            # Объявление параметров запроса
            self.__param = {
                'employer_id': employer_id,
                'per_page': 100,
                'page': i,
            }

            # Запрос
            request = requests.get(self.__url_vac, headers=self.__header, params=self.__param)
            if request.ok:
                response = request.content.decode()
                request.close()
                data = json.loads(response)

                # Получение данных и запись их в соответствующие атрибуты экземпляра класса Vacancy
                if data['items']:
                    for item in data['items']:
                        title = item.get('name')
                        url = item.get('alternate_url')
                        if item.get('salary'):
                            salary_from = item.get('salary').get('from')
                            salary_to = item.get('salary').get('to')
                            if not item.get('salary').get('from'):
                                salary_from = 0
                            if not item.get('salary').get('to'):
                                salary_to = 0
                        else:
                            salary_from = 0
                            salary_to = 0
                        if not self.__db_vacancies.get(item.get('employer').get('name')):
                            self.__employer_name = item.get('employer').get('name')
                            self.__db_vacancies[self.__employer_name] = []
                        self.__db_vacancies[self.__employer_name].append(Vacancy(title, url, salary_from, salary_to))
                else:
                    continue
            time.sleep(0.25)
        return self.__db_vacancies
