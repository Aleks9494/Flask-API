from datetime import datetime, timedelta
from app import db
from flask_jwt_extended import create_access_token
from passlib.hash import bcrypt


class User (db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=True, nullable=False)
    user_status = db.Column(db.String(40), nullable=True, default='Лучший пользователь проекта')

    comments = db.relationship('Comment', backref='user_comments', lazy=True, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, **kwargs):  # переопределяем инициализацию объекта для генерации хэша пароля
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))
        self.user_status = kwargs.get('user_status')

    def as_dict(self):              # объект класса в словарь для json
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'password'}

    def get_token(self, expire_time=24):        # создание токена для авторизации
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)
        return token


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    comments = db.relationship('Comment', backref='article', lazy=True, cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    body = db.Column(db.Text(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.now)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

