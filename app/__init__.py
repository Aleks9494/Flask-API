from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

app = Flask(__name__)

client = app.test_client()

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,  db)    # потом в терминале flask db init для создания папки migrations
jwt = JWTManager(app)       # аутентификация
docs = FlaskApiSpec()     # документации для swagger
docs.init_app(app)

from app.views import *
docs.register(register)
docs.register(login)
docs.register(show_user)
docs.register(update_user)
docs.register(delete_user)
docs.register(show_all_posts)
docs.register(show_post)
docs.register(comment_post)
docs.register(user_posts)
docs.register(user_add_post)
docs.register(user_update_post)
docs.register(user_delete_post)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='MyBlog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'})

from app import views, models
