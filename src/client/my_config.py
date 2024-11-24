# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask import Flask
# from PyQt6.uic import loadUi

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'hardsecretkey'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Azizalinegm111@localhost/dnd_helper'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['UPLOAD_FOLDER'] = 'static/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IP_ADDRESS = '185.247.185.193'  # IP адрес сервера
PORT = 5000  # Порт flask сервера

# try:
#     with open('tokens.txt', 'r') as f:
#         data = f.readlines()
#         access_token = data[0].strip()
#         refresh_token = data[1].strip()
# except Exception as e1:
access_token = ''
refresh_token = ''

# db = SQLAlchemy(app)
# login_manager = LoginManager()
