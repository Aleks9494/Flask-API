import pytest
import requests
from app import app, db
from app.models import User, Post


@pytest.fixture(scope='session')
def testapp():         # создание приложения и БД
    _app = app
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db. drop_all()


@pytest.fixture(scope='session')
def user(testapp):
    user = User(username='Igor', email='a23@mail.ru', password='654321')
    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture(scope='session')
def user_2(testapp):
    user_2 = User(username='Maksim', email='bam@mail.ru', password='password')
    db.session.add(user_2)
    db.session.commit()

    return user_2


@pytest.fixture(scope='session')
def get_header_token(user):    # в заголовки добавляется токен для роутов с jwt_required
    data = {'email': user.email, 'password': '654321'}
    response = requests.post('http://localhost:5000/api/login', json=data)
    r = response.json()['access_token']
    headers = {'Authorization': f'Bearer {r}'}

    return headers


@pytest.fixture(scope='session')
def get_header_token_2(user_2):    # в заголовки добавляется токен для роутов с jwt_required
    data = {'email': user_2.email, 'password': 'password'}
    response = requests.post('http://localhost:5000/api/login', json=data)
    r = response.json()['access_token']
    headers = {'Authorization': f'Bearer {r}'}

    return headers


@pytest.fixture(scope='session')
def add_post(user):
    post = Post(title='Test', content='Test by Pytest!!', user_id=user.id)
    db.session.add(post)
    db.session.commit()

    return post

