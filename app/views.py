from sqlalchemy.exc import DBAPIError
from app import app, db
from flask import jsonify, request, json
from app.models import User, Post
from passlib.hash import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route('/api/register', methods=['POST'])
def register():
    user = User(**json.loads(request.data.decode("Windows-1251")))
    try:
        db.session.add(user)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    token = user.get_token()
    return {'access_token': token}


@app.route('/api/login', methods=['POST'])
def login():
    params = json.loads(request.data.decode("Windows-1251"))
    user = User.query.filter_by(email=params.get('email')).first()
    if not user:
        return {'message': f"No user with email {params.get('email')}"}
    if user:
        if not bcrypt.verify(params.get('password'), user.password):  # сравниваем пароль из запроса с БД
            return {'message': f"Invalid password"}
        else:
            token = user.get_token()
            return {'access_token': token}


@app.route('/api/users/<int:user_id>', methods=['GET'], endpoint='show_user')
@jwt_required()
def show_user(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
    пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    dict_res = user.as_dict()
    list_com, list_post = [], []
    for com in user.comments:
        dict_com = dict()
        dict_com = com.as_dict()
        dict_com['Title of the Post'] = com.article.title  # Название поста, к которому этот комментарий
        dict_com['Username author of the Post'] = com.article.author.username  # Имя автора поста, к которому этот комментарий
        del dict_com['user_id']
        del dict_com['id']
        del dict_com['username']
        list_com.append(dict_com)
    for post in user.posts:
        dict_post = dict()
        dict_post = post.as_dict()
        del dict_post['user_id']
        del dict_post['id']
        list_post.append(dict_post)
    dict_res['posts'] = list_post
    dict_res['comments'] = list_com

    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>', methods=['PUT'], endpoint='update_user')
@jwt_required()
def update_user(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
        пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    new_task = json.loads(request.data.decode("Windows-1251"))
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    for key, value in new_task.items():
        setattr(user, key, value)     # устанавливаем по ключу значение в user
    db.session.commit()
    dict_res = user.as_dict()   # выводим измененного юзера

    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>', methods=['DELETE'], endpoint='delete_user')
@jwt_required()
def delete_user(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
        пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    try:
        db.session.delete(user)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return {'message': f'User with id {user_id} deleted'}


@app.route('/api/users/<int:user_id>/posts', methods=['GET'], endpoint='user_posts')
@jwt_required()
def user_posts(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
        пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    list_posts = list()
    for post in user.posts:
        dict_post = post.as_dict()
        del dict_post['user_id']
        del dict_post['id']
        list_com = list()
        for com in post.comments:
            dict_com = dict()
            dict_com = com.as_dict()
            del dict_com['post_id']
            del dict_com['user_id']
            del dict_com['id']
            list_com.append(dict_com)
        dict_post['comments'] = list_com
        list_posts.append(dict_post)
    if not list_posts:
        return {'message': f'User with id {user_id} has not any posts'}

    return jsonify(list_posts)


@app.route('/api/users/<int:user_id>/posts', methods=['POST'], endpoint='user_add_post')
@jwt_required()
def user_add_post(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
            пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    new_post = Post(user_id=user.id, **json.loads(request.data.decode("Windows-1251")))
    try:
        db.session.add(new_post)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()
    finally:
        dict_res = new_post.as_dict()

    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>/posts/<int:post_id>', methods=['PUT'], endpoint='user_update_post')
@jwt_required()
def user_update_post(user_id, post_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
            пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter(Post.id == post_id, User.id == user_id_token, User.id == user_id).first()
    new_task = json.loads(request.data.decode("Windows-1251"))
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400
    for key, value in new_task.items():
        setattr(post, key, value)
    db.session.commit()
    dict_res = post.as_dict()

    return jsonify(dict_res)


@app.route('/api/users/<int:user_id>/posts/<int:post_id>', methods=['DELETE'], endpoint='user_delete_post')
@jwt_required()
def user_delete_post(user_id, post_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
                пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter(Post.id == post_id, User.id == user_id_token, User.id == user_id).first()
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400
    try:
        db.session.delete(post)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return {'message': f'Post with id {post_id} deleted'}


@app.route('/api/users/<int:user_id>/comments', methods=['GET'], endpoint='user_comments')
@jwt_required()
def user_comments(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
                пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    list_comments = list()
    for comment in user.comments:
        dict_comments = comment.as_dict()
        dict_comments['Title of the Post'] = comment.article.title  # Название поста, к которому этот комментарий
        dict_comments[
            'Username author of the Post'] = comment.article.author.username    # Имя автора поста, к которому этот комментарий
        del dict_comments['post_id']
        del dict_comments['user_id']
        del dict_comments['id']
        list_comments.append(dict_comments)
    if not list_comments:
        return {'message': f'User with id {user_id} has not any comment'}

    return jsonify(list_comments)





