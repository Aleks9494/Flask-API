from sqlalchemy.exc import DBAPIError
from app import app, db
from app.models import User, Post, Comment
from passlib.hash import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas import PostSchema, UserSchema, AuthSchema, CommentSchema, UpdateUserSchema, UpdatePostSchema
from flask_apispec import marshal_with, use_kwargs
from flask import jsonify
from flask_apispec import MethodResource


# @app.route('/api/user', methods=['GET'])
# @marshal_with(UserSchema)
# def show():
#     user = User.query.all()
#     return user

# Регистрация
@app.route('/api/register', methods=['POST'])
@use_kwargs(UserSchema)  # декоратор для десериализации входящих параметров, аналог schema.load
@marshal_with(AuthSchema)  # декоратор для сериализации объекта например БД, аналог schema.dump
def register(**kwargs):
    user = User(**kwargs)
    try:
        db.session.add(user)
        db.session.commit()
        token = user.get_token()
        return {'access_token': token}
    except DBAPIError:
        db.session.rollback()
        return {'message': f"Email {kwargs.get('email')} is busy "}


# авторизация
@app.route('/api/login', methods=['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))  # декоратор для десериализации входящих параметров
@marshal_with(AuthSchema)
def login(**kwargs):
    user = User.query.filter_by(email=kwargs.get('email')).first()
    if not user:
        return {'message': f"No user with email {kwargs.get('email')}"}
        # raise Exception(f"No user with email {kwargs.get('email')}")
    if user:
        if not bcrypt.verify(kwargs.get('password'), user.password):  # сравниваем пароль из запроса с БД
            return {'message': f"Invalid password"}
        else:
            token = user.get_token()
            return {'access_token': token}


# Просмотр инфомарции о себе
@app.route('/api/users/<int:user_id>', methods=['GET'], endpoint='show_user')
@jwt_required()
@marshal_with(UserSchema)
def show_user(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
    пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400

    return user   # возвращаем при помощи @marshal_with(UserSchema) сериализованный в json объект user


# Изменение информации о себе
@app.route('/api/users/<int:user_id>', methods=['PUT'], endpoint='update_user')
@jwt_required()
@marshal_with(UserSchema)
@use_kwargs(UpdateUserSchema)   # убрал обязательные поля, чтобы можно было менять что-то одно
def update_user(user_id, **kwargs):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
        пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    """аргументы kwargs - это те данные, котоыре приходят в post запросе, use_kwargs нужен для 
        десериализации данных json из запроса  """
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    try:
        for key, value in kwargs.items():
            setattr(user, key, value)  # устанавливаем по ключу значение в user
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return user


# Удаление своего пользователя
@app.route('/api/users/<int:user_id>', methods=['DELETE'], endpoint='delete_user')
@jwt_required()
@marshal_with(UserSchema)
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


# посмотреть все посты на сайте
class ShowPosts(MethodResource):
    @jwt_required()
    # @marshal_with(PostSchema(many=True))  # декоратор для сериализации данных,  список json объектов
    def get(self, user_id):  # при MethodResourse(Pluggable Views для API названия методов get, post, put, delete)
        user_id_token = get_jwt_identity()
        if user_id_token != user_id:
            return {'message': f'Access denied, this id not yours = {user_id}'}, 400
        posts = Post.query.all()
        if not posts:
            return {'message': 'There are not any posts'}
        schema = PostSchema(many=True)
        # c декоратором #@marshal_with(PostSchema(many=True)) возвращается
        # "title": "<built-in method title of str object at 0x0000025FAD58ECB0>"
        return jsonify(schema.dump(posts))


# Просмотр любого поста
@app.route('/api/users/<int:user_id>/allposts/<int:post_id>', methods=['GET'], endpoint='show_post')
@jwt_required()
@marshal_with(PostSchema)
def show_post(user_id, post_id):
    user_id_token = get_jwt_identity()
    if user_id_token != user_id:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400

    return post


# Комментирование не своего поста
@app.route('/api/users/<int:user_id>/allposts/<int:post_id>', methods=['POST'], endpoint='comment_post')
@jwt_required()
@marshal_with(PostSchema)
@use_kwargs(CommentSchema)
def comment_post(user_id, post_id, **kwargs):
    user_id_token = get_jwt_identity()
    if user_id_token != user_id:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400
    elif post.user_id == user_id_token:
        return {'message': 'This is your post!!'}, 400
    new_comment = Comment(user_id=user_id, post_id=post_id, **kwargs)
    try:
        db.session.add(new_comment)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return post


# Просмотр своих постов
@app.route('/api/users/<int:user_id>/posts', methods=['GET'], endpoint='user_posts')
@jwt_required()
# @marshal_with(PostSchema(many=True))       # декоратор для сериализации данных,  список json объектов
def user_posts(user_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
        пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    posts = Post.query.filter(Post.user_id == user_id_token, Post.user_id == user_id).all()
    schema = PostSchema(many=True)
    # c декоратором #@marshal_with(PostSchema(many=True)) возвращается
    # "title": "<built-in method title of str object at 0x0000025FAD58ECB0>"
    if not posts:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400

    return jsonify(schema.dump(posts))
    # return posts


# Добавление своего поста
@app.route('/api/users/<int:user_id>/posts', methods=['POST'], endpoint='user_add_post')
@jwt_required()
@use_kwargs(PostSchema)  # декоратор для десериализации входящих параметров
@marshal_with(PostSchema)  # декоратор для сериализации данных,  один json объект
def user_add_post(user_id, **kwargs):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
            пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    """аргументы kwargs - это те данные, котоыре приходят в post запросе"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    new_post = Post(user_id=user.id, **kwargs)
    try:
        db.session.add(new_post)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()
        return {'message': f'Title {kwargs.get("title")} already exist'}

    return new_post


# Редактирование своего поста
@app.route('/api/users/<int:user_id>/posts/<int:post_id>', methods=['PUT'], endpoint='user_update_post')
@jwt_required()
@use_kwargs(UpdatePostSchema)  # декоратор для десериализации входящих параметров
@marshal_with(PostSchema)  # декоратор для сериализации данных,  один json объект
def user_update_post(user_id, post_id, **kwargs):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
            пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    """аргументы kwargs - это те данные, котоыре приходят в post запросе"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter(Post.id == post_id, Post.user_id == user_id_token, Post.user_id == user_id).first()
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400
    try:
        for key, value in kwargs.items():
            setattr(post, key, value)  # устанавливаем по ключу значение в user
        db.session.commit()
    except DBAPIError:
        db.session.rollback()
        return {'message': f'Title {kwargs.get("title")} already exist'}

    return post


# Удаление своего поста
@app.route('/api/users/<int:user_id>/posts/<int:post_id>', methods=['DELETE'], endpoint='user_delete_post')
@jwt_required()
@marshal_with(PostSchema)
def user_delete_post(user_id, post_id):
    """Получаем id из пользователя, прошедшего идентификацию для того, чтобы другие идентифицированые
                пользователи не смогли ввести свой id в строку браузера и увидеть данные по id,который они ввели"""
    user_id_token = get_jwt_identity()
    user = User.query.filter(User.id == user_id_token, User.id == user_id).first()
    if not user:
        return {'message': f'Access denied, this id not yours = {user_id}'}, 400
    post = Post.query.filter(Post.id == post_id, Post.user_id == user_id_token, Post.user_id == user_id).first()
    if not post:
        return {'message': f'No post with id = {post_id}'}, 400
    try:
        db.session.delete(post)
        db.session.commit()
    except DBAPIError:
        db.session.rollback()

    return {'message': f'Post with id {post_id} deleted'}


@app.errorhandler(422)  # обработка исключений схем marshmallow (422), если обязательного поля нет в данных в запросе
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request'])
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


app.add_url_rule('/api/users/<int:user_id>/allposts', view_func=ShowPosts.as_view('show_posts'), methods=['GET'])
