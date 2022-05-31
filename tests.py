from run import client


def test_get():
    result = client.get('api/lists')

    assert result.status_code == 200
    assert len(result.json) == 2
    assert result.json[0]['id'] == 1


def test_post():
    data = {
        'id': 3,
        'title': 'Number 3',
        'description': 'Test #3'
    }
    result = client.post('api/lists', json=data)   # в result все данные из списка словарей (из функции add_list() в return весь список)

    assert result.status_code == 200
    assert len(result.json) == 3
    assert result.json[2]['id'] == 3


def test_put():
    data = {
        'title': 'Number 222222',
        'description': 'Test #3 update by test'
    }
    result = client.put('api/lists/3', json=data)   # в result только 1 запись из списка словарей (из функции update_list в return измененная запись)

    assert result.status_code == 200
    assert result.json['title'] == 'Number 222222'
    assert result.json['description'] == 'Test #3 update by test'


def test_delete():

    result = client.delete('api/lists/3')   # в result сообщение ((из функции del_list в return message)

    assert result.status_code == 200
    assert result.json['message'] == 'Task with id 3 deleted'
