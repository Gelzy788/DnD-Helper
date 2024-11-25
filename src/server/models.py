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
    refresh_token = db.Column(db.String(256), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }


class Friends(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column(db.BigInteger(), db.ForeignKey(
        'users.id'), nullable=False)
    friend_id = db.Column(
        db.BigInteger(), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Boolean(), default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'friend_id': self.friend_id,
            'user_name': User.query.filter_by(id=self.user_id).first().username,
            'friend_name': User.query.filter_by(id=self.friend_id).first().username,
            'status': self.status
        }


class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), nullable=False)
    class_name = db.Column(db.String(32), nullable=False)
    species = db.Column(db.String(32), nullable=False)
    background = db.Column(db.String(32))
    worldview = db.Column(db.String(64))
    experience = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    character_name = db.Column(db.String(32))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'class_name': self.class_name,
            'species': self.species,
            'background': self.background,
            'worldview': self.worldview,
            'experience': self.experience,
            'level': self.level,
            'character_name': self.character_name
        }


class Groups(db.Model):
    __tablename__ = 'users_groups'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    next_game_date = db.Column(db.Date)
    owner_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), nullable=False)
    plot = db.Column(db.Text())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            # Преобразуем дату в строку
            'next_game_date': self.next_game_date.isoformat() if self.next_game_date else None,
            'owner_id': self.owner_id,
            'plot': self.plot,
        }


class GroupsMembers(db.Model):
    __tablename__ = 'groups_members'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    group_id = db.Column(db.BigInteger, db.ForeignKey(
        'users_groups.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'name': Groups.query.get(self.group_id).to_dict()['name'],
            'username': User.query.get(self.user_id).to_dict()['username']
        }


class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column(db.BigInteger(), db.ForeignKey(
        'users.id'), nullable=False)
    device_id = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(128), nullable=False)
