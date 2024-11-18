from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardsecretkey'
ACCESS_TOKEN_SECRET_KEY = 'My super-secret key'  # Код для токена
REFRESH_TOKEN_TIME = 30  # Время истечения refresh токена в днях
REFRESH_TOKEN_SECRET_KEY = 'My super-secret key'  # Код для токена

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Gelzy:Azizalinegm111@localhost/DnD_Helper'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\SystemX\\Documents\\server\\static\\profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ACCESS_TOKEN_EXPIRATION_TIME = 15  # Время истечения токена в минутах
REFRESH_TOKEN_EXPIRATION_TIME = 30  # Время истечения refresh токена в днях
# engine = create_engine("mysql+mysqldb://root:pass@192.168.1.13/tasklist")
db = SQLAlchemy(app)
login_manager = LoginManager()
