from app import client
from app.models import User
import requests
from flask import json

def test_get():
    # user_json = user.as_dict()
    # result = requests.post('http://localhost:5000/api/login', json=user_json)
    data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post('http://localhost:5000/api/login', data=json.dumps(data), headers=headers)
    assert r.status_code == 200


