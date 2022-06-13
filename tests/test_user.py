import requests


def test_user_login(user):
    data = {'email': user.email, 'password': '654321'}
    response = requests.post('http://localhost:5000/api/login', json=data)

    assert response.status_code == 200
    assert response.json().get('access_token')


def test_user_registration():
    data = {'email': 'a12@mail.ru', 'password': '123456', 'username': 'Aleks'}
    response = requests.post('http://localhost:5000/api/register', json=data)

    assert response.status_code == 200
    assert response.json().get('access_token')


def test_user_show(user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}'
    response = requests.get(url, headers=get_header_token)

    assert response.status_code == 200
    assert user.username == 'Igor'


def test_user_update(user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}'
    data = {'email': 'a121111@mail.ru', 'username': 'Olga'}
    response = requests.put(url, json=data, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()['username'] == 'Olga'
    assert response.json()['email'] == 'a121111@mail.ru'


def test_user_delete(user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}'
    response = requests.delete(url, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()['message'] == f'User with id {user.id} deleted'
