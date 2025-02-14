from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from PyQt6.uic import loadUi

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardsecretky'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Azizalinegm111@localhost/dnd_helper'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IP_ADDRESS = '185.247.185.193'  # IP адрес сервера
PORT = 5000  # Порт flask сервера
# main_screen = loadUi('ui_files\\main_screen.ui')
# default_screen = loadUi('ui_files\\default_screen.ui')
# login_screen = loadUi('ui_files\\login_screen.ui')
# registration_screen = loadUi('ui_files\\registration_screen.ui')

db = SQLAlchemy(app)
login_manager = LoginManager()
