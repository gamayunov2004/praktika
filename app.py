'''from flask import Flask, render_template, request

import psycopg2

conn = psycopg2.connect(database='cards',
                        user='postgres',
                        password='0000',
                        host='localhost',
                        port='5432')
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    height = request.form['height']
    weight = request.form['weight']
    experience = request.form['gender']
    if :

    else:


    return render_template('result.html', bmi=bmi, img=img, card_title=card_title,
                           text=text, link=link, img2=img2, card_title2=card_title2,
                           text2=text2, link2=link2,explanation=explanation,
                           img3=img3, card_title3=card_title3, text3=text3,
                           link3=link3)

if __name__ == '__main__':
    app.run(debug=True)'''

from flask import Flask, render_template, request, jsonify
import jinja2
import requests
import psycopg2

app = Flask(__name__)

# Установка соединения с базой данных PostgreSQL
conn = psycopg2.connect(database='vacancies',
                        user='postgres',
                        password='0000',
                        host='localhost',
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
    return render_template('index.html')


# Определяем конечную точку для обработки запроса поиска и сохранения вакансий в базу данных
@app.route('/search', methods=['POST'])
def search():
    features = request.form  # Получаем критерии поиска из формы
    # Отправляем запрос к API hh.ru с критериями поиска и получаем данные

    f_spec = str(features.getlist('spec')[0].lower())
    f_area = '&area=' + str(find_city_id_by_name(features.getlist('area')[0]))
    f_education = '&education=' + str(features.getlist('education')[0])
    print(f_education)
    f_employment = '&employment=' + str(features.getlist('employment')[0])
    f_schedule = '&schedule=' + str(features.getlist('schedule')[0])
    f_salary = '&only_with_salary=true&salary=' + str(features.getlist('salary')[0])
    features_list = [f_area, f_education, f_employment, f_schedule, f_salary]
    print(features_list)

    def add_feature(feature):
        if 'None' not in feature and feature[-1] != '=':
            return feature
        return ''

    url = f'https://api.hh.ru/vacancies?clusters=true&enable_snippets=true&showClusters=true&per_page=5&text={f_spec}&area=113'
    for i in range(len(features_list)):
        url += add_feature(features_list[i])
        print(url)


    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Получение информации о вакансиях и сохранение в базу данных
        print(data.get('items'))
        for vacancy in data.get('items', []):
            # Извлекаем необходимую информацию о вакансии

            title = vacancy.get('name', '')
            print('название ' + title)

            requirement = ''
            if vacancy.get('snippet'):
                if vacancy.get('snippet').get('requirement'):
                    requirement = vacancy['snippet']['requirement']
            print('описание ' + requirement)

            city = ''
            if vacancy.get('area'):
                city = vacancy['area']['name']
            print('город ' + city)

            salary_from = 0
            salary_to = 0
            if vacancy.get('salary'):
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']

            print(salary_from, salary_to)

            employment = ''
            if vacancy.get('employment'):
                employment = vacancy['employment']['name']
            print('занятость ' + employment)

            schedule=''
            if vacancy.get('schedule'):
                schedule = vacancy['schedule']['name']
            print('график работы ' + schedule)

            vacancy_url = vacancy['alternate_url']
            print(vacancy_url)

            print('-------------------')

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

        # Создание списка словарей для передачи данных в шаблон
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

        return render_template('result.html', vacancies=vacancies)

    else:
        return 'Error retrieving data from HH.ru API', 500


if __name__ == '__main__':
    app.run()
