from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

client = app.test_client()

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,  db)    # потом в терминале flask db init для создания папки migrations

from app import views, models
