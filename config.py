import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')
JSON_AS_ASCII = False    # чтобы нормально отображались символы
