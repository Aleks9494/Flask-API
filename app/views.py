from sqlalchemy.exc import DBAPIError
from app import app, db
from flask import jsonify, request
from app.models import User


@app.route('/api/users', methods=['GET'])
def get_users():
    result = User.query.all()
    list_json = []
    for res in result:
        dict_res = res.as_dict()    # переводим объект класса User в словарь методом класса User
        dict_com, dict_post = {}, {}
        for com in res.comments:
            dict_com = com.as_dict()
        for post in res.posts:
            dict_post = post.as_dict()
        dict_res['posts'] = dict_post
        dict_res['comments'] = dict_com
        list_json.append(dict_res)
    return jsonify(list_json)


@app.route('/api/users', methods=['POST'])
def add_user():
    new_task = User(**request.json)  # распаковывваем словарь,создаем объект класса User
    try:
        db.session.add(new_task)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()
    finally:
        dict_res = new_task.as_dict()
    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    new_task = request.json
    if not user:
        return {'message': f'No tasks with id = {user_id}'}, 400
    for key, value in new_task.items():
        setattr (user, key, value)     #  устанавливаем по ключу значение в user
    db.session.commit()
    dict_res = user.as_dict()   # выводим измененного юзера
    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return {'message': f'No tasks with id = {user_id}'}, 400
    try:
        db.session.delete(user)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return {'message': f'User with id {user_id} deleted'}

