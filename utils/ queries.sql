-- Создание таблицы employers
CREATE TABLE IF NOT EXISTS employers (
    employers_id SERIAL,
    company_name VARCHAR,

    CONSTRAINT pk_employers_employers_id PRIMARY KEY (employers_id)
)

-- Создание таблицы db_vacancies
CREATE TABLE IF NOT EXISTS db_vacancies (
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
)

--Выборка компаний и количества вакансий
SELECT employers.company_name, COUNT(vacancies_id)
FROM employers INNER JOIN db_vacancies USING (employers_id)
GROUP BY employers.company_name
ORDER BY employers.company_name DESC

--Выборка списка вакансий с указанием компании, названии вакансии, зарплаты и ссылки
SELECT company_name AS Название_компании, vacancy_name AS Вакансия,
    (CASE
        WHEN salary_from = 0 AND salary_to = 0 THEN 0
        WHEN salary_from = 0 AND salary_to <> 0 THEN salary_to
        WHEN salary_from <> 0 AND salary_to = 0 THEN salary_from
        ELSE (salary_from + salary_to) / 2
    END) AS Зарплата, url AS Ссылка
FROM employers INNER JOIN db_vacancies USING (employers_id)
ORDER BY 3 DESC

--Выборка средней зарплаты по вакансиям
SELECT ROUND(AVG(CASE
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

--Выборка списка вакансий, у которых зарплата выше средней по вакансиям
WITH get_avg_salary(avg_salary)
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