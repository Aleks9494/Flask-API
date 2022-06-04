from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)

client = app.test_client()

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,  db)    # потом в терминале flask db init для создания папки migrations
jwt = JWTManager(app)

from app import views, models
