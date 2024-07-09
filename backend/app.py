import pytest
from flask import Flask, render_template, request
import jinja2
import requests
import psycopg2
import os


app = Flask(__name__, template_folder='/app/frontend')

# Установка соединения с базой данных PostgreSQL
conn = psycopg2.connect(database='vacancies',
                        user='postgres',
                        password='12345',
                        host=os.getenv('DATABASE_HOST', 'localhost'),
                        port='5432')
cur = conn.cursor()

url_cities = f"https://api.hh.ru/areas/113"
response_cities = requests.get(url_cities)


def find_city_id_by_name(city_name):
    data = response_cities.json()

    def search_city_id(city_name, areas):
        for area in areas:
            if area.get('name').lower() == city_name.lower():
                return area.get('id')
            elif area.get('areas'):
                result = search_city_id(city_name, area.get('areas'))
                if result:
                    return result

    areas = data.get('areas', [])
    city_id = search_city_id(city_name, areas)

    return city_id


# Определяем конечную точку для отображения главной страницы
@app.route('/')
def index():
    return render_template("index.html")


# Определяем конечную точку для обработки запроса поиска и сохранения вакансий в базу данных
@app.route('/search', methods=['POST'])
def search():
    features = request.form  # Получаем критерии поиска из формы

    f_spec = str(features.getlist('spec')[0].lower())
    f_area = '&area=' + str(find_city_id_by_name(features.getlist('area')[0]))
    f_education = '&education=' + str(features.getlist('education')[0])
    f_employment = '&employment=' + str(features.getlist('employment')[0])
    f_schedule = '&schedule=' + str(features.getlist('schedule')[0])
    f_salary = '&only_with_salary=true&salary=' + str(features.getlist('salary')[0])
    features_list = [f_area, f_education, f_employment, f_schedule, f_salary]

    def add_feature(feature):
        if 'None' not in feature and feature[-1] != '=':
            return feature
        return ''

    url = f'https://api.hh.ru/vacancies?clusters=true&enable_snippets=true&showClusters=true&per_page=5&text={f_spec}'
    for i in range(len(features_list)):
        url += add_feature(features_list[i])

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Получение информации о вакансиях и сохранение в базу данных
        for vacancy in data.get('items', []):

            title = vacancy.get('name', '')

            requirement = ''
            if vacancy.get('snippet'):
                if vacancy.get('snippet').get('requirement'):
                    requirement = vacancy['snippet']['requirement']

            city = ''
            if vacancy.get('area'):
                city = vacancy['area']['name']

            salary_from = 0
            salary_to = 0
            if vacancy.get('salary'):
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']

            employment = ''
            if vacancy.get('employment'):
                employment = vacancy['employment']['name']

            schedule = ''
            if vacancy.get('schedule'):
                schedule = vacancy['schedule']['name']

            vacancy_url = vacancy['alternate_url']

            # Добавляем информацию в базу данных
            cur.execute(
                "INSERT INTO hhru_table (title, requirement,"
                " city, salary_from, salary_to, employment, schedule, vacancy_url)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (vacancy_url) DO NOTHING",
                (title, requirement, city, salary_from, salary_to, employment, schedule, vacancy_url))

        conn.commit()  # Фиксируем изменения в базе данных

        cur.execute(
            "SELECT title, requirement, city, salary_from, salary_to, employment, schedule, vacancy_url FROM hhru_table")
        rows = cur.fetchall()

        # Создание списка словарей для передачи данных в html-таблицу
        vacancies = []
        for row in rows:
            vacancy = {
                'title': row[0],
                'requirement': row[1],
                'city': row[2],
                'salary_from': row[3],
                'salary_to': row[4],
                'employment': row[5],
                'schedule': row[6],
                'vacancy_url': row[7]
            }
            vacancies.append(vacancy)

        return render_template("result.html", vacancies=vacancies)

    else:
        return 'Error retrieving data from HH.ru API', 500


if __name__ == '__main__':
    app.run(debug=True)
