from app import client
from flask import json
from app.models import User

def test_get():

    result = client.get('api/users')
    print (result.json)
    assert result.status_code == 200
    assert len(result.json) == len(User.query.all())


def test_post():
    data = {
        'id': 5,
        'username': 'Petya',
        'email': 'e@mail.ru',
        'user_status': 'Fifth to Go!!!!!'
    }
    result = client.post('api/users', json=data)

    assert result.status_code == 200
    assert result.json['username'] == data['username']
    assert result.json['username'] == User.query.filter_by(id=data['id']).first().username


def test_put():
    data = {
        'user_status': 'First to Go!!!!!!',
    }
    result = client.put('api/users/1', json=data)

    assert result.status_code == 200
    assert result.json['user_status'] == data['user_status']
    assert result.json['user_status'] == User.query.get(1).user_status


def test_delete():

    result = client.delete('api/users/5')

    assert result.status_code == 200
    assert result.json['message'] == 'User with id 5 deleted'
