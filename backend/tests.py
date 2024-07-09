import pytest
from app import find_city_id_by_name, app


def test_find_city_id_by_name():
    assert find_city_id_by_name('Москва') == '1'
    assert find_city_id_by_name('Новосибирск') == '4'
    assert find_city_id_by_name('Нижний Новгород') == '66'


def test_index_route():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert 'Парсер вакансий hh.ru' in response.get_data(as_text=True)


def test_search_route():
    with app.test_client() as client:
        data = {
            'spec': 'python',
            'area': 'Москва',
            'salary': '100000',
            'education': 'higher',
            'employment': 'full',
            'schedule': 'fullDay'
        }
        response = client.post('/search', data=data)
        assert response.status_code == 200
        assert 'Результат поиска вакансий' in response.get_data(as_text=True)


if __name__ == '__main__':
    test_find_city_id_by_name()
    test_index_route()
    test_search_route()
    print('All tests passed!')