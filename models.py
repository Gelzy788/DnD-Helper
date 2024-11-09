from flask_login import UserMixin
from config import db
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)
    profile_picture = db.Column(db.String(128), nullable=True)
