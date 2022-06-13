import requests


def test_all_posts(add_post, user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}' + '/allposts'
    response = requests.get(url, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Test'


def test_user_posts(add_post, user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}' + '/posts'
    response = requests.get(url, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Test'


def test_user_add_post(user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}' + '/posts'
    data = {'title': 'Test #2', 'content': 'Test by Pytest #2!!'}
    response = requests.post(url, json=data, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()['title'] == 'Test #2'
    assert response.json()['content'] == 'Test by Pytest #2!!'


def test_user_update_post(add_post, user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}' + '/posts/' + f'{add_post.id}'
    data = {'title': 'Test Update', 'content': 'Test by Pytest updated!!'}
    response = requests.put(url, json=data, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()['title'] == 'Test Update'
    assert response.json()['content'] == 'Test by Pytest updated!!'


def test_user_comment(add_post, user_2, get_header_token_2):
    url = 'http://localhost:5000/api/users/' + f'{user_2.id}' + '/allposts/' + f'{add_post.id}'
    data = {'username': 'Maksim', 'body': 'Maks comments Post of Igor!!'}
    response = requests.post(url, json=data, headers=get_header_token_2)

    assert response.status_code == 200
    assert response.json()['comments'][0]['body'] == 'Maks comments Post of Igor!!'


def test_user_delete_post(add_post, user, get_header_token):
    url = 'http://localhost:5000/api/users/' + f'{user.id}' + '/posts/' + f'{add_post.id}'
    response = requests.delete(url, headers=get_header_token)

    assert response.status_code == 200
    assert response.json()['message'] == f'Post with id {add_post.id} deleted'
