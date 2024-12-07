from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e3f0f3eae8e4f8f2e0fdeff6fcfdefeaf2e6f9'
ACCESS_TOKEN_SECRET_KEY = 'edeff8f3fb5cf7e2f4e0f0f8e7e0f3ecf2f9f2f1eef8e0f3eae8f8f0e0f3e8'  # Код для токена
REFRESH_TOKEN_TIME = 30  # Время истечения refresh токена в днях
REFRESH_TOKEN_SECRET_KEY = 'e5f132e332f033f0e3ece2efeef6f1e8f9f2323933f038e8eae9e0eee4fce6f3eae1ebe7f6f1f2f8f0e8f8f0f2e2fbfce1fdf4f6e2f1f2fcf6e2'  # Код для токена
#  Путь к бд: /var/lib/mysql/
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Gelzy:Azizalinegm111@localhost/DnD_Helper'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Путь к папке для хранения фото профиля
app.config['UPLOAD_FOLDER'] = 'static/questionnaire_images'
# Разрешенные расширения файлов для фоток профиля
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ACCESS_TOKEN_EXPIRATION_TIME = 1  # Время истечения токена в минутах
REFRESH_TOKEN_EXPIRATION_TIME = 30  # Время истечения refresh токена в днях
# Подключение зависимостей
db = SQLAlchemy(app)
login_manager = LoginManager()
