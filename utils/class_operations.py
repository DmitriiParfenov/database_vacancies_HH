class Vacancy:
    """Класс для представления вакансий."""
    def __init__(self, title: str, url: str, salary_from: int, salary_to: int) -> None:
        """
        Экземпляр инициализируется title, url, salary_from, salary_to для хранения информации об вакансии.
        При инициализации экземпляров класса Vacancy происходит валидация данных при помощи метода validate date.
        """
        self._title = title
        self._url = url
        self._salary_from = salary_from
        self._salary_to = salary_to
        self.__validate_data(title, url, salary_from, salary_to)

    @staticmethod
    def __validate_data(title: str, url: str, salary_from: int, salary_to: int):
        """Метод проверяет корректность входных данных при инициализации экземпляров класса Vacancy."""
        if not isinstance(title, str):
            raise TypeError('Название вакансии должно быть строкой')
        if not isinstance(url, str):
            raise TypeError('Ссылка на вакансию должна быть строкой')
        if not isinstance(salary_from, int):
            raise TypeError('Зарплата должна быть целым числом')
        if not isinstance(salary_to, int):
            raise TypeError('Зарплата должна быть целым числом')

    @property
    def title(self) -> str:
        """Метод возвращает название вакансии."""
        return self._title

    @property
    def url(self) -> str:
        """Метод возвращает ссылку на вакансии."""
        return self._url

    @property
    def salary_from(self) -> int:
        """Метод возвращает начальное значение зарплатной вилки."""
        return self._salary_from

    @property
    def salary_to(self):
        """Метод возвращает конечное значение зарплатной вилки."""
        return self._salary_to

    def __str__(self) -> str:
        """Возвращает строку с атрибутами экземпляров в дружественном формате."""
        result = ''
        for elem in self.__dict__:
            result += f'{elem}: {self.__dict__[elem]}\n'
        return result

    def __repr__(self) -> str:
        """Возвращает строку с названием классов и атрибутами при инициализации экземпляров класса."""
        return f"{self.__class__.__name__}('{self._title}', '{self._url}', '{self._salary_from}','{self._salary_to}')"
