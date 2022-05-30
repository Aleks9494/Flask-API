from flask import Flask, jsonify, request

app = Flask(__name__)

client = app.test_client()

app.config['JSON_AS_ASCII'] = False         # чтобы нормально отображались символы

lists = [
        {
            'id': 1,
            'title': 'Number 1',
            'description': 'Test #1'
        },
        {
            'id': 2,
            'title': 'Number 2',
            'description': 'Test #2'
        }
        ]


@app.route('/api/lists', methods=['GET'])
def get_lists():
    return jsonify(lists)


@app.route('/api/lists', methods=['POST'])
def add_list():
    new_task = request.json
    lists.append(new_task)
    return jsonify(lists)


@app.route('/api/lists/<int:list_id>', methods=['PUT'])
def update_list(list_id):
    elem = next((x for x in lists if x['id'] == list_id), None)
    new_task = request.json
    if not elem:
        return {'message': f'No tasks with id = {list_id}'}, 400
    elem.update(new_task)
    return jsonify(elem)


@app.route('/api/lists/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    elem = next((x for x in enumerate(lists) if x[1]['id'] == list_id), None)
    """ Enumerate возращает кортеж (индекс элемента в lists, сам элемент (словарь))
        Next возращает элемент итератора, или None (если условие не выполнено)
        x[1] - сам элемент в кортеже"""
    if not elem:
        return {'message': f'No tasks with id = {list_id}'}, 400
    lists.pop(elem[0])                          # так как elem - кортеж
    return {'message': f'Task with id {list_id} deleted'}


if __name__ == '__main__':
    app.run(debug=True)
